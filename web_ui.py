import os
from flask import Flask, render_template_string, request, Response
from dotenv import load_dotenv
from elevenlabs import stream, set_api_key
from elevenlabs.api import Voices

# Load API key from .env
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise RuntimeError("ELEVENLABS_API_KEY not set in environment")
set_api_key(api_key)

# Initialize Flask app
app = Flask(__name__)

# Fetch available voices once
try:
    voices = Voices.from_api()
except Exception:
    voices = []

VOICE_NAMES = [v.name for v in voices] if voices else ["Rachel", "Daniel"]

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>ElevenLabs Web Conversation</title>
</head>
<body>
    <h1>ElevenLabs Web Conversation</h1>
    <form id="speech-form">
        <textarea id="text" rows="4" cols="60" placeholder="Enter text here"></textarea><br>
        <label for="voice">Voice:</label>
        <select id="voice">
        {% for name in voice_names %}
            <option value="{{ name }}">{{ name }}</option>
        {% endfor %}
        </select>
        <button type="submit">Speak</button>
    </form>
    <audio id="player" controls></audio>
    <script>
    document.getElementById('speech-form').addEventListener('submit', function(e){
        e.preventDefault();
        const text = document.getElementById('text').value;
        const voice = document.getElementById('voice').value;
        const player = document.getElementById('player');
        player.src = '/synthesize?text=' + encodeURIComponent(text) + '&voice=' + encodeURIComponent(voice);
        player.play();
    });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, voice_names=VOICE_NAMES)

@app.route('/synthesize')
def synthesize():
    text = request.args.get('text', '')
    voice_name = request.args.get('voice', VOICE_NAMES[0])
    voice = next((v for v in voices if v.name == voice_name), voice_name)

    audio_stream = stream(
        text=text,
        voice=voice,
        model="eleven_multilingual_v2",
        stream=True
    )

    def generate():
        for chunk in audio_stream:
            yield chunk

    return Response(generate(), mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True)
