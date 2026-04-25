"""
Transcript Server — chạy local để lấy phụ đề YouTube
Setup:
    pip install youtube-transcript-api flask flask-cors
Chạy:
    python transcript_server.py
Sau đó mở app HTML qua VS Code Live Server (hoặc python -m http.server 8080)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

app = Flask(__name__)
CORS(app)  # cho phép HTML app gọi cross-origin

@app.route('/transcript')
def get_transcript():
    video_id = request.args.get('v', '').strip() or request.args.get('video_id', '').strip()
    if not video_id:
        return jsonify({'error': 'Thiếu tham số video_id'}), 400

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # Ưu tiên lấy tiếng Anh hoặc tiếng Việt
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB', 'vi'])
        except Exception:
            # Nếu không có, lấy transcript đầu tiên trong danh sách và dịch sang tiếng Anh
            for t in transcript_list:
                transcript = t.translate('en')
                break
                
        raw = transcript.fetch()

        # Chuyển sang format {text, start, end}
        result = []
        for seg in raw:
            result.append({
                'text': seg['text'].replace('\n', ' ').strip(),
                'start': round(seg['start'], 3),
                'end': round(seg['start'] + seg['duration'], 3)
            })

        return jsonify({'sentences': result, 'count': len(result)})

    except TranscriptsDisabled:
        return jsonify({'error': 'Video này đã tắt phụ đề.'}), 404
    except NoTranscriptFound:
        return jsonify({'error': 'Không tìm thấy phụ đề tiếng Anh cho video này.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Transcript server đang chạy'})


if __name__ == '__main__':
    print("=" * 55)
    print("  Transcript Server đang chạy tại http://localhost:5000")
    print("  Thử: http://localhost:5000/health")
    print("  Dừng: Ctrl+C")
    print("=" * 55)
    app.run(port=5000, debug=False)
