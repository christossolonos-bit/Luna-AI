# migrate_json_to_sql.py
"""
Migration Script: JSON to SQL Database
Migrates Discord and Twitch user data from JSON files to SQL databases
"""

import json
import os
from discord_user_tracker_sql import discord_user_tracker_sql
from twitch_user_tracker_sql import twitch_user_tracker_sql

def migrate_discord_users():
    """Migrate Discord users from JSON to SQL"""
    json_file = "discord_users.json"
    
    if not os.path.exists(json_file):
        print(f"[WARNING] {json_file} not found. Skipping Discord migration.")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        print(f"[INFO] Migrating {len(users_data)} Discord users to SQL...")
        
        migrated = 0
        for username, user_info in users_data.items():
            try:
                # Get user data with defaults for missing fields
                first_seen = user_info.get('first_seen', user_info.get('last_seen', 0))
                last_seen = user_info.get('last_seen', first_seen)
                total_messages = user_info.get('total_messages', user_info.get('message_count', 0))
                
                # Get channels (may be list or set from JSON)
                channels = user_info.get('channels', [])
                if isinstance(channels, dict):
                    channels = list(channels.keys())
                
                # Get guilds
                guilds = user_info.get('guilds', [])
                if isinstance(guilds, dict):
                    guilds = list(guilds.keys())
                
                # Get recent messages
                recent_messages = user_info.get('recent_messages', [])
                
                # Track each recent message
                for msg_data in recent_messages:
                    if isinstance(msg_data, dict):
                        message = msg_data.get('message', '')
                        channel = msg_data.get('channel', 'unknown')
                        guild = msg_data.get('guild', 'Unknown')
                        timestamp = msg_data.get('timestamp', last_seen)
                        
                        # Temporarily modify the timestamp to match the message
                        import sqlite3
                        import time
                        
                        conn = sqlite3.connect(discord_user_tracker_sql.db_path)
                        cursor = conn.cursor()
                        
                        # Get or create user
                        cursor.execute('SELECT id FROM discord_users WHERE username = ?', (username,))
                        result = cursor.fetchone()
                        
                        if result:
                            user_id = result[0]
                        else:
                            cursor.execute('''
                                INSERT INTO discord_users (username, first_seen, last_seen, total_messages)
                                VALUES (?, ?, ?, 0)
                            ''', (username, first_seen, last_seen))
                            user_id = cursor.lastrowid
                        
                        # Insert message
                        cursor.execute('''
                            INSERT INTO discord_messages (user_id, message, channel, guild, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (user_id, message, channel, guild, timestamp))
                        
                        # Update channel activity
                        cursor.execute('''
                            INSERT INTO discord_user_channels (user_id, channel, guild, first_seen, last_seen, message_count)
                            VALUES (?, ?, ?, ?, ?, 1)
                            ON CONFLICT(user_id, channel, guild) DO UPDATE SET
                                last_seen = MAX(last_seen, excluded.last_seen),
                                message_count = message_count + 1
                        ''', (user_id, channel, guild, timestamp, timestamp))
                        
                        conn.commit()
                        conn.close()
                
                # Update final user stats
                import sqlite3
                conn = sqlite3.connect(discord_user_tracker_sql.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE discord_users 
                    SET total_messages = ?, last_seen = ?
                    WHERE username = ?
                ''', (total_messages, last_seen, username))
                conn.commit()
                conn.close()
                
                migrated += 1
                
            except Exception as e:
                print(f"[WARNING] Error migrating Discord user {username}: {e}")
        
        print(f"[OK] Successfully migrated {migrated} Discord users to SQL!")
        
        # Backup original JSON
        backup_file = json_file + ".backup"
        import shutil
        shutil.copy(json_file, backup_file)
        print(f"[INFO] Original JSON backed up to {backup_file}")
        
    except Exception as e:
        print(f"[ERROR] Error during Discord migration: {e}")

def migrate_twitch_users():
    """Migrate Twitch users from JSON to SQL"""
    json_file = "twitch_users.json"
    
    if not os.path.exists(json_file):
        print(f"[WARNING] {json_file} not found. Skipping Twitch migration.")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        print(f"[INFO] Migrating {len(users_data)} Twitch users to SQL...")
        
        migrated = 0
        for username, user_info in users_data.items():
            try:
                # Get user data with defaults for missing fields
                first_seen = user_info.get('first_seen', user_info.get('last_seen', 0))
                last_seen = user_info.get('last_seen', first_seen)
                total_messages = user_info.get('interaction_count', user_info.get('message_count', 0))
                
                # Get channels (may be list or set from JSON)
                channels = user_info.get('channels', [])
                if isinstance(channels, dict):
                    channels = list(channels.keys())
                
                # Get recent messages
                recent_messages = user_info.get('recent_messages', [])
                
                # Track each recent message
                for msg_data in recent_messages:
                    if isinstance(msg_data, dict):
                        message = msg_data.get('message', '')
                        channel = msg_data.get('channel', 'default')
                        timestamp = msg_data.get('timestamp', last_seen)
                        
                        import sqlite3
                        import time
                        
                        conn = sqlite3.connect(twitch_user_tracker_sql.db_path)
                        cursor = conn.cursor()
                        
                        # Get or create user
                        cursor.execute('SELECT id FROM twitch_users WHERE username = ?', (username,))
                        result = cursor.fetchone()
                        
                        if result:
                            user_id = result[0]
                        else:
                            cursor.execute('''
                                INSERT INTO twitch_users (username, first_seen, last_seen, total_messages)
                                VALUES (?, ?, ?, 0)
                            ''', (username, first_seen, last_seen))
                            user_id = cursor.lastrowid
                        
                        # Insert message
                        cursor.execute('''
                            INSERT INTO twitch_messages (user_id, message, channel, timestamp)
                            VALUES (?, ?, ?, ?)
                        ''', (user_id, message, channel, timestamp))
                        
                        # Update channel activity
                        cursor.execute('''
                            INSERT INTO twitch_user_channels (user_id, channel, first_seen, last_seen, message_count)
                            VALUES (?, ?, ?, ?, 1)
                            ON CONFLICT(user_id, channel) DO UPDATE SET
                                last_seen = MAX(last_seen, excluded.last_seen),
                                message_count = message_count + 1
                        ''', (user_id, channel, timestamp, timestamp))
                        
                        # Extract topics
                        twitch_user_tracker_sql._extract_topics(user_id, message, timestamp, cursor)
                        
                        conn.commit()
                        conn.close()
                
                # Update final user stats
                import sqlite3
                conn = sqlite3.connect(twitch_user_tracker_sql.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE twitch_users 
                    SET total_messages = ?, last_seen = ?
                    WHERE username = ?
                ''', (total_messages, last_seen, username))
                conn.commit()
                conn.close()
                
                migrated += 1
                
            except Exception as e:
                print(f"[WARNING] Error migrating Twitch user {username}: {e}")
        
        print(f"[OK] Successfully migrated {migrated} Twitch users to SQL!")
        
        # Backup original JSON
        backup_file = json_file + ".backup"
        import shutil
        shutil.copy(json_file, backup_file)
        print(f"[INFO] Original JSON backed up to {backup_file}")
        
    except Exception as e:
        print(f"[ERROR] Error during Twitch migration: {e}")

def main():
    """Run migration for both Discord and Twitch"""
    print("[INFO] Starting migration from JSON to SQL...")
    print("=" * 60)
    
    migrate_discord_users()
    print()
    migrate_twitch_users()
    
    print("=" * 60)
    print("[OK] Migration complete!")
    print("\nSummary:")
    
    # Show stats
    discord_stats = discord_user_tracker_sql.get_user_stats()
    twitch_stats = twitch_user_tracker_sql.get_user_stats()
    
    print(f"\nDiscord:")
    print(f"  - Total users: {discord_stats['total_users']}")
    print(f"  - Total messages: {discord_stats['total_messages']}")
    print(f"  - Active users (24h): {discord_stats['active_users']}")
    
    print(f"\nTwitch:")
    print(f"  - Total users: {twitch_stats['total_users']}")
    print(f"  - Total messages: {twitch_stats['total_messages']}")
    print(f"  - Active users (24h): {twitch_stats['active_users']}")
    print(f"  - Subscribers: {twitch_stats['subscribers']}")

if __name__ == "__main__":
    main()
