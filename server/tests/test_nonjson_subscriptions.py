import json

from fastapi.testclient import TestClient

from server.app import api
from tests.utils_for_tests import is_valid_uuid

'''
СЦЕНАРИИ ТЕСТОВ

Общее:
Послал не json - получил ответ, что это не нормальный JSON

Подписки
Подписался - получил правильный ответ
Пытаешься подписаться на то, на что уже подписан - соотв. сообщение
Отписываешься от существующей подписки - ок
Отписываешься от несуществующей подписки - соотв. сообщение
'''


def test_read_main():
    client = TestClient(api)
    response = client.get("/")
    assert response.status_code == 200


def test_non_json(non_json_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(non_json_message)
        data = websocket.receive_json()
        assert data.get('messageType') == 2
        assert data.get('message').get('reason') == 'The message is not a valid JSON'


def test_normal_subscription(subscribe_normal_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(subscribe_normal_message)
        data = websocket.receive_json()
        assert data.get('messageType') == 1
        uuid_from_message = data.get('message').get('subscriptionId')
        assert is_valid_uuid(uuid_from_message)


def test_normal_unsubscribe(subscribe_normal_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(subscribe_normal_message)
        data = websocket.receive_json()
        uuid = data.get('message').get('subscriptionId')
        websocket.send_text(f'{{"messageType": 2, "message": {{"subscriptionId": "{uuid}"}}}}')
        data = websocket.receive_json()
        assert data.get('messageType') == 1
        assert data.get('message').get('subscriptionId') == uuid
        
def test_noexist_unsubscribe(unsubscribe_noexist_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(unsubscribe_noexist_message)
        data = websocket.receive_json()
        assert data.get('messageType') == 2
        assert data.get('message').get('reason') == 'The subscribe does not exist'

def test_subscribe_twice(subscribe_normal_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(subscribe_normal_message)
        websocket.receive_json()
        websocket.send_text(subscribe_normal_message)
        data = websocket.receive_json()
        assert data.get('messageType') == 2
        assert data.get('message').get('reason') == 'The subscribe already exists'
