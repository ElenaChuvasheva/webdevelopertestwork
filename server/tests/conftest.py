import pytest


@pytest.fixture
def non_json_message():
    return 'non json message'

@pytest.fixture
def subscribe_normal_message():
    return r'{"messageType": 1,"message": {"instrument": 2}}'

@pytest.fixture
def subscribe_noexist_instr_message():
    return r'{"messageType": 1,"message": {"instrument": 20}}'

@pytest.fixture
def unsubscribe_noexist_message():
    return r'{"messageType": 2,"message": {"subscriptionId": "0c11e37fc1e1433ea2732c39600ea577"}}'

