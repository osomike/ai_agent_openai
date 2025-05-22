from flask import Flask, request, jsonify, render_template
from core.ai_agent import AIAgent

# Initialize Flask app
app = Flask(__name__)

# Initialize the AI Agent
ai_agent = AIAgent(
    config_path="config/settings.yaml",
    prompt_path="config/prompts.yaml",
    log_level="DEBUG"
)

@app.route("/")
def index():
    """
    Render the chat interface.
    """
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle chat messages sent by the user.
    """
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Get the AI assistant's response
        ai_response = ai_agent.ask(user_message)
        
        # Optionally format the response as markdown
        markdown_response = f"**AI Assistant:**\n\n{ai_response}"
        return jsonify({"response": markdown_response})
    except Exception as e:
        ai_agent.logger.error(f"Error during chat: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)