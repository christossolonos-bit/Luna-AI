"""
Luna Agents GUI — Real-time view of what Luna's memory agents are doing.
Run alongside Luna to monitor ExtractAgent, StoreAgent, RecallAgent, OrganizeAgent, PersistAgent.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, scrolledtext, font as tkfont
import threading
import time


def create_agents_gui():
    """Create and return the Agents GUI window."""
    from luna_agents import AgentLogger

    root = tk.Tk()
    root.title("Luna Agents — Memory & Recall")
    root.geometry("700x450")
    root.minsize(500, 300)

    # Style
    style = ttk.Style()
    style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
    style.configure("Status.TLabel", font=("Consolas", 9))

    main = ttk.Frame(root, padding=10)
    main.pack(fill=tk.BOTH, expand=True)

    # Header
    header = ttk.Frame(main)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Agent activity", style="Header.TLabel").pack(side=tk.LEFT)
    ttk.Separator(header, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

    # Agent legend
    legend = ttk.Frame(main)
    legend.pack(fill=tk.X, pady=(0, 5))
    ttk.Label(legend, text="Extract | Store | Recall | Organize | Persist").pack(side=tk.LEFT)
    ttk.Label(legend, text="▶ start  ✓ ok  ○ skip  ✗ error", foreground="gray").pack(side=tk.RIGHT)

    # Log area
    log_frame = ttk.Frame(main)
    log_frame.pack(fill=tk.BOTH, expand=True)
    log_text = scrolledtext.ScrolledText(
        log_frame,
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg="#1e1e1e",
        fg="#d4d4d4",
        insertbackground="#d4d4d4",
        state=tk.DISABLED,
        height=20,
    )
    log_text.pack(fill=tk.BOTH, expand=True)
    log_text.tag_configure("ok", foreground="#4ec9b0")
    log_text.tag_configure("error", foreground="#f48771")
    log_text.tag_configure("skip", foreground="#808080")
    log_text.tag_configure("start", foreground="#dcdcaa")

    def tag_for_status(status: str) -> str:
        return {"ok": "ok", "error": "error", "skip": "skip", "start": "start"}.get(status, "")

    def refresh_log():
        logger = AgentLogger.get()
        lines = logger.get_all_lines(80)
        log_text.config(state=tk.NORMAL)
        log_text.delete(1.0, tk.END)
        events = logger.get_recent(80)
        for e in events:
            line = e.to_line() + "\n"
            log_text.insert(tk.END, line, tag_for_status(e.status))
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)

    def clear_log():
        AgentLogger.get().clear()
        refresh_log()

    # Buttons
    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill=tk.X, pady=(5, 0))
    ttk.Button(btn_frame, text="Refresh", command=refresh_log).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(btn_frame, text="Clear", command=clear_log).pack(side=tk.LEFT)

    def poll():
        while root.winfo_exists():
            try:
                root.after(0, refresh_log)
            except tk.TclError:
                break
            time.sleep(2)

    poll_thread = threading.Thread(target=poll, daemon=True)
    poll_thread.start()

    # Initial load
    refresh_log()

    return root


if __name__ == "__main__":
    root = create_agents_gui()
    root.mainloop()
