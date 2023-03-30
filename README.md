# Симулятор биржи

Можно отправить заявку (ордер) на покупку или продажу какого либо актива. 
Получив заявку, биржа ищет встречную заявку для заключения сделки.
Заявка в итоге может быть исполнена, отклонена или же ее можно отменить самому.
Исполнение заявок и поток котировок симулируются как случайные события.

Биржа (сервер) поддерживает подключение по протоколу `websocket` нескольких клиентов одновременно, дает им возможность:

* получать информацию о всех своих заявках
* получать текущие котировки
* выставлять заявки
* отменять активные заявки

## Технологии
Python 3.10, FastAPI, Pytest, SQLAlchemy, Alembic, Docker, PostgreSQL

## API
Все сообщения имеют общий `JSON` формат:
    
    {
        "messageType": <integer>,
        "message": <object>
    }

В зависимости от типа сообщения (`messageType`) само сообщение (`message`) должно иметь конкретный формат, например:

**SubscribeMarketData** `messageType=1`
    
    | Field          | Type     | Comment                                                            |
    |----------------|----------|--------------------------------------------------------------------|
    | **instrument** | integer  | Идентификатор инструмента на котировки которого запрошена подписка |

Пример:
    
        {"instrument": 12}
    
В случае успешной подписки, сервер отвечает сообщением **SuccessInfo**, где поле `message` будет содержать идентификатор подписки:
    
        {"subscriptionId": <string:UUID>}
    
И далее при каждом изменении котировок, сервер будет присылать сообщение **MarketDataUpdate**.
    
В случае какой-либо ошибки, сервер отвечает сообщением **ErrorInfo**, где поле `message` будет содержать описание причины ошибки:
    
        {"reason": <string>}
    
Чтобы отменить подписку, нужно отправить сообщение **UnsubscribeMarketData**.

## Локальный запуск проекта
Для запуска подойдёт Docker 20.10.21, Docker Compose 2.12.2.  
Клонируйте репозиторий:
```
git@github.com:ElenaChuvasheva/webdevelopertestwork.git
```
Перейдите в папку webdevelopertestwork/server:
```
cd webdevelopertestwork\server
```
Создайте в этой папке файл .env с переменными окружения для работы с базой данных, значения имени пользователя и пароля даны для примера:
```
DB_NAME=exchange
DB_HOST=db
DB_PORT=5432
POSTGRES_USER=root
POSTGRES_DB=exchange
POSTGRES_PASSWORD=root
```
В этой же папке запустите команду сборки контейнеров:
```
docker-compose up
```
Запустите миграции:
```
docker-compose exec -T web alembic upgrade head
```
Проект с минимальным интерфейсом откроется по адресу http://127.0.0.1:8000/ . 

## Примеры сообщений
### Подписка на инструмент
Запрос:
```
{
    "messageType": 1,
    "message": {"instrument": 1}
}
```
Ответ:
```
{"messageType": 1, "message": {"subscriptionId": "46a122ae-f7ae-492e-900e-c9166d673c4d"}}
```
### Отписка от инструмента
```
{
    "messageType": 2,
    "message": {"subscriptionId": "0c11e37fc1e1433ea2732c39600ea577"}
}
```
Ответ:
```
{"messageType": 1, "message": {"subscriptionId": "0c11e37fc1e1433ea2732c39600ea577"}}
```
### Размещение заявки
```
{
    "messageType": 3,
    "message": {"instrument": 2, "side": 1, "amount": 3, "price": 20}
}
```
Ответ:
```
{"messageType": 3, "message": {"orderId": "85693ea2-2d9c-4d25-b9e3-105194d1a7fd", "orderStatus": "active"}}
```
### Сообщение с результатом обработки заявки
```
{"messageType": 3, "message": {"orderId": "85693ea2-2d9c-4d25-b9e3-105194d1a7fd", "orderStatus": "filled"}}
```
