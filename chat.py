from pychatgpt import Chat, Options

options = Options()

# Track conversation
options.track = True

# Use a proxy
options.proxies = 'http://localhost:8080'

# Optionally, you can pass a file path to save the conversation
# They're created if they don't exist
options.chat_log = "chat_log.txt"
options.id_log = "id_log.txt"

# Create a Chat object
chat = Chat(email="email", password="password", options=options)
answer = chat.ask("How are you?")
print(answer)