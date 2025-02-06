from flask import Flask, request, jsonify, send_file, render_template
import os
import google.generativeai as genai
from gtts import gTTS
from flask_cors import CORS
import pygame
from dotenv import load_dotenv

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)  # Allow all origins, adjust for security if needed

load_dotenv()  # Load environment variables from .env file

# Configure Generative AI with API key
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

def chatbot_response(user_input):
    """Generates chatbot response using the fine-tuned Generative AI model."""
    try:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            model_name="tunedModels/copy-of-finalefinal-mm6hnii9n2pp",
            generation_config=generation_config,
        )
        
        response = model.generate_content(f"Act as a lawyer and provide advice on {user_input}")
        return response.text.replace("**", "").replace("*", "")
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route('/')
def home():
    """Renders the homepage."""
    return render_template("index.html")

@app.route('/chat.html')
def chat():
    """Renders the chat page."""
    return render_template("chat.html")

@app.route('/process', methods=['POST'])
def process_input():
    """Handles user input, generates chatbot response, and optionally provides TTS output."""
    data = request.get_json()
    user_message = data.get('text', '')
    tts_enabled = data.get('tts', False)
    
    if not user_message:
        return jsonify({"response": "No input provided"}), 400

    bot_response = chatbot_response(user_message)
    
    if tts_enabled:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Generate TTS audio
            audio_path = 'audio/output.mp3'
            tts = gTTS(bot_response)
            tts.save(audio_path)
            
            # Play the generated audio
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            return jsonify({"response": bot_response, "audio_url": f"/audio"}), 200
        except Exception as e:
            print(f"Error occurred during TTS: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"response": bot_response})

@app.route('/audio', methods=['GET'])
def get_audio():
    """Serves the generated TTS audio file."""
    audio_path = 'audio/output.mp3'
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mpeg')
    return jsonify({"error": "Audio file not found"}), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)