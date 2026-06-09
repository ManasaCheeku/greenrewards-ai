import io
import os
import pytest


def test_file_size_limit_enforced(test_app, monkeypatch):
    client, SessionLocal = test_app
    # create user
    r = client.post('/users/', json={'username': 'sizeuser', 'password': 'pw'})
    uid = r.json()['id']
    r = client.post('/token', data={'username': 'sizeuser', 'password': 'pw'})
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # set MAX_UPLOAD_BYTES env small
    monkeypatch.setenv('MAX_UPLOAD_BYTES', '10')
    # large content
    big = b'a' * 1024
    files = {'file': ('big.jpg', io.BytesIO(big), 'image/jpeg')}
    res = client.post(f'/users/{uid}/proofs/?proof_type=travel', headers=headers, files=files)
    assert res.status_code == 400


def test_mime_validation(test_app):
    client, SessionLocal = test_app
    r = client.post('/users/', json={'username': 'mimeuser', 'password': 'pw'})
    uid = r.json()['id']
    r = client.post('/token', data={'username': 'mimeuser', 'password': 'pw'})
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    files = {'file': ('file.txt', io.BytesIO(b'text'), 'text/plain')}
    res = client.post(f'/users/{uid}/proofs/?proof_type=food', headers=headers, files=files)
    assert res.status_code == 400


def test_rate_limiting_absent_by_default(test_app):
    client, SessionLocal = test_app
    r = client.post('/users/', json={'username': 'ratetest', 'password': 'pw'})
    uid = r.json()['id']
    r = client.post('/token', data={'username': 'ratetest', 'password': 'pw'})
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # send multiple uploads quickly; expect they all process (no 429)
    for i in range(5):
        files = {'file': (f'file{i}.jpg', io.BytesIO(b'data'), 'image/jpeg')}
        res = client.post(f'/users/{uid}/proofs/?proof_type=travel', headers=headers, files=files)
        assert res.status_code == 200
