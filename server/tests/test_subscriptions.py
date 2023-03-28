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
Отписываешься не с uuid - ошибка

Заявки
Выложил заявку - ок
Отписка от несуществующей заявки - ошибка
Отписка от обработанной заявки - ошибка
Получение всех заявок - список
Запись в базу - uuid из сообщения
Запрос заявок - список с заявкой
Запрос заявок при их отсутствии - пустой список
'''


def test_normal_subscription(subscribe_normal_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(subscribe_normal_message)
        data = websocket.receive_json()
        assert data['messageType'] == 1
        uuid_from_message = data['message']['subscriptionId']
        assert is_valid_uuid(uuid_from_message)


def test_subscribe_noexist_instrument(subscribe_noexist_instr_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(subscribe_noexist_instr_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2


def test_normal_unsubscribe(subscribe_normal_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(subscribe_normal_message)
        data = websocket.receive_json()
        uuid = data['message']['subscriptionId']
        websocket.send_text(f'{{"messageType": 2, "message": {{"subscriptionId": "{uuid}"}}}}')
        data = websocket.receive_json()
        assert data['messageType'] == 1
        assert data['message']['subscriptionId'] == uuid
        
def test_noexist_unsubscribe(unsubscribe_noexist_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(unsubscribe_noexist_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2
        assert data['message']['reason'] == 'The subscribe does not exist'

def test_not_uuid_unsubscribe(unsubscribe_not_uuid_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(unsubscribe_not_uuid_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2


def test_subscribe_twice(subscribe_normal_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(subscribe_normal_message)
        websocket.receive_json()
        websocket.send_text(subscribe_normal_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2
        assert data['message']['reason'] == 'The subscribe already exists'

def test_quotes(subscribe_normal_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(subscribe_normal_message)
        websocket.receive_json()
        data = websocket.receive_json()
        assert data['messageType'] == 4
        fields_external = ('subscriptionId', 'instrument', 'quotes')
        assert all(map(data['message'].__contains__, fields_external))
        quote = data['message']['quotes'][0]
        fields_internal = ('bid', 'offer', 'minAmount', 'maxAmount', 'timestamp')
        assert all(map(quote.__contains__, fields_internal))