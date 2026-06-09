def test_walking_submit_and_stats(test_app):
    client, TestingSessionLocal = test_app
    db = TestingSessionLocal()
    # create user
    from schemas import UserCreate
    import crud
    user = crud.create_user(db, UserCreate(username='walker', password='secret'))

    # obtain token
    resp = client.post('/token', data={'username': 'walker', 'password': 'secret'})
    assert resp.status_code == 200
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # submit walking activity
    payload = {"steps": 6000, "distance_km": None, "purpose": "Office Commute"}
    r = client.post('/walking/submit', json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data['steps'] == 6000

    # get stats
    s = client.get('/walking/stats', headers=headers)
    assert s.status_code == 200
    stats = s.json()
    assert stats['total_steps'] >= 6000
    assert stats['green_points'] >= 0


def test_walking_verify_as_admin(test_app):
    client, TestingSessionLocal = test_app
    db = TestingSessionLocal()
    from schemas import UserCreate
    import crud
    # create normal user and admin
    user = crud.create_user(db, UserCreate(username='w2', password='pw'))
    admin = crud.create_user(db, UserCreate(username='admin', password='adminpw'))
    # set roles
    u = crud.get_user_by_username(db, 'admin')
    u.role = 'admin'
    db.commit()

    # get tokens
    t_user = client.post('/token', data={'username': 'w2', 'password': 'pw'}).json()['access_token']
    t_admin = client.post('/token', data={'username': 'admin', 'password': 'adminpw'}).json()['access_token']

    headers_user = {"Authorization": f"Bearer {t_user}"}
    headers_admin = {"Authorization": f"Bearer {t_admin}"}

    # submit walking
    payload = {"steps": 7000, "distance_km": None, "purpose": "Local Errand"}
    r = client.post('/walking/submit', json=payload, headers=headers_user)
    assert r.status_code == 200
    wid = r.json()['id']

    # admin verify using ai_verified (no proof present so ai_confidence None)
    resp = client.post('/walking/verify', params={'walking_id': wid, 'level': 'ai_verified'}, headers=headers_admin)
    assert resp.status_code == 200
    ver = resp.json()
    assert ver['level'] in ('ai_verified', 'screenshot', 'self_reported', 'external')
