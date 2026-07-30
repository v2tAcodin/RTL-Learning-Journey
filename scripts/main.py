from gemini_client import ask_gemini
from telegram_sender import send_message
from prompt_builder import build_prompt

prompt = build_prompt()

print("Generating...")

text = ask_gemini(prompt)

print(text)

send_message(text)

print("Done.")