import pytest
import models
import main
import crud
from services import ai_verifier


def test_background_handles_exceptions_and_leaves_proof_pending(test_app, monkeypatch):
    client, SessionLocal = test_app
    # create user and a proof record via API
    r = client.post('/users/', json={'username': 'bguser', 'password': 'pw'})
    uid = r.json()['id']
    r = client.post('/token', data={'username': 'bguser', 'password': 'pw'})
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    db = SessionLocal()
    try:
        proof = crud.create_upload_proof(
            db,
            user_id=uid,
            filename='doc.jpg',
            content_type='image/jpeg',
            proof_type='travel',
            file_hash='doc-hash',
        )
        proof_id = proof.id
    finally:
        db.close()

    # monkeypatch verifier to raise
    def raise_exc(path, ptype):
        raise RuntimeError('simulated verifier failure')
    monkeypatch.setattr(ai_verifier, 'verify_proof', raise_exc)

    # call background directly and expect exception
    with pytest.raises(RuntimeError):
        main.process_proof_background(proof_id, main.UPLOAD_DIR + '/' + 'doc.jpg', 'travel')

    # ensure proof still pending
    db = SessionLocal()
    try:
        pf = db.query(models.UploadProof).filter(models.UploadProof.id == proof_id).first()
        assert pf.status == 'pending'
    finally:
        db.close()


def test_manual_retry_succeeds_after_transient_failure(test_app, monkeypatch):
    client, SessionLocal = test_app
    r = client.post('/users/', json={'username': 'retryuser', 'password': 'pw'})
    uid = r.json()['id']
    r = client.post('/token', data={'username': 'retryuser', 'password': 'pw'})
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    file_path = main.UPLOAD_DIR + '/' + 'retry.jpg'
    with open(file_path, 'wb') as f:
        f.write(b'bus 5 km')

    db = SessionLocal()
    try:
        proof = crud.create_upload_proof(
            db,
            user_id=uid,
            filename='retry.jpg',
            content_type='image/jpeg',
            proof_type='travel',
            file_hash='retry-hash',
        )
        proof_id = proof.id
    finally:
        db.close()

    calls = {'n': 0}
    def flaky(path, ptype):
        calls['n'] += 1
        if calls['n'] == 1:
            raise RuntimeError('transient')
        return ai_verifier.verify_proof.__wrapped__(path, ptype) if hasattr(ai_verifier.verify_proof, '__wrapped__') else ai_verifier.verify_proof(path, ptype)

    # Monkeypatch with function that raises first then calls original
    orig = ai_verifier.verify_proof
    def first_then_orig(path, ptype):
        calls['n'] += 1
        if calls['n'] == 1:
            raise RuntimeError('transient')
        return orig(path, ptype)
    monkeypatch.setattr(ai_verifier, 'verify_proof', first_then_orig)

    # first call -> raises
    with pytest.raises(RuntimeError):
        main.process_proof_background(proof_id, file_path, 'travel')
    # second call -> should succeed
    main.process_proof_background(proof_id, file_path, 'travel')

    # check proof verified
    db = SessionLocal()
    try:
        pf = db.query(models.UploadProof).filter(models.UploadProof.id == proof_id).first()
        assert pf.status in ('verified', 'rejected')
    finally:
        db.close()
