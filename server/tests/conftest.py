import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy_utils import create_database, drop_database

from server.models import dbase

os.environ['DB_NAME'] = 'test_db'


@pytest.fixture(scope="module")
def temp_db():
    create_database(dbase.TEST_SQLALCHEMY_DATABASE_URL)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
    command.upgrade(alembic_cfg, "head")

    try:
        yield
    finally:
        drop_database(dbase.TEST_SQLALCHEMY_DATABASE_URL)


@pytest.fixture
def non_json_message():
    return 'non json message'


@pytest.fixture
def nonexisting_message_code():
    return r'{"messageType": 10}'


@pytest.fixture
def subscribe_normal_message():
    return r'{"messageType": 1, "message": {"instrument": 1}}'


@pytest.fixture
def subscribe_noexist_instr_message():
    return r'{"messageType": 1, "message": {"instrument": 20}}'


@pytest.fixture
def unsubscribe_noexist_message():
    return (r'{"messageType": 2, "message": '
            r'{"subscriptionId": "0c11e37fc1e1433ea2732c39600ea577"}}')


@pytest.fixture
def unsubscribe_not_uuid_message():
    return (r'{"messageType": 2, "message": '
            r'{"subscriptionId": "not a uuid"}}')


@pytest.fixture
def place_normal_order_message():
    return (r'{"messageType": 3, "message": '
            r'{"instrument": 2, "side": 1, "amount": 3, "price": 20}}')


@pytest.fixture
def place_order_noexist_instr_message():
    return (r'{"messageType": 3, "message": '
            r'{"instrument": 20, "side": 1, "amount": 3, "price": 20}}')


@pytest.fixture
def place_order_noexist_side_message():
    return (r'{"messageType": 3, "message": '
            r'{"instrument": 2, "side": 10, "amount": 3, "price": 20}}')


@pytest.fixture
def place_order_negative_price_message():
    return (r'{"messageType": 3, "message": '
            r'{"instrument": 2, "side": 1, "amount": 3, "price": -20}}')


@pytest.fixture
def place_order_negative_amount_message():
    return (r'{"messageType": 3, "message": '
            r'{"instrument": 2, "side": 1, "amount": -3, "price": 20}}')


@pytest.fixture
def cancel_noexist_order_message():
    return (r'{"messageType": 4, "message": '
            r'{"orderId": "4a01e7fc-4cb5-4718-b563-9d049c6b0272"}}')


@pytest.fixture
def get_all_orders_message():
    return r'{"messageType": 5, "message": {}}'
