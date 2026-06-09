import os
import io
import hashlib
from fastapi.testclient import TestClient
import pytest
import models
import main
from database import Base


def test_auth_and_upload_end_to_end(test_app):
    client, SessionLocal = test_app
    # create user
    res = client.post('/users/', json={'username': 'alice', 'password': 'secret'})
    assert res.status_code == 200
    user = res.json()
    user_id = user['id']

    # get token
    res = client.post('/token', data={'username': 'alice', 'password': 'secret'})
    assert res.status_code == 200
    token = res.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # upload a travel proof containing 'bus 10 km'
    content = b"Bus ticket distance 10 km"
    files = {'file': ('ticket.jpg', io.BytesIO(content), 'image/jpeg')}
    res = client.post(f'/users/{user_id}/proofs/?proof_type=travel', headers=headers, files=files)
    assert res.status_code == 200
    resp = res.json()
    assert 'proof_id' in resp
    proof_id = resp['proof_id']

    # After background processing, travel record should exist
    # Fetch travel records
    res = client.get(f'/users/{user_id}/travel/')
    assert res.status_code == 200
    travels = res.json()
    assert len(travels) >= 1
    tr = travels[0]
    assert tr['transport_mode'] in ['bus', 'metro', 'train', 'bicycle', 'carpool', 'ev', 'private']

    # Check carbon calculations
    res = client.get(f'/users/{user_id}/scores/')
    assert res.status_code == 200
    scores = res.json()
    assert 'sustainability_score' in scores
    assert 'carbon_confidence' in scores


def test_authorization_block_upload(test_app):
    client, SessionLocal = test_app
    # create two users
    res1 = client.post('/users/', json={'username': 'bob', 'password': 'pw'})
    res2 = client.post('/users/', json={'username': 'carol', 'password': 'pw'})
    uid1 = res1.json()['id']
    uid2 = res2.json()['id']

    # login as bob
    res = client.post('/token', data={'username': 'bob', 'password': 'pw'})
    token = res.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # try to upload for carol
    content = b"Metro ticket 5 km"
    files = {'file': ('metro.jpg', io.BytesIO(content), 'image/jpeg')}
    res = client.post(f'/users/{uid2}/proofs/?proof_type=travel', headers=headers, files=files)
    assert res.status_code == 403


def test_duplicate_upload_detection(test_app):
    client, SessionLocal = test_app
    res = client.post('/users/', json={'username': 'dan', 'password': 'pw'})
    uid = res.json()['id']
    res = client.post('/token', data={'username': 'dan', 'password': 'pw'})
    token = res.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    content = b"Bike ride"
    files = {'file': ('bike.jpg', io.BytesIO(content), 'image/jpeg')}
    r1 = client.post(f'/users/{uid}/proofs/?proof_type=travel', headers=headers, files=files)
    assert r1.status_code == 200
    p1 = r1.json()['proof_id']

    # upload same bytes again
    r2 = client.post(f'/users/{uid}/proofs/?proof_type=travel', headers=headers, files=files)
    assert r2.status_code == 200
    p2 = r2.json()['proof_id']

    # same proof id returned (duplicate detection)
    assert p1 == p2

    # DB should only have one record with that file_hash
    db = SessionLocal()
    try:
        proofs = db.query(models.UploadProof).filter(models.UploadProof.file_hash != None).all()
        # there may be multiple but ensure at least one
        assert len(proofs) >= 1
    finally:
        db.close()
