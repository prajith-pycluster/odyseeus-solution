"""Offline logic check using a fake client (no API key / internet needed)."""
import sys
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from types import SimpleNamespace
import chatbot
from chatbot import SupportBot


class FakeClient:
    def __init__(self):
        self.calls = []
        self.messages = self

    def create(self, **kw):
        self.calls.append({**kw, "messages": list(kw["messages"])})
        sys_prompt = kw.get("system", "")
        if "classifier" in sys_prompt:
            text = kw["messages"][0]["content"].split("Latest message:")[-1].lower()
            label = ("COMPETITOR" if "airtel" in text else
                     "PERSONAL" if "landlord" in text else
                     "UNRELATED" if "weather" in text else "IN_SCOPE")
        elif "Summarise" in sys_prompt:
            label = "summary text"
        else:
            label = f"reply#{len(kw['messages'])}"
        return SimpleNamespace(content=[SimpleNamespace(text=label)])


fc = FakeClient()
bot = SupportBot(client=fc)
for q in ["What plan am I on?", "Is there a faster option?", "How much more?"]:
    bot.chat(q)
main_calls = [c for c in fc.calls if "customer support assistant" in c.get("system", "")]
assert [len(c["messages"]) for c in main_calls] == [1, 3, 5], "history not passed"
assert "Priya" in main_calls[0]["system"] and "₹1,399" in main_calls[0]["system"]

for q, key in [("Compare with Airtel", "other providers"),
               ("email to my landlord", "outside what I can help"),
               ("weather in Mumbai", "outside my area")]:
    assert key in bot.chat(q), q

long_bot = SupportBot(client=FakeClient(), max_messages=6, keep_recent=2)
for i in range(10):
    long_bot.chat(f"question {i}")
assert len(long_bot.history) <= 6 and long_bot.summary
assert long_bot.history[0]["role"] == "user"
print("All offline checks passed")
