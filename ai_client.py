import socket
import threading
import time

# AI Client setup
ai_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ai_client.connect(('localhost', 55556))

# Send AI nickname
ai_client.send('AI_Bot'.encode('utf-8'))
print("AI_Bot connected!")

# Receive and respond
def receive_and_respond():
    while True:
        try:
            message = ai_client.recv(1024).decode('utf-8')
            print(f"Received: {message}")
            if "hi" in message.lower():
                time.sleep(1)  # Simulate thinking
                ai_client.send('AI_Bot: Hello! How can I help?'.encode('utf-8'))
            elif any(word in message.lower() for word in ["bye", "/quit"]):
                ai_client.send('AI_Bot: Goodbye!'.encode('utf-8'))
                ai_client.close()
                break
        except Exception as e:
            print(f"AI error: {e}")
            break

receive_thread = threading.Thread(target=receive_and_respond)
receive_thread.start()

# Keep alive
while receive_thread.is_alive():
    time.sleep(1)