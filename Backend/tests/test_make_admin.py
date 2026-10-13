import sys

from conftest import BACKEND_DIR, register_and_login

sys.path.insert(0, str(BACKEND_DIR / "harvest_scripts"))
from make_admin import set_admin


def test_set_admin_promotes_user_and_unlocks_admin_routes(client, db):
    headers = register_and_login(client, "Boss@Example.com")
    assert client.get("/api/admin/users", headers=headers).status_code == 403

    assert set_admin(db, "boss@example.com") is True # email match is case-insensitive

    assert client.get("/api/admin/users", headers=headers).status_code == 200


def test_set_admin_revoke(client, db):
    headers = register_and_login(client, "boss@example.com")
    set_admin(db, "boss@example.com")

    assert set_admin(db, "boss@example.com", is_admin=False) is True

    assert client.get("/api/admin/users", headers=headers).status_code == 403


def test_set_admin_unknown_email_returns_false(db):
    assert set_admin(db, "nobody@example.com") is False
