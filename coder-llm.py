import gradio as gr
import ollama
import json
import os

# File to store conversation history
HISTORY_FILE = "conversation_history.json"

# Load conversation history from file
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as file:
        conversation_history = json.load(file)
else:
    conversation_history = []

def save_conversation_history():
    with open(HISTORY_FILE, "w") as file:
        json.dump(conversation_history, file)

def chat_with_ollama(prompt, model="qwen2.5-coder:3b"):
    global conversation_history
    conversation_history.append({"role": "user", "content": prompt})

    response = ollama.chat(model=model, messages=conversation_history)
    message = response["message"]["content"]

    conversation_history.append({"role": "assistant", "content": message})

    save_conversation_history()

    return format_response(conversation_history)

def format_response(history):
    """Formats messages with syntax highlighting for code responses."""
    formatted_text = ""
    
    for msg in history:
        if msg["role"] == "user":
            formatted_text += f"<div style='border: 1px solid #ccc; padding: 10px; margin: 20px 0; border-radius: 10px; background-color: #52525b; color: white;'><strong>You:</strong> {msg['content']}</div>\n\n"
        else:
            # If response contains code, format it properly
            if "```" in msg["content"]:
                formatted_text += f"<div style='border: 1px solid #ccc; padding: 10px; margin: 20px 0; border-radius: 10px; background-color: #52525b; color: white;'><strong>Ollama:</strong>\n{msg['content']}</div>\n\n"
            else:
                formatted_text += f"<div style='border: 1px solid #ccc; padding: 10px; margin: 20px 0; border-radius: 10px; background-color: #52525b; color: white;'><strong>Ollama:</strong> {msg['content']}</div>\n\n"

    return formatted_text.strip()

# Gradio UI
with gr.Blocks(css=".chat-container { display: flex; flex-direction: column; height: 100vh; } .chat-output { flex: 1; overflow-y: auto; } .chat-input { display: flex; } .chat-input > * { flex: 1; } .chat-input button { flex: 0; }") as app:
    gr.Markdown("## Qwen Chatbot")
    with gr.Column(elem_id="chat-container"):
        output = gr.Markdown(format_response(conversation_history), label="Conversation History", elem_id="chat-output")  # Supports rich text & code blocks
        with gr.Column(elem_id="chat-input"):
            user_input = gr.Textbox(label="Your Message", placeholder="Type your question here...", lines=2, show_label=False)
            btn = gr.Button("Send", elem_id="submit_btn")

    def submit_message(prompt):
        response = chat_with_ollama(prompt)
        return response, ""

    btn.click(submit_message, inputs=user_input, outputs=[output, user_input])
    user_input.submit(submit_message, inputs=user_input, outputs=[output, user_input])

app.launch()