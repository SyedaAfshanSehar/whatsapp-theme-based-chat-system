import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
names = []

# Ask server name
root = tk.Tk()
root.withdraw()
server_name = simpledialog.askstring("Server", "Enter server name:")

# GUI
root = tk.Tk()
root.title(server_name)
root.geometry("420x600")
root.config(bg="#ECE5DD")

chat_frame = tk.Frame(root, bg="#ECE5DD")
chat_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(chat_frame, bg="#ECE5DD")
scrollbar = tk.Scrollbar(chat_frame, command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#ECE5DD")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

bottom_frame = tk.Frame(root, bg="#ECE5DD")
bottom_frame.pack(fill=tk.X)

msg_entry = tk.Entry(bottom_frame, font=("Arial", 12))
msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

def add_message(msg, side="left"):
    time = datetime.now().strftime("%H:%M")

    bubble = tk.Label(
        scrollable_frame,
        text=f"{msg}\n{time}",
        bg="#DCF8C6" if side == "right" else "#FFFFFF",
        wraplength=250,
        justify="left",
        anchor="e" if side == "right" else "w",
        padx=10,
        pady=5
    )

    bubble.pack(anchor="e" if side == "right" else "w", pady=5, padx=10)

def broadcast(message):
    for client in clients:
        try:
            client.sendall(message.encode())
        except:
            pass

def send_message():
    msg = msg_entry.get().strip()
    if not msg:
        return

    message = f"{server_name}: {msg}"
    broadcast(message)
    add_message(message, "right")

    msg_entry.delete(0, tk.END)

tk.Button(bottom_frame, text="Send", command=send_message, bg="#25D366", fg="white").pack(side=tk.RIGHT, padx=5)

root.bind("<Return>", lambda e: send_message())

def handle(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg:
                broadcast(msg)
                add_message(msg, "left")
        except:
            break

def receive():
    while True:
        client, addr = server.accept()
        client.send("NAME".encode())
        name = client.recv(1024).decode()

        clients.append(client)
        names.append(name)

        join_msg = f"{name} joined 🟢"
        broadcast(join_msg)
        add_message(join_msg)

        threading.Thread(target=handle, args=(client,), daemon=True).start()

threading.Thread(target=receive, daemon=True).start()
root.mainloop()
