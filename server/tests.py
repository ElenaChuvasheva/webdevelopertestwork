from fastapi.testclient import TestClient

from server.app import api

'''
СЦЕНАРИИ ТЕСТОВ

Общее:
Послал хз что - получил ответ, что это не нормальный JSON

Подписки
Подписался - получил правильный ответ
Пытаешься подписаться на несуществующий инструмент - соотв. сообщение
Пытаешься подписаться на то, на что уже подписан - соотв. сообщение
'''
def test_read_main():
    client = TestClient(api)
    response = client.get("/")
    assert response.status_code == 200
