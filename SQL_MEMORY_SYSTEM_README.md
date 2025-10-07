# Luna SQL Memory System 🧠💾

## Overview

Luna's memory system has been upgraded from JSON files to SQL databases for better performance, reliability, and scalability. This system tracks all Discord and Twitch user interactions in SQLite databases.

## Features ✨

### Discord Memory System
- **User Tracking**: Tracks Discord usernames, IDs, first seen, last seen, and message counts
- **Message History**: Stores recent messages with timestamps
- **Channel Activity**: Tracks which channels users are active in
- **Guild Support**: Supports multiple Discord servers (guilds)

### Twitch Memory System
- **User Tracking**: Tracks Twitch usernames, IDs, and activity
- **Subscriber Detection**: Identifies subscribers and moderators
- **Topic Extraction**: Automatically detects user interests (gaming, tech, music, etc.)
- **Channel Activity**: Tracks activity across different Twitch channels

### GUI Interface
- **Real-time Stats**: View Discord and Twitch statistics
- **User Management**: Browse all users with their activity data
- **Chat Interface**: Communicate with Luna directly from the GUI
- **Auto-refresh**: Updates every 30 seconds automatically

## File Structure 📁

```
Luna Waifu/
├── discord_user_tracker_sql.py      # Discord SQL tracker
├── twitch_user_tracker_sql.py       # Twitch SQL tracker
├── luna_sql_gui.py                  # Enhanced GUI with memory management
├── migrate_json_to_sql.py           # Migration script (JSON → SQL)
├── luna_discord_users.db            # Discord SQLite database
├── luna_twitch_users.db             # Twitch SQLite database
├── discord_users.json.backup        # JSON backup (after migration)
└── twitch_users.json.backup         # JSON backup (after migration)
```

## Installation & Setup 🚀

### Step 1: Migrate Existing Data

If you have existing JSON data, migrate it to SQL:

```bash
python migrate_json_to_sql.py
```

This will:
- Create SQL databases (`luna_discord_users.db` and `luna_twitch_users.db`)
- Migrate all existing user data from JSON to SQL
- Backup original JSON files (`.json.backup`)

### Step 2: Launch the GUI

```bash
python luna_sql_gui.py
```

The GUI provides:
- **Chat Tab**: Direct chat with Luna
- **Discord Users Tab**: View all Discord users and their stats
- **Twitch Users Tab**: View all Twitch users and their stats
- **Statistics Tab**: Combined statistics across platforms

### Step 3: Run Luna with SQL Memory

The main system automatically uses SQL-based trackers:

```bash
python main.py
```

Luna will now:
- Track Discord messages in SQL
- Track Twitch messages in SQL
- Remember all user interactions permanently

## Database Schema 📊

### Discord Users Database

**discord_users** table:
- `id`: Primary key
- `username`: Discord username
- `discord_id`: Discord user ID
- `first_seen`: First interaction timestamp
- `last_seen`: Last interaction timestamp
- `total_messages`: Total message count

**discord_messages** table:
- `id`: Primary key
- `user_id`: Foreign key to discord_users
- `message`: Message content
- `channel`: Channel name
- `guild`: Server name
- `timestamp`: Message timestamp

**discord_user_channels** table:
- Tracks which channels users are active in
- Message counts per channel

### Twitch Users Database

**twitch_users** table:
- `id`: Primary key
- `username`: Twitch username
- `twitch_id`: Twitch user ID
- `first_seen`: First interaction timestamp
- `last_seen`: Last interaction timestamp
- `total_messages`: Total message count
- `is_subscriber`: Subscriber status
- `is_moderator`: Moderator status

**twitch_messages** table:
- `id`: Primary key
- `user_id`: Foreign key to twitch_users
- `message`: Message content
- `channel`: Channel name
- `timestamp`: Message timestamp

**twitch_user_topics** table:
- Tracks user interests and topics
- Mention counts per topic

## API Usage 💻

### Discord Tracker

```python
from discord_user_tracker_sql import (
    track_discord_message_sql,
    get_discord_user_context_sql,
    get_discord_chat_context_sql,
    get_all_discord_users_sql
)

# Track a message
track_discord_message_sql(
    username="User123",
    message="Hello Luna!",
    channel="general",
    guild="My Server",
    discord_id="123456789"
)

# Get user context
context = get_discord_user_context_sql("User123")
print(context)

# Get all users
users = get_all_discord_users_sql()
for user in users:
    print(user['username'], user['total_messages'])
```

### Twitch Tracker

```python
from twitch_user_tracker_sql import (
    track_twitch_message_sql,
    get_twitch_user_context_sql,
    get_twitch_chat_context_sql,
    get_all_twitch_users_sql
)

# Track a message
track_twitch_message_sql(
    username="viewer123",
    message="Great stream!",
    channel="solonaras",
    is_subscriber=True,
    is_moderator=False
)

# Get user context
context = get_twitch_user_context_sql("viewer123")
print(context)

# Get all users
users = get_all_twitch_users_sql()
for user in users:
    print(user['username'], user['badges'], user['total_messages'])
```

## Benefits of SQL vs JSON 🎯

### Performance
- **Faster Queries**: SQL indexes enable instant lookups
- **Efficient Filtering**: Find active users, top contributors, etc.
- **Scalability**: Handles thousands of users effortlessly

### Reliability
- **Data Integrity**: Foreign keys prevent orphaned data
- **Atomic Operations**: No partial writes or corruption
- **Concurrent Access**: Multiple processes can read simultaneously

### Features
- **Complex Queries**: Join tables, aggregate stats, filter by criteria
- **Analytics**: Track trends, activity patterns, user growth
- **Relationships**: Link users, messages, channels seamlessly

## Maintenance 🔧

### Cleanup Old Data

Remove messages older than 30 days:

```python
from discord_user_tracker_sql import discord_user_tracker_sql
from twitch_user_tracker_sql import twitch_user_tracker_sql

# Clean Discord messages
discord_user_tracker_sql.cleanup_old_data(days=30)

# Clean Twitch messages
twitch_user_tracker_sql.cleanup_old_data(days=30)
```

### Backup Databases

```bash
# Backup Discord database
copy luna_discord_users.db luna_discord_users_backup.db

# Backup Twitch database
copy luna_twitch_users.db luna_twitch_users_backup.db
```

### View Database

Use SQLite browser or command line:

```bash
sqlite3 luna_discord_users.db
.tables
SELECT * FROM discord_users LIMIT 10;
```

## Troubleshooting 🛠️

### Migration Issues

**Problem**: Migration script fails
**Solution**: Check that JSON files exist and are valid
```bash
python -c "import json; json.load(open('discord_users.json'))"
```

### Import Errors

**Problem**: Module not found errors
**Solution**: Ensure all files are in the same directory
```bash
# Check files exist
ls discord_user_tracker_sql.py
ls twitch_user_tracker_sql.py
```

### Database Locked

**Problem**: "Database is locked" error
**Solution**: Close GUI or other connections before migration
```bash
# Kill processes using database
taskkill /f /im python.exe
```

## Advanced Features 🚀

### Custom Queries

Access databases directly for custom analytics:

```python
import sqlite3

conn = sqlite3.connect('luna_discord_users.db')
cursor = conn.cursor()

# Find most active users
cursor.execute('''
    SELECT username, total_messages
    FROM discord_users
    ORDER BY total_messages DESC
    LIMIT 10
''')

top_users = cursor.fetchall()
for username, count in top_users:
    print(f"{username}: {count} messages")

conn.close()
```

### Integration with Other Systems

```python
# Export to JSON for external tools
import json
import sqlite3

conn = sqlite3.connect('luna_discord_users.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM discord_users')
users = [dict(zip([col[0] for col in cursor.description], row)) 
         for row in cursor.fetchall()]

with open('discord_export.json', 'w') as f:
    json.dump(users, f, indent=2)
```

## Future Enhancements 🔮

- [ ] PostgreSQL support for distributed deployments
- [ ] Advanced analytics dashboard
- [ ] User preference learning system
- [ ] Cross-platform user linking (Discord ↔ Twitch)
- [ ] Sentiment analysis on messages
- [ ] Automated insights and reports

## Support 💖

For issues or questions:
1. Check this README
2. Review the migration logs
3. Inspect database files with SQLite browser
4. Check console output for error messages

---

**Created for Luna AI** 🌙✨  
*Remember: With great memory comes great responsibility!*
