import socket
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import simpledialog
import threading
from tkinter import filedialog  # For photo selection

# Client setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    print("Trying to connect...")
    client.connect(('localhost', 55556))
except Exception as e:
    messagebox.showerror("Connection Error", f"Failed to connect: {e}")
    exit()

# GUI setup
window = tk.Tk()
window.title("Mini WhatsApp")
window.geometry("500x600")  # Increased size for photo

# Nickname input
nickname = tk.simpledialog.askstring("Nickname", "Please choose a nickname", parent=window)
if nickname:
    try:
        client.send(nickname.encode('utf-8'))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send nickname: {e}")
        window.destroy()
else:
    messagebox.showerror("Error", "Nickname required")
    window.destroy()

# Chat display
chat_display = scrolledtext.ScrolledText(window, state='disabled')
chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Message input and Send button frame
input_frame = tk.Frame(window)
input_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

message_input = tk.Entry(input_frame, width=30)
message_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
message_input.focus()

def send_message(event=None):  # Allow event for Enter key
    message = message_input.get().strip()
    if message:
        if message.lower() == '/quit':
            client.send(f'{nickname}: {message}'.encode('utf-8'))
            client.close()
            window.destroy()
        else:
            try:
                full_message = f'{nickname}: {message}'
                client.send(full_message.encode('utf-8'))
                message_input.delete(0, tk.END)
                # Display sent message locally only once
                chat_display.config(state='normal')
                chat_display.insert(tk.END, full_message + '\n')
                chat_display.config(state='disabled')
                chat_display.see(tk.END)
            except Exception as e:
                messagebox.showerror("Send Error", f"Failed to send: {e}")

send_button = tk.Button(input_frame, text="Send", command=send_message)
send_button.grid(row=0, column=1, padx=5, pady=5)

# Photo send button
def send_photo():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
    if file_path:
        try:
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()
                # Send as text (base64 for simplicity, limited to 1024 bytes for now)
                import base64
                encoded_data = base64.b64encode(image_data[:1024]).decode('utf-8')  # Limit to 1024 bytes
                full_message = f'{nickname}: [PHOTO] {encoded_data}'
                client.send(full_message.encode('utf-8'))
                chat_display.config(state='normal')
                chat_display.insert(tk.END, f'{nickname}: [PHOTO SENT]\n')
                chat_display.config(state='disabled')
                chat_display.see(tk.END)
        except Exception as e:
            messagebox.showerror("Photo Error", f"Failed to send photo: {e}")

photo_button = tk.Button(window, text="Send Photo", command=send_photo)
photo_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

# Bind Enter key to send_message
window.bind('<Return>', send_message)

# Receive messages (skip self-sent)
last_sent = ""
def receive_messages():
    global last_sent
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message != last_sent:  # Skip if it's the last sent message
                chat_display.config(state='normal')
                if "[PHOTO]" in message:
                    chat_display.insert(tk.END, f"{message.split(':')[0]}: [PHOTO RECEIVED]\n")
                else:
                    chat_display.insert(tk.END, message + '\n')
                chat_display.config(state='disabled')
                chat_display.see(tk.END)
            last_sent = message
        except Exception as e:
            print(f"Receive error: {e}")
            break

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Make window resizable and adjust grid
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
input_frame.grid_columnconfigure(0, weight=1)

window.mainloop()