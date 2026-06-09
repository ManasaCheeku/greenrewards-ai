import pytest
import models


def test_admin_rbac_permissions(test_app):
    client, SessionLocal = test_app
    # create employee
    r = client.post('/users/', json={'username': 'emp', 'password': 'pw'})
    emp_id = r.json()['id']
    # create manager
    r = client.post('/users/', json={'username': 'mgr', 'password': 'pw'})
    mgr_id = r.json()['id']
    # create admin
    r = client.post('/users/', json={'username': 'admin', 'password': 'pw'})
    admin_id = r.json()['id']

    # set roles directly in DB
    db = SessionLocal()
    try:
        u = db.query(models.User).filter(models.User.id == mgr_id).first()
        u.role = 'manager'
        ua = db.query(models.User).filter(models.User.id == admin_id).first()
        ua.role = 'admin'
        db.commit()
    finally:
        db.close()

    # employee token
    r = client.post('/token', data={'username': 'emp', 'password': 'pw'})
    emp_token = r.json()['access_token']
    headers_emp = {'Authorization': f'Bearer {emp_token}'}
    res = client.get('/admin/proofs/pending', headers=headers_emp)
    assert res.status_code in (401, 403)

    # manager token should be denied for admin endpoint
    r = client.post('/token', data={'username': 'mgr', 'password': 'pw'})
    mgr_token = r.json()['access_token']
    headers_mgr = {'Authorization': f'Bearer {mgr_token}'}
    res = client.get('/admin/proofs/pending', headers=headers_mgr)
    assert res.status_code in (401, 403)

    # admin token should be allowed
    r = client.post('/token', data={'username': 'admin', 'password': 'pw'})
    admin_token = r.json()['access_token']
    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    res = client.get('/admin/proofs/pending', headers=headers_admin)
    assert res.status_code == 200

    # invalid token
    res = client.get('/admin/proofs/pending', headers={'Authorization': 'Bearer badtoken'})
    assert res.status_code == 401
