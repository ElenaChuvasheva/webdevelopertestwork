# Бэкенд для симулятора биржи

Можно отправить заявку (ордер) на покупку или продажу какого-либо актива. 
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

## Локальный запуск проекта
Для запуска подойдёт Docker 20.10.21, Docker Compose 2.12.2.  
Клонируйте репозиторий:
```
git clone git@github.com:ElenaChuvasheva/webdevelopertestwork.git
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
docker-compose exec web alembic upgrade head
```
Проект с минимальным интерфейсом откроется по адресу http://127.0.0.1:8000/ .  
Запуск тестов:
```
docker-compose exec web pytest
```

## API
### Структура сообщений
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

### Примеры сообщений
#### Подписка на инструмент
Запрос:
```
{
    "messageType": 1,
    "message": {"instrument": 1}
}
```
Ответ:
```
{
    "messageType": 1,
    "message": {"subscriptionId": "46a122ae-f7ae-492e-900e-c9166d673c4d"}
}
```
#### Отписка от инструмента
Запрос:
```
{
    "messageType": 2,
    "message": {"subscriptionId": "0c11e37fc1e1433ea2732c39600ea577"}
}
```
Ответ:
```
{
    "messageType": 1,
    "message": {"subscriptionId": "0c11e37fc1e1433ea2732c39600ea577"}
}
```
#### Размещение заявки
Запрос:
```
{
    "messageType": 3,
    "message": {"instrument": 2, "side": 1, "amount": 3, "price": 20}
}
```
Ответ:
```
{
    "messageType": 3,
    "message": {"orderId": "85693ea2-2d9c-4d25-b9e3-105194d1a7fd", "orderStatus": "active"}
}
```
#### Сообщение с результатом обработки заявки
Ответ:
```
{
    "messageType": 3,
    "message": {"orderId": "85693ea2-2d9c-4d25-b9e3-105194d1a7fd", "orderStatus": "filled"}
}
```
#### Отмена заявки
Запрос:
```
{
    "messageType": 4,
    "message": {"orderId": "4a01e7fc-4cb5-4718-b563-9d049c6b0272"}
}
```
Ответ:
```
{
    "messageType": 3,
    "message": {"orderId": "4a01e7fc-4cb5-4718-b563-9d049c6b0272", "orderStatus": "cancelled"}
}
```
#### Запрос всех своих заявок
Запрос:
```
{
    "messageType": 5,
    "message": {}
}
```
Ответ:
```
{
    "messageType": 5,
    "message": {
                "orders": 
                         [        
                              {    
                                   "creationTime": "2023-03-30T11:34:01.456227",
                                   "changeTime": "2023-03-30T11:34:22.550857",
                                   "status": "rejected",  "side": "buy",
                                   "price": 30, "amount": 2,
                                   "instrument": "EUR/RUB",
                                   "uuid": "8b4d17ca-db5b-4e44-808f-affbbb7656ab"
                              },
                              {    
                                   "creationTime": "2023-03-30T11:34:12.548832",
                                   "changeTime": "2023-03-30T11:34:12.548839",
                                   "status": "active", "side": "sell",
                                   "price": 20, "amount": 3,
                                   "instrument": "EUR/RUB",
                                   "uuid": "75c936d0-8ae1-4f20-9510-97f557b679d1"
                              }
                         ]
               }
}
```
#### Сообщение об изменении котировок
Ответ:
```
{
    "messageType": 4,
    "message": {    
                "subscriptionId": "634905d5-13f0-4cd6-8b62-1b5a24227029", "instrument": "USD/RUB",
                "quotes": 
                         [    
                              {    
                                   "bid": 32.540866044239536, "offer": 32.768034070299606,
                                   "minAmount": 30.97320671154219,
                                   "maxAmount": 36.668907735148736,
                                   "timestamp": "2023-03-30T11:42:51.229960"
                              },
                              {
                                   "bid": 35.30738166239448, "offer": 37.97198429333178,
                                   "minAmount": 34.039151483095445,
                                   "maxAmount": 38.928840172008506,
                                   "timestamp": "2023-03-30T11:43:01.231579"
                              }
                         ]
               }
}
```
#### Сообщение об ошибке
Ответ:
```
{
    "messageType": 2,
    "message": {"reason": "The message is not a valid JSON"}
}
```
