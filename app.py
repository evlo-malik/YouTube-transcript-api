from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re
import requests
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

# Get proxy details from environment variables
PROXY_USER = os.environ.get('PROXY_USER')
PROXY_PASS = os.environ.get('PROXY_PASS')
PROXY_ADDRESS = os.environ.get('PROXY_ADDRESS', 'brd.superproxy.io')
PROXY_PORT = os.environ.get('PROXY_PORT', '22225')

if PROXY_ADDRESS and PROXY_PORT:
    if PROXY_USER and PROXY_PASS:
        proxy_auth = f'{PROXY_USER}:{PROXY_PASS}@'
    else:
        proxy_auth = ''
    proxy_url = f'http://{proxy_auth}{PROXY_ADDRESS}:{PROXY_PORT}'
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    # Create a session with proxies
    session = requests.Session()
    session.proxies.update(proxies)

    # Update the YouTubeTranscriptApi session
    YouTubeTranscriptApi._session = session
else:
    # No proxy configuration
    session = requests.Session()
    YouTubeTranscriptApi._session = session

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
        logging.exception("Error fetching transcript")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
