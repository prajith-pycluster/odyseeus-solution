"""
Interactive chat in the terminal.
Usage:
    python chat_cli.py
Commands:
    /account - Display mock account details
    /reset   - Reset conversation memory
    /help    - Show help commands
    quit     - Exit the chat session
"""
import sys

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from chatbot import SupportBot, ACCOUNT, BACKEND, MAIN_MODEL

bot = SupportBot()
print("=" * 60)
print(f"ConnectX Telecom Support Assistant")
print(f"Active Backend: {BACKEND} | Model: {MAIN_MODEL}")
print(f"Customer Context: {ACCOUNT['customer_name']} ({ACCOUNT['plan']})")
print("Type your message below. Type 'quit' or 'exit' to end.")
print("Type '/reset' to clear conversation memory, '/account' for details.")
print("=" * 60 + "\n")

while True:
    try:
        msg = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        break

    if not msg:
        continue

    if msg.lower() in ("quit", "exit"):
        print("Bot: Thank you for contacting ConnectX Support. Have a wonderful day!")
        break

    if msg.lower() == "/reset":
        bot.reset()
        print("Bot: [Conversation history cleared. How can I help you today?]\n")
        continue

    if msg.lower() == "/account":
        print("\n--- Current Account Details ---")
        for k, v in ACCOUNT.items():
            print(f"  {k}: {v}")
        print("-------------------------------\n")
        continue

    if msg.lower() == "/help":
        print("\nCommands: 'quit', '/reset', '/account', '/help'")
        print("Try asking: 'What plan am I on?', 'Is there a faster option?', 'When is my bill due?'\n")
        continue

    reply = bot.chat(msg)
    print(f"Bot: {reply}\n")
