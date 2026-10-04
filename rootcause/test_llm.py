import ollama

resp = ollama.chat(
    model="gemma3:4b",
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)
print(resp["message"]["content"])
