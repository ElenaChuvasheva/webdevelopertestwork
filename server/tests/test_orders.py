from fastapi.testclient import TestClient

from server.app import api
from tests.utils_for_tests import is_valid_uuid


def test_place_normal_order(place_normal_order_message, temp_db):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_normal_order_message)
        data = websocket.receive_json()
        assert data['messageType'] == 3
        uuid_from_message = data['message']['orderId']
        assert is_valid_uuid(uuid_from_message)
        assert data['message']['orderStatus'] == 'active'


def test_place_order_noexist_instr(place_order_noexist_instr_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_order_noexist_instr_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2


def test_place_order_noexist_side(place_order_noexist_side_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_order_noexist_side_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2


def test_place_order_negative_price(place_order_negative_price_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_order_negative_price_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2


def test_place_order_negative_amount(place_order_negative_amount_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_order_negative_amount_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2


def test_cancel_order(place_normal_order_message, temp_db):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_normal_order_message)
        data = websocket.receive_json()
        uuid = data['message']['orderId']
        websocket.send_text(f'{{"messageType": 4, "message": '
                            f'{{"orderId": "{uuid}"}}}}')
        data = websocket.receive_json()
        assert data['messageType'] == 3
        assert data['message']['orderId'] == uuid
        assert data['message']['orderStatus'] == 'cancelled'


def test_cancel_noexist_order(cancel_noexist_order_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(cancel_noexist_order_message)
        data = websocket.receive_json()
        assert data['messageType'] == 2
        assert data['message']['reason'] == 'The order does not exist'


def test_cancel_processed_order(place_normal_order_message, temp_db):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_normal_order_message)
        data = websocket.receive_json()
        uuid = data['message']['orderId']
        websocket.receive_json()
        websocket.send_text(f'{{"messageType": 4, "message": '
                            f'{{"orderId": "{uuid}"}}}}')
        data = websocket.receive_json()
        assert data['messageType'] == 2
        reason = data['message']['reason']
        assert (reason == 'The order is filled'
                or reason == 'The order is rejected')


def test_get_orders_empty(get_all_orders_message):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(get_all_orders_message)
        data = websocket.receive_json()
        assert data['messageType'] == 5
        assert data['message']['orders'] == []


def test_get_orders(place_normal_order_message, get_all_orders_message,
                    temp_db):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_normal_order_message)
        websocket.receive_json()
        websocket.send_text(get_all_orders_message)
        data = websocket.receive_json()
        assert data['messageType'] == 5
        order = data['message']['orders'][0]
        fields = ('creationTime', 'changeTime', 'status',
                  'side', 'price', 'amount', 'instrument', 'uuid')
        assert all(map(order.__contains__, fields))


def test_process_orders(place_normal_order_message, temp_db):
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text(place_normal_order_message)
        websocket.receive_json()
        data = websocket.receive_json()
        assert data['messageType'] == 3
        assert data['message']['orderStatus'] in ('filled', 'rejected')
