# Telegram Channel Message Fetcher

Приложение для получения сообщений и статистики из Telegram каналов с использованием Telethon API.

## Функциональность

- Получение последних сообщений из Telegram канала
- Анализ статистики канала (средние просмотры, репосты) - анализ ведется от новых сообщений к старым
- Фильтрация сообщений по наличию текста
- Получение статистики конкретного сообщения
- Преобразование данных в JSON формат
- Возможность вывода результата в консоль или сохранения в файл
- Экспорт сообщений канала в CSV

## Установка

### Предварительные требования

- Python 3.7 или выше
- Учетная запись Telegram
- API ID и API Hash от Telegram ([получить здесь](https://my.telegram.org/apps))

### Шаги установки

1. Клонировать репозиторий:
```bash
git clone <url-репозитория>
cd <имя-папки-репозитория>
```

2. Создать и активировать виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/MacOS
# или
.venv\Scripts\activate  # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Настроить переменные окружения:
```bash
cp .env.example .env
```
Затем отредактировать файл `.env`, вставив свои данные API Telegram.

## Использование

### Получение последних сообщений

```bash
python main.py messages @channel_name
```

или

```bash
python main.py messages https://t.me/channel_name
```

Для приватных чатов используйте название чата:

```bash
python main.py messages "Название чата"
```

Дополнительные параметры:
- Указание количества сообщений:
```bash
python main.py messages @channel_name -l 20
```

### Получение статистики канала

```bash
python main.py stats @channel_name
```

Для приватных чатов можно указать название чата:

```bash
python main.py stats "Название чата"
```

Дополнительные параметры:
- Указание количества сообщений для анализа:
```bash
python main.py stats @channel_name -l 50
```
- Указание максимальной даты сообщений (анализируются только сообщения старше этой даты):
```bash
python main.py stats @channel_name -d 2023-01-01
```
- Учет только сообщений с текстом:
```bash
python main.py stats @channel_name -t
```

### Экспорт сообщений канала в CSV

```bash
python main.py export @channel_name -o messages.csv
```

Для приватных чатов укажите название чата:

```bash
python main.py export "Название чата" -o messages.csv
```

В режиме отладки можно экспортировать только первые 100 сообщений:

```bash
python main.py export @channel_name -o messages.csv --DEBUG
```

### Получение статистики конкретного сообщения

```bash
python main.py message https://t.me/channel_name/123
```

### Общие параметры

Для всех команд доступны следующие параметры:
- Сохранение результата в файл:
```bash
python main.py <command> <args> -o result.json
```

- Получение справки:
```bash
python main.py --help
```

## Примечания

При первом запуске приложение попросит вас авторизоваться в Telegram. Для этого следуйте инструкциям в консоли (ввод номера телефона и кода подтверждения).

После успешной авторизации создается файл сессии (по умолчанию `tg_session.session`), и в последующих запусках авторизация не требуется.

## Лицензия

MIT 