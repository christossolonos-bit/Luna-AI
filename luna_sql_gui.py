# luna_sql_gui.py
"""
Enhanced Luna GUI with Discord and Twitch Memory Management
Shows user statistics and memory data from SQL databases
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
from discord_user_tracker_sql import discord_user_tracker_sql, get_discord_user_stats_sql, get_all_discord_users_sql
from twitch_user_tracker_sql import twitch_user_tracker_sql, get_twitch_user_stats_sql, get_all_twitch_users_sql

LUNA_ENDPOINT = "http://127.0.0.1:8000/luna"

class LunaSQLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Luna AI - Discord & Twitch Memory Manager 💖")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e2f")
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background="#1e1e2f", borderwidth=0)
        style.configure('TNotebook.Tab', background="#2e2e3e", foreground="#ffffff", padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', '#ff6699')])
        
        # Create tabs
        self.create_chat_tab()
        self.create_discord_tab()
        self.create_twitch_tab()
        self.create_stats_tab()
        
        # Auto-refresh stats every 30 seconds
        self.auto_refresh()
    
    def create_chat_tab(self):
        """Create chat interface tab"""
        chat_frame = tk.Frame(self.notebook, bg="#1e1e2f")
        self.notebook.add(chat_frame, text="💬 Chat")
        
        # Chat box
        self.chat_box = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            font=("Segoe UI", 11), 
            bg="#2e2e3e", 
            fg="#f2f2f2",
            insertbackground="#ffffff"
        )
        self.chat_box.tag_config("user", foreground="#a1cfff")
        self.chat_box.tag_config("luna", foreground="#ffb6c1")
        self.chat_box.tag_config("system", foreground="#90ee90")
        self.chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Entry frame
        entry_frame = tk.Frame(chat_frame, bg="#1e1e2f")
        entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.entry = tk.Entry(
            entry_frame, 
            font=("Segoe UI", 12), 
            bg="#3e3e50", 
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_message())
        
        send_button = tk.Button(
            entry_frame, 
            text="Send 💌", 
            command=self.send_message, 
            bg="#ff6699", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )
        send_button.pack(side=tk.RIGHT)
    
    def create_discord_tab(self):
        """Create Discord users tab"""
        discord_frame = tk.Frame(self.notebook, bg="#1e1e2f")
        self.notebook.add(discord_frame, text="💬 Discord Users")
        
        # Title and refresh button
        header_frame = tk.Frame(discord_frame, bg="#1e1e2f")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame, 
            text="Discord User Memory", 
            font=("Segoe UI", 16, "bold"),
            bg="#1e1e2f", 
            fg="#a1cfff"
        ).pack(side=tk.LEFT)
        
        tk.Button(
            header_frame, 
            text="🔄 Refresh", 
            command=self.refresh_discord_users,
            bg="#5865f2", 
            fg="white", 
            font=("Segoe UI", 10),
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Stats frame
        stats_frame = tk.Frame(discord_frame, bg="#2e2e3e")
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.discord_stats_label = tk.Label(
            stats_frame,
            text="Loading stats...",
            font=("Segoe UI", 11),
            bg="#2e2e3e",
            fg="#ffffff",
            anchor="w",
            justify="left"
        )
        self.discord_stats_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Users table
        table_frame = tk.Frame(discord_frame, bg="#1e1e2f")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("Username", "Discord ID", "First Seen", "Last Seen", "Total Messages")
        self.discord_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.discord_tree.yview)
        
        # Configure columns
        for col in columns:
            self.discord_tree.heading(col, text=col)
            self.discord_tree.column(col, width=150, anchor="center")
        
        self.discord_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure colors
        style = ttk.Style()
        style.configure("Treeview", background="#2e2e3e", foreground="#ffffff", fieldbackground="#2e2e3e")
        style.map('Treeview', background=[('selected', '#5865f2')])
        
        # Load initial data
        self.refresh_discord_users()
    
    def create_twitch_tab(self):
        """Create Twitch users tab"""
        twitch_frame = tk.Frame(self.notebook, bg="#1e1e2f")
        self.notebook.add(twitch_frame, text="🎮 Twitch Users")
        
        # Title and refresh button
        header_frame = tk.Frame(twitch_frame, bg="#1e1e2f")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame, 
            text="Twitch User Memory", 
            font=("Segoe UI", 16, "bold"),
            bg="#1e1e2f", 
            fg="#9146ff"
        ).pack(side=tk.LEFT)
        
        tk.Button(
            header_frame, 
            text="🔄 Refresh", 
            command=self.refresh_twitch_users,
            bg="#9146ff", 
            fg="white", 
            font=("Segoe UI", 10),
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Stats frame
        stats_frame = tk.Frame(twitch_frame, bg="#2e2e3e")
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.twitch_stats_label = tk.Label(
            stats_frame,
            text="Loading stats...",
            font=("Segoe UI", 11),
            bg="#2e2e3e",
            fg="#ffffff",
            anchor="w",
            justify="left"
        )
        self.twitch_stats_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Users table
        table_frame = tk.Frame(twitch_frame, bg="#1e1e2f")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("Username", "Badges", "First Seen", "Last Seen", "Total Messages")
        self.twitch_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.twitch_tree.yview)
        
        # Configure columns
        for col in columns:
            self.twitch_tree.heading(col, text=col)
            self.twitch_tree.column(col, width=150, anchor="center")
        
        self.twitch_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load initial data
        self.refresh_twitch_users()
    
    def create_stats_tab(self):
        """Create statistics overview tab"""
        stats_frame = tk.Frame(self.notebook, bg="#1e1e2f")
        self.notebook.add(stats_frame, text="📊 Statistics")
        
        # Title
        tk.Label(
            stats_frame, 
            text="Luna Memory Statistics", 
            font=("Segoe UI", 18, "bold"),
            bg="#1e1e2f", 
            fg="#ffb6c1"
        ).pack(pady=20)
        
        # Stats display
        self.stats_display = scrolledtext.ScrolledText(
            stats_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#2e2e3e",
            fg="#ffffff",
            height=30
        )
        self.stats_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Refresh button
        tk.Button(
            stats_frame, 
            text="🔄 Refresh Statistics", 
            command=self.refresh_all_stats,
            bg="#ff6699", 
            fg="white", 
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
            pady=10
        ).pack(pady=(0, 20))
        
        # Load initial stats
        self.refresh_all_stats()
    
    def send_message(self):
        """Send message to Luna"""
        user_message = self.entry.get()
        if not user_message.strip():
            return
        
        self.chat_box.insert(tk.END, f"You: {user_message}\n", "user")
        
        try:
            response = requests.post(LUNA_ENDPOINT, json={"message": user_message}, timeout=30)
            luna_reply = response.json().get("response", "[No reply]")
        except Exception as e:
            luna_reply = f"[Error: {e}]"
        
        self.chat_box.insert(tk.END, f"Luna: {luna_reply}\n\n", "luna")
        self.chat_box.see(tk.END)
        self.entry.delete(0, tk.END)
    
    def refresh_discord_users(self):
        """Refresh Discord users table"""
        # Clear existing data
        for item in self.discord_tree.get_children():
            self.discord_tree.delete(item)
        
        # Get stats
        stats = get_discord_user_stats_sql()
        self.discord_stats_label.config(
            text=f"📊 Total Users: {stats['total_users']} | "
                 f"Active (24h): {stats['active_users']} | "
                 f"Total Messages: {stats['total_messages']} | "
                 f"Recent Messages: {stats['recent_messages']}"
        )
        
        # Get users
        users = get_all_discord_users_sql()
        for user in users:
            self.discord_tree.insert("", tk.END, values=(
                user['username'],
                user['discord_id'],
                user['first_seen'],
                user['last_seen'],
                user['total_messages']
            ))
    
    def refresh_twitch_users(self):
        """Refresh Twitch users table"""
        # Clear existing data
        for item in self.twitch_tree.get_children():
            self.twitch_tree.delete(item)
        
        # Get stats
        stats = get_twitch_user_stats_sql()
        self.twitch_stats_label.config(
            text=f"📊 Total Users: {stats['total_users']} | "
                 f"Active (24h): {stats['active_users']} | "
                 f"Total Messages: {stats['total_messages']} | "
                 f"Subscribers: {stats['subscribers']}"
        )
        
        # Get users
        users = get_all_twitch_users_sql()
        for user in users:
            self.twitch_tree.insert("", tk.END, values=(
                user['username'],
                user['badges'],
                user['first_seen'],
                user['last_seen'],
                user['total_messages']
            ))
    
    def refresh_all_stats(self):
        """Refresh all statistics"""
        self.stats_display.delete(1.0, tk.END)
        
        # Discord stats
        discord_stats = get_discord_user_stats_sql()
        self.stats_display.insert(tk.END, "=" * 60 + "\n")
        self.stats_display.insert(tk.END, "DISCORD STATISTICS\n")
        self.stats_display.insert(tk.END, "=" * 60 + "\n\n")
        self.stats_display.insert(tk.END, f"Total Users:          {discord_stats['total_users']}\n")
        self.stats_display.insert(tk.END, f"Active Users (24h):   {discord_stats['active_users']}\n")
        self.stats_display.insert(tk.END, f"Total Messages:       {discord_stats['total_messages']}\n")
        self.stats_display.insert(tk.END, f"Recent Messages:      {discord_stats['recent_messages']}\n")
        
        # Twitch stats
        twitch_stats = get_twitch_user_stats_sql()
        self.stats_display.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.stats_display.insert(tk.END, "TWITCH STATISTICS\n")
        self.stats_display.insert(tk.END, "=" * 60 + "\n\n")
        self.stats_display.insert(tk.END, f"Total Users:          {twitch_stats['total_users']}\n")
        self.stats_display.insert(tk.END, f"Active Users (24h):   {twitch_stats['active_users']}\n")
        self.stats_display.insert(tk.END, f"Total Messages:       {twitch_stats['total_messages']}\n")
        self.stats_display.insert(tk.END, f"Subscribers:          {twitch_stats['subscribers']}\n")
        
        # Combined stats
        total_users = discord_stats['total_users'] + twitch_stats['total_users']
        total_messages = discord_stats['total_messages'] + twitch_stats['total_messages']
        
        self.stats_display.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.stats_display.insert(tk.END, "COMBINED STATISTICS\n")
        self.stats_display.insert(tk.END, "=" * 60 + "\n\n")
        self.stats_display.insert(tk.END, f"Total Users:          {total_users}\n")
        self.stats_display.insert(tk.END, f"Total Messages:       {total_messages}\n")
        self.stats_display.insert(tk.END, f"Active Communities:   2 (Discord + Twitch)\n")
        
        self.stats_display.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.stats_display.insert(tk.END, "✅ Luna's memory system is tracking all interactions!\n")
        self.stats_display.insert(tk.END, "=" * 60 + "\n")
    
    def auto_refresh(self):
        """Auto-refresh data every 30 seconds"""
        self.refresh_discord_users()
        self.refresh_twitch_users()
        self.refresh_all_stats()
        self.root.after(30000, self.auto_refresh)  # 30 seconds

def main():
    root = tk.Tk()
    app = LunaSQLGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
