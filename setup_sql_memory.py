# setup_sql_memory.py
"""
Quick Setup Script for Luna's SQL Memory System
Automates the setup and migration process
"""

import os
import sys

def print_header(text):
    """Print a fancy header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def check_files():
    """Check if required files exist"""
    print_header("Checking Required Files")
    
    required_files = [
        'discord_user_tracker_sql.py',
        'twitch_user_tracker_sql.py',
        'luna_sql_gui.py',
        'migrate_json_to_sql.py'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[MISSING] {file}")
            missing.append(file)
    
    if missing:
        print(f"\n[WARNING] Missing {len(missing)} required file(s)!")
        return False
    
    print("\n[OK] All required files present!")
    return True

def check_json_data():
    """Check for existing JSON data"""
    print_header("Checking for Existing Data")
    
    has_discord = os.path.exists('discord_users.json')
    has_twitch = os.path.exists('twitch_users.json')
    
    if has_discord:
        print("[OK] Found discord_users.json")
    else:
        print("[INFO] No discord_users.json found (will start fresh)")
    
    if has_twitch:
        print("[OK] Found twitch_users.json")
    else:
        print("[INFO] No twitch_users.json found (will start fresh)")
    
    return has_discord or has_twitch

def run_migration():
    """Run the migration script"""
    print_header("Running Migration")
    
    try:
        import migrate_json_to_sql
        migrate_json_to_sql.main()
        return True
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        return False

def test_databases():
    """Test if databases were created successfully"""
    print_header("Testing Databases")
    
    try:
        from discord_user_tracker_sql import get_discord_user_stats_sql
        from twitch_user_tracker_sql import get_twitch_user_stats_sql
        
        discord_stats = get_discord_user_stats_sql()
        twitch_stats = get_twitch_user_stats_sql()
        
        print("[OK] Discord database working!")
        print(f"   - Total users: {discord_stats['total_users']}")
        print(f"   - Total messages: {discord_stats['total_messages']}")
        
        print("\n[OK] Twitch database working!")
        print(f"   - Total users: {twitch_stats['total_users']}")
        print(f"   - Total messages: {twitch_stats['total_messages']}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print_header("Setup Complete!")
    
    print("Next Steps:\n")
    print("1. Launch the GUI to view user data:")
    print("   python luna_sql_gui.py\n")
    
    print("2. Run Luna with SQL memory enabled:")
    print("   python main.py\n")
    
    print("3. View the documentation:")
    print("   Read SQL_MEMORY_SYSTEM_README.md\n")
    
    print("4. Check your databases:")
    print("   - luna_discord_users.db")
    print("   - luna_twitch_users.db\n")
    
    print("=" * 70)
    print("  Luna's SQL Memory System is ready!")
    print("=" * 70)

def main():
    """Main setup function"""
    print("""
    ==================================================================
    
              Luna SQL Memory System Setup
    
         Automated setup for Discord & Twitch memory tracking
    
    ==================================================================
    """)
    
    # Step 1: Check files
    if not check_files():
        print("\n[ERROR] Setup cannot continue without required files.")
        sys.exit(1)
    
    # Step 2: Check for existing data
    has_data = check_json_data()
    
    # Step 3: Run migration (or initialize fresh databases)
    if has_data:
        print("\n[INFO] Existing data found. Starting migration...")
        input("Press ENTER to continue...")
        if not run_migration():
            print("\n[ERROR] Setup failed during migration.")
            sys.exit(1)
    else:
        print("\n[INFO] No existing data. Initializing fresh databases...")
        try:
            from discord_user_tracker_sql import discord_user_tracker_sql
            from twitch_user_tracker_sql import twitch_user_tracker_sql
            print("[OK] Fresh databases initialized!")
        except Exception as e:
            print(f"[ERROR] Failed to initialize databases: {e}")
            sys.exit(1)
    
    # Step 4: Test databases
    if not test_databases():
        print("\n[WARNING] Databases created but tests failed. Check errors above.")
    
    # Step 5: Show next steps
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
