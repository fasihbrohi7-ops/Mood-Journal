import json
import os
import re
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, send_from_directory
# Load environment variables if dotenv is present
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    load_dotenv('.env')
except ImportError:
    pass

try:
    from api.sentiment import analyze_sentiment, get_mood_bucket
except ImportError:
    from sentiment import analyze_sentiment, get_mood_bucket

# Determine public folder path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'public'))

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path='')

class StorageManager:
    def __init__(self):
        self.redis_url = os.environ.get('UPSTASH_REDIS_REST_URL')
        self.redis_token = os.environ.get('UPSTASH_REDIS_REST_TOKEN')
        self.use_redis = bool(self.redis_url and self.redis_token)
        
        if self.use_redis:
            try:
                from upstash_redis import Redis
                self.client = Redis(url=self.redis_url, token=self.redis_token)
                print('[Storage] Using Upstash Redis REST datastore.')
            except Exception as e:
                print(f'[Storage] Failed to initialize Upstash Redis: {e}. Falling back to local storage.')
                self.use_redis = False
                self._init_local()
        else:
            print('[Storage] UPSTASH_REDIS credentials not set. Using local JSON storage.')
            self._init_local()

    def _init_local(self):
        self.local_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'entries.json'))
        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)
        if not os.path.exists(self.local_path):
            with open(self.local_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def _read_local(self):
        try:
            with open(self.local_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_local(self, data):
        with open(self.local_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def hget(self, hash_name: str, key: str):
        if self.use_redis:
            val = self.client.hget(hash_name, key)
            if isinstance(val, bytes):
                return val.decode('utf-8')
            return val
        data = self._read_local()
        return data.get(hash_name, {}).get(key)

    def hset(self, hash_name: str, key: str, value: str):
        if self.use_redis:
            return self.client.hset(hash_name, key, value)
        data = self._read_local()
        if hash_name not in data:
            data[hash_name] = {}
        data[hash_name][key] = value
        self._write_local(data)
        return True

    def hgetall(self, hash_name: str):
        if self.use_redis:
            res = self.client.hgetall(hash_name)
            if not res:
                return {}
            cleaned = {}
            for k, v in res.items():
                decoded_k = k.decode('utf-8') if isinstance(k, bytes) else str(k)
                decoded_v = v.decode('utf-8') if isinstance(v, bytes) else str(v)
                cleaned[decoded_k] = decoded_v
            return cleaned
        data = self._read_local()
        return data.get(hash_name, {})

# Global datastore instance
storage = StorageManager()

def get_mood_bucket(score: float) -> str:
    if score < -0.5:
        return 'very_negative'
    elif score < -0.1:
        return 'negative'
    elif score <= 0.1:
        return 'neutral'
    elif score <= 0.5:
        return 'positive'
    else:
        return 'very_positive'

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

@app.route('/api/entry', methods=['POST', 'OPTIONS'])
def create_or_update_entry():
    if request.method == 'OPTIONS':
        return ('', 204)
        
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON body.'}), 400

    raw_text = data.get('text')
    if raw_text is None or not isinstance(raw_text, str):
        return jsonify({'error': 'text is required and must be a string.'}), 400

    text = raw_text.strip()
    if len(text) < 1 or len(text) > 1000:
        return jsonify({'error': 'Entry text must be between 1 and 1000 characters.'}), 400

    target_date = data.get('date')
    if target_date and isinstance(target_date, str):
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', target_date):
            return jsonify({'error': 'date format must be YYYY-MM-DD.'}), 400
    else:
        target_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    analysis = analyze_sentiment(text)
    score = analysis['score']
    bucket = analysis['bucket']
    language = analysis['language']

    try:
        existing_raw = storage.hget('entries', target_date)
        if existing_raw:
            existing = json.loads(existing_raw) if isinstance(existing_raw, str) else existing_raw
            created_at = existing.get('created_at', now_iso)
        else:
            created_at = now_iso

        record = {
            'date': target_date,
            'text': text,
            'score': score,
            'bucket': bucket,
            'language': language,
            'created_at': created_at,
            'updated_at': now_iso
        }

        storage.hset('entries', target_date, json.dumps(record, ensure_ascii=False))

        return jsonify({
            'date': target_date,
            'text': text,
            'score': score,
            'bucket': bucket,
            'language': language
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to persist entry: {str(e)}'}), 500

@app.route('/api/entries', methods=['GET'])
def get_entries():
    try:
        days_param = request.args.get('days', default=371, type=int)
        days = max(1, min(days_param, 1000))

        raw_entries = storage.hgetall('entries')
        entries_list = []

        cutoff_date = (datetime.now(timezone.utc).date() - timedelta(days=days)).strftime('%Y-%m-%d')

        for date_str, raw_val in raw_entries.items():
            try:
                item = json.loads(raw_val) if isinstance(raw_val, str) else raw_val
                entry_date = item.get('date', date_str)
                if entry_date >= cutoff_date:
                    entries_list.append({
                        'date': entry_date,
                        'score': item.get('score', 0.0),
                        'bucket': item.get('bucket', 'neutral')
                    })
            except Exception:
                continue

        entries_list.sort(key=lambda x: x['date'], reverse=True)
        return jsonify({'entries': entries_list}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve entries: {str(e)}'}), 500

@app.route('/api/entry/<date>', methods=['GET'])
def get_entry_by_date(date):
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        return jsonify({'error': 'Invalid date format. Expected YYYY-MM-DD.'}), 400

    try:
        raw_val = storage.hget('entries', date)
        if not raw_val:
            return jsonify({'error': 'Entry not found'}), 404

        item = json.loads(raw_val) if isinstance(raw_val, str) else raw_val
        return jsonify({
            'date': item.get('date', date),
            'text': item.get('text', ''),
            'score': item.get('score', 0.0),
            'bucket': item.get('bucket', 'neutral'),
            'language': item.get('language', 'English')
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve entry: {str(e)}'}), 500

@app.route('/api/streak', methods=['GET'])
def get_streak():
    try:
        raw_entries = storage.hgetall('entries')
        dates = set()
        for k, v in raw_entries.items():
            try:
                item = json.loads(v) if isinstance(v, str) else v
                d_str = item.get('date', k)
                if re.match(r'^\d{4}-\d{2}-\d{2}$', d_str):
                    dates.add(datetime.strptime(d_str, '%Y-%m-%d').date())
            except Exception:
                continue

        if not dates:
            return jsonify({'current_streak': 0, 'longest_streak': 0}), 200

        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        current_streak = 0
        if today in dates:
            check_date = today
            while check_date in dates:
                current_streak += 1
                check_date -= timedelta(days=1)
        elif yesterday in dates:
            check_date = yesterday
            while check_date in dates:
                current_streak += 1
                check_date -= timedelta(days=1)

        sorted_dates = sorted(dates)
        longest_streak = 1
        current_run = 1

        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
                current_run += 1
                if current_run > longest_streak:
                    longest_streak = current_run
            else:
                current_run = 1

        return jsonify({
            'current_streak': current_streak,
            'longest_streak': longest_streak
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to compute streak: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'storage': 'upstash_redis' if storage.use_redis else 'local_json',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200

@app.route('/')
def index():
    if os.path.exists(os.path.join(PUBLIC_DIR, 'index.html')):
        return send_from_directory(PUBLIC_DIR, 'index.html')
    return jsonify({'message': 'Mood Journal API is running. Place index.html in public/'}), 200

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(PUBLIC_DIR, path)):
        return send_from_directory(PUBLIC_DIR, path)
    return send_from_directory(PUBLIC_DIR, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'Starting Mood Journal on http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True)
