from flask import Flask, request, send_file, Response
from io import BytesIO
import logging
import tempfile
import os
import wave
from piper import PiperVoice
from indicnlp.tokenize import indic_tokenize

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load Piper TTS Hindi model
try:
    voice = PiperVoice.load(
        model_path='/app/models/hi_IN-pratham-medium.onnx',
        config_path='/app/models/hi_IN-pratham-medium.onnx.json'
    )
    logger.info("Piper TTS Hindi model (hi_IN-pratham-medium) loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Piper TTS: {e}")
    raise

# Text preprocessing for Hindi
def preprocess_text(text):
    try:
        return ' '.join(indic_tokenize.trivial_tokenize(text, lang='hi'))
    except Exception as e:
        logger.error(f"Error preprocessing text: {e}")
        return text

# Audio generation function
def generate_audio(text):
    try:
        # Preprocess Hindi text
        processed_text = preprocess_text(text)
        
        # Create a temporary WAV file path
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_path = temp_wav.name

        # Generate audio using PiperVoice
        with wave.open(temp_wav_path, 'wb') as wav_file:
            voice.synthesize(processed_text, wav_file)

        # Read the WAV file into BytesIO
        bio = BytesIO()
        with open(temp_wav_path, 'rb') as wav_file:
            bio.write(wav_file.read())
        bio.seek(0)

        # Clean up temporary file
        os.unlink(temp_wav_path)

        logger.info(f"Audio generated successfully for text: {text}")
        return bio

    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise

# Home route
@app.route('/')
def index():
    logger.info("Accessing home route")
    return '''
    <h2>✅ Piper TTS Hindi Ready</h2>
    <p>Use <code>GET /output?text=हेलो+यह+एक+टेस्ट+है</code> to download/play audio.</p>
    <p>Or <code>POST /generate</code> with JSON body {"text": "हेलो यह एक टेस्ट है"}</p>
    <p>Try <a href="/output">/output</a> for a test audio.</p>
    '''

# Ping route for health check
@app.route('/ping')
def ping():
    logger.info("Ping route accessed")
    return 'OK', 200

# Output route with query parameters
@app.route('/output')
def output():
    logger.info("Accessing output route")
    text = request.args.get('text', 'हेलो, यह एक टेस्ट है।')
    try:
        bio = generate_audio(text)
        return send_file(
            bio,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='output.wav'
        )
    except Exception as e:
        logger.error(f"Error in output route: {e}")
        return f"Error: {e}", 500

# Generate route for POST requests
@app.route('/generate', methods=['POST'])
def generate():
    logger.info("Accessing generate route")
    data = request.json
    if not data or 'text' not in data:
        logger.error("Bad Request: Missing text")
        return 'Bad Request: Missing text', 400
    text = data['text']
    try:
        bio = generate_audio(text)
        return send_file(
            bio,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='output.wav'
        )
    except Exception as e:
        logger.error(f"Error in generate route: {e}")
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run()
