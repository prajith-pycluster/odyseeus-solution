"""
Runs the practical-test stages from the specification.
Usage:
    python run_tests.py
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

from chatbot import ask_once, SupportBot, BACKEND, MAIN_MODEL


def show(q, a):
    print(f"\nUSER: {q}\nBOT : {a}")


print("=" * 60)
print(f"ConnectX Support Chatbot Tests [Backend: {BACKEND} | Model: {MAIN_MODEL}]")
print("=" * 60)

print("\n" + "=" * 60)
print("STAGE 1 - Core Assistant (Stateless single turn)")
print("=" * 60)
q = "What is my current plan and how much do I pay each month?"
show(q, ask_once(q))

print("\n" + "=" * 60)
print("STAGE 2 - Conversation Memory (Multi-turn context)")
print("=" * 60)
bot = SupportBot()
for q in [
    "What plan am I on?",
    "Is there a faster option?",
    "How much more would that cost?",
]:
    show(q, bot.chat(q))

print("\n" + "=" * 60)
print("STAGE 3 - Out-of-Scope Handling (Scope Router + Dual-layer Guardrail)")
print("=" * 60)
bot = SupportBot()  # Fresh session
for q in [
    "How does ConnectX compare to Airtel's pricing?",
    "Can you help me write an email to my landlord?",
    "What's the weather like in Mumbai today?",
    "When is my next bill due?",  # In-scope control test: must NOT be refused
]:
    show(q, bot.chat(q))

print("\n" + "=" * 60)
print("All stage tests completed successfully!")
print("=" * 60)
