#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import argparse
import sys
from tg_client import TelegramChannelClient

async def main():
    """Основная функция запуска приложения"""
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Получение статистики из Telegram канала')
    subparsers = parser.add_subparsers(dest='command', help='Команда для выполнения')

    # Парсер для получения сообщений
    messages_parser = subparsers.add_parser('messages', help='Получение последних сообщений')
    messages_parser.add_argument('channel', type=str, help='URL или username канала (@channel или https://t.me/channel)')
    messages_parser.add_argument('-l', '--limit', type=int, default=10, help='Количество последних сообщений (по умолчанию: 10)')
    messages_parser.add_argument('-o', '--output', type=str, help='Путь к файлу для сохранения JSON (по умолчанию: вывод в консоль)')

    # Парсер для получения статистики канала
    stats_parser = subparsers.add_parser('stats', help='Получение статистики канала')
    stats_parser.add_argument('channel', type=str, help='URL или username канала (@channel или https://t.me/channel)')
    stats_parser.add_argument('-l', '--limit', type=int, default=100, help='Максимальное количество сообщений для анализа (по умолчанию: 100)')
    stats_parser.add_argument('-d', '--max-date', type=str, help='Максимальная дата сообщений в формате YYYY-MM-DD (анализируются только сообщения старше этой даты)')
    stats_parser.add_argument('-t', '--only-text', action='store_true', help='Учитывать только сообщения с текстом')
    stats_parser.add_argument('-o', '--output', type=str, help='Путь к файлу для сохранения JSON (по умолчанию: вывод в консоль)')

    # Парсер для получения статистики сообщения
    message_parser = subparsers.add_parser('message', help='Получение статистики конкретного сообщения')
    message_parser.add_argument('url', type=str, help='URL сообщения в формате https://t.me/channel/123')
    message_parser.add_argument('-o', '--output', type=str, help='Путь к файлу для сохранения JSON (по умолчанию: вывод в консоль)')
    
    args = parser.parse_args()
    
    # Инициализация клиента
    client = TelegramChannelClient()
    
    try:
        # Запуск клиента
        await client.start()
        
        # Выполнение соответствующей команды
        if args.command == 'messages':
            messages = await client.get_messages(args.channel, args.limit)
            json_data = client.messages_to_json(messages)
        elif args.command == 'stats':
            stats = await client.get_channel_stats(args.channel, args.limit, args.max_date, args.only_text)
            json_data = client.messages_to_json(stats)
        elif args.command == 'message':
            stats = await client.get_message_stats(args.url)
            json_data = client.messages_to_json(stats)
        else:
            parser.print_help()
            return 1
        
        # Вывод результата
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_data)
            print(f'Результат сохранен в файл: {args.output}')
        else:
            print(json_data)
            
    except Exception as e:
        print(f'Ошибка: {e}', file=sys.stderr)
        return 1
    finally:
        # Закрытие соединения
        await client.stop()
        
    return 0

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 