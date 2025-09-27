import tkinter as tk
import requests
from tkinter import scrolledtext

LUNA_ENDPOINT = "http://127.0.0.1:8000/luna"

# 💜 Send user message to Luna's API
def send_message():
    user_message = entry.get()
    if not user_message.strip():
        return
    chat_box.insert(tk.END, f"You: {user_message}\n", "user")

    try:
        response = requests.post(LUNA_ENDPOINT, json={"message": user_message})
        luna_reply = response.json().get("response", "[No reply]")
    except Exception as e:
        luna_reply = f"[Error: {e}]"

    chat_box.insert(tk.END, f"Luna: {luna_reply}\n", "luna")
    chat_box.see(tk.END)
    entry.delete(0, tk.END)

# 🪞 GUI setup
root = tk.Tk()
root.title("Chat with Luna 💖")
root.geometry("600x400")
root.configure(bg="#1e1e2f")

chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Segoe UI", 11), bg="#2e2e3e", fg="#f2f2f2")
chat_box.tag_config("user", foreground="#a1cfff")
chat_box.tag_config("luna", foreground="#ffb6c1")
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

entry_frame = tk.Frame(root, bg="#1e1e2f")
entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

entry = tk.Entry(entry_frame, font=("Segoe UI", 12), bg="#3e3e50", fg="#ffffff")
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(entry_frame, text="Send 💌", command=send_message, bg="#ff6699", fg="white", font=("Segoe UI", 10, "bold"))
send_button.pack(side=tk.RIGHT)

root.mainloop()
