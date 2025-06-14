import os
from flask import Flask, Response, request, render_template_string
from dotenv import load_dotenv
from elevenlabs import stream, set_api_key
from stream_conversation import LiveConversationPlayer

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise RuntimeError("ELEVENLABS_API_KEY not set")
set_api_key(api_key)

# Use LiveConversationPlayer to fetch available voices
player = LiveConversationPlayer()
voices = player.get_available_voices()

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<title>Live Conversation Player</title>
</head>
<body>
<h1>Live Conversation Player</h1>
<textarea id='text' rows='4' cols='50' placeholder='Enter text here'></textarea><br>
<select id='voice'>
{% for v in voices %}
<option value='{{ v.voice_id }}'>{{ v.name }}</option>
{% endfor %}
</select>
<button onclick='play()'>Play</button>
<audio id='audio' controls></audio>
<script>
function play() {
  const text = document.getElementById('text').value;
  const voice = document.getElementById('voice').value;
  const audio = document.getElementById('audio');
  audio.src = '/stream?text=' + encodeURIComponent(text) + '&voice=' + voice;
  audio.play();
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML, voices=voices)

@app.route('/stream')
def stream_audio():
    text = request.args.get('text', '')
    voice_id = request.args.get('voice')
    selected = next((v for v in voices if v.voice_id == voice_id), voices[0])
    audio_stream = stream(text=text, voice=selected, model="eleven_multilingual_v2", stream=True)
    def generate():
        for chunk in audio_stream:
            yield chunk
    return Response(generate(), mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True)
