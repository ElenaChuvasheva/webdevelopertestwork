from fastapi.testclient import TestClient

from server.app import api


def test_read_main():
    client = TestClient(api)
    response = client.get("/")
    assert response.status_code == 200


def test_non_json(non_json_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(non_json_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2
        assert data['message']['reason'] == 'The message is not a valid JSON'


def test_nonexisting_message_code(nonexisting_message_code):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(nonexisting_message_code)
        data = websocket.receive_json()
        assert data['messageType'] == 2
