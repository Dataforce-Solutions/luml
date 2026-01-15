from fastapi.testclient import TestClient
from luml.server import app

client = TestClient(app)

def test_delete_account_no_auth():
    response = client.delete("/auth/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
