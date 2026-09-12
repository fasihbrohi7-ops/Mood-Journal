import os
import json
import pytest
from datetime import datetime, timezone, timedelta

# Set temporary test file for local storage
os.environ['UPSTASH_REDIS_REST_URL'] = ''
os.environ['UPSTASH_REDIS_REST_TOKEN'] = ''

from api.index import app, storage, get_mood_bucket

@pytest.fixture
def client(tmp_path):
    # Point storage to isolated temp directory for each test
    test_file = str(tmp_path / 'test_entries.json')
    storage.local_path = test_file
    storage._write_local({})
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_sentiment_buckets():
    assert get_mood_bucket(-0.8) == 'very_negative'
    assert get_mood_bucket(-0.51) == 'very_negative'
    assert get_mood_bucket(-0.5) == 'negative'
    assert get_mood_bucket(-0.3) == 'negative'
    assert get_mood_bucket(-0.1) == 'neutral'
    assert get_mood_bucket(0.0) == 'neutral'
    assert get_mood_bucket(0.1) == 'neutral'
    assert get_mood_bucket(0.2) == 'positive'
    assert get_mood_bucket(0.5) == 'positive'
    assert get_mood_bucket(0.6) == 'very_positive'
    assert get_mood_bucket(1.0) == 'very_positive'

def test_create_and_update_entry(client):
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    # 1. Create entry
    res = client.post('/api/entry', json={'text': 'Today was an amazing, cheerful, and successful day!'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['date'] == today
    assert 'amazing' in data['text']
    assert data['score'] > 0
    assert data['bucket'] in ('positive', 'very_positive')

    # Check that it is stored
    stored_raw = storage.hget('entries', today)
    assert stored_raw is not None
    stored = json.loads(stored_raw)
    first_created_at = stored['created_at']

    # 2. Update entry on the same day
    res_update = client.post('/api/entry', json={'text': 'Actually, it turned out to be very terrible and sad.'})
    assert res_update.status_code == 200
    updated_data = res_update.get_json()
    assert updated_data['date'] == today
    assert 'terrible' in updated_data['text']
    assert updated_data['score'] < 0
    assert updated_data['bucket'] in ('negative', 'very_negative')

    # Confirm updated, not duplicated
    all_entries = storage.hgetall('entries')
    assert len(all_entries) == 1
    stored_updated = json.loads(storage.hget('entries', today))
    assert stored_updated['created_at'] == first_created_at

def test_validation(client):
    # No JSON body
    res = client.post('/api/entry', data='not json', content_type='application/json')
    assert res.status_code == 400

    # Missing text
    res = client.post('/api/entry', json={})
    assert res.status_code == 400

    # Empty text
    res = client.post('/api/entry', json={'text': ''})
    assert res.status_code == 400

    # Whitespace text
    res = client.post('/api/entry', json={'text': '   \n  '})
    assert res.status_code == 400

    # 1000 characters - should succeed
    exact_1000 = 'a' * 1000
    res = client.post('/api/entry', json={'text': exact_1000})
    assert res.status_code == 200

    # 1001 characters - should fail
    too_long = 'a' * 1001
    res = client.post('/api/entry', json={'text': too_long})
    assert res.status_code == 400

def test_get_entries_list(client):
    today = datetime.now(timezone.utc).date()
    d1 = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    d2 = (today - timedelta(days=2)).strftime('%Y-%m-%d')

    client.post('/api/entry', json={'date': d1, 'text': 'Day one was great!'})
    client.post('/api/entry', json={'date': d2, 'text': 'Day two was okay.'})

    res = client.get('/api/entries')
    assert res.status_code == 200
    data = res.get_json()
    assert 'entries' in data
    assert len(data['entries']) == 2
    # Ensure full text is not leaked in bulk entries response
    for item in data['entries']:
        assert 'date' in item
        assert 'score' in item
        assert 'bucket' in item
        assert 'text' not in item

def test_get_entry_by_date(client):
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    client.post('/api/entry', json={'date': today, 'text': 'Detailed thoughts for the day.'})

    # Success
    res = client.get(f'/api/entry/{today}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['date'] == today
    assert data['text'] == 'Detailed thoughts for the day.'
    assert 'score' in data
    assert 'bucket' in data

    # 404 for missing
    res_404 = client.get('/api/entry/2020-01-01')
    assert res_404.status_code == 404

    # 400 for bad format
    res_400 = client.get('/api/entry/not-a-date')
    assert res_400.status_code == 400

def test_streak_calculation(client):
    # Empty
    res = client.get('/api/streak')
    assert res.status_code == 200
    assert res.get_json() == {'current_streak': 0, 'longest_streak': 0}

    today = datetime.now(timezone.utc).date()
    
    # Yesterday only -> current streak should be 1
    y_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    client.post('/api/entry', json={'date': y_str, 'text': 'Logged yesterday'})
    res = client.get('/api/streak')
    assert res.get_json()['current_streak'] == 1
    assert res.get_json()['longest_streak'] == 1

    # Today added -> current streak should be 2
    t_str = today.strftime('%Y-%m-%d')
    client.post('/api/entry', json={'date': t_str, 'text': 'Logged today'})
    res = client.get('/api/streak')
    assert res.get_json()['current_streak'] == 2
    assert res.get_json()['longest_streak'] == 2

    # Add historical sequence with gap: 10, 11, 12, 13, 14 days ago (5 days)
    for i in range(10, 15):
        past_date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        client.post('/api/entry', json={'date': past_date, 'text': f'Past day {i}'})

    res = client.get('/api/streak')
    data = res.get_json()
    assert data['current_streak'] == 2
    assert data['longest_streak'] == 5

def test_health_check(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'healthy'

def test_static_routes(client):
    res_index = client.get('/')
    assert res_index.status_code == 200
    assert b'Mood Journal' in res_index.data

    res_css = client.get('/style.css')
    assert res_css.status_code == 200

    res_js = client.get('/app.js')
    assert res_js.status_code == 200
