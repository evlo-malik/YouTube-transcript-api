from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os


app = Flask(__name__)

def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    else:
        return None

@app.route('/test_youtube_connection')
def test_youtube_connection():
    import requests
    try:
        response = requests.get('https://www.youtube.com', timeout=5)
        if response.status_code == 200:
            return 'Connected to YouTube successfully.'
        else:
            return f'Failed to connect to YouTube. Status code: {response.status_code}'
    except Exception as e:
        return f'An error occurred: {e}'


@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify({'transcript': transcript})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


