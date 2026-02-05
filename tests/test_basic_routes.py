def test_login_page_loads(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_home_redirects_without_login(client):
    res = client.get("/", follow_redirects=False)
    assert res.status_code in (302, 303)


def test_gallery_requires_login(client):
    res = client.get("/gallery", follow_redirects=False)
    assert res.status_code in (302, 303)


def test_upload_blocked_without_login(client):
    res = client.post(
        "/upload",
        files={"image": ("test.jpg", b"fake", "image/jpeg")},
        follow_redirects=False
    )
    assert res.status_code in (302, 303)


def test_logout_redirects(client):
    res = client.get("/logout", follow_redirects=False)
    assert res.status_code in (302, 303)


def test_update_narrative_requires_auth(client):
    res = client.post(
        "/update-narrative",
        data={"filename": "fake.jpg", "narrative": "hello"},
        follow_redirects=False
    )
    assert res.status_code in (302, 303)
