from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

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
        # Optionally use proxy settings
        proxy_address = os.environ.get("PROXY")
        if proxy_address:
            proxies = {"http": proxy_address, "https": proxy_address}
            transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify({'transcript': transcript})
    except Exception as e:
        logging.exception("Error fetching transcript")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
