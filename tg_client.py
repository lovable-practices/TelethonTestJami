#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import csv
import asyncio
from datetime import datetime, timezone
from telethon import TelegramClient
from dotenv import load_dotenv
from typing import List, Dict, Any, Union, Optional, Tuple

# Загрузка переменных окружения
load_dotenv()

class TelegramChannelClient:
    """Класс для работы с Telegram API через библиотеку Telethon"""
    
    def __init__(self):
        """Инициализация клиента Telethon с данными из переменных окружения"""
        api_id = int(os.getenv('TELEGRAM_API_ID'))
        api_hash = os.getenv('TELEGRAM_API_HASH')
        session_name = os.getenv('TELEGRAM_SESSION_NAME', 'tg_session')
        
        self.client = TelegramClient(session_name, api_id, api_hash)
        
    async def start(self):
        """Запуск клиента"""
        await self.client.start()
        
    async def stop(self):
        """Остановка клиента"""
        await self.client.disconnect()
        
    async def get_messages(self, channel_url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получение последних сообщений из указанного канала
        
        Args:
            channel_url: URL или username канала (@channel или https://t.me/channel)
            limit: Количество последних сообщений для получения
            
        Returns:
            List[Dict]: Список сообщений в формате словаря
        """
        # Нормализуем URL канала
        if channel_url.startswith('https://t.me/'):
            channel_username = channel_url.split('/')[-1]
        elif channel_url.startswith('@'):
            channel_username = channel_url[1:]
        else:
            channel_username = channel_url
            
        # Получаем сообщения
        messages = []
        async for message in self.client.iter_messages(channel_username, limit=limit):
            # Преобразуем сообщение в словарь
            message_dict = {
                'id': message.id,
                'date': message.date.isoformat(),
                'text': message.text,
                'sender_id': message.sender_id,
                'has_media': message.media is not None,
                'views': getattr(message, 'views', None),
                'forwards': getattr(message, 'forwards', None),
                'reply_to_msg_id': message.reply_to_msg_id,
            }
            messages.append(message_dict)
            
        return messages
        
    def messages_to_json(self, messages: List[Dict[str, Any]]) -> str:
        """
        Преобразование списка сообщений в JSON-строку
        
        Args:
            messages: Список сообщений
            
        Returns:
            str: JSON-строка с сообщениями
        """
        return json.dumps(messages, ensure_ascii=False, indent=2)

    async def get_channel_stats(self, channel_url: str, limit: int = 100, max_date: Optional[str] = None, only_with_text: bool = False) -> Dict[str, Any]:
        """
        Получение статистики канала
        
        Args:
            channel_url: URL или username канала (@channel или https://t.me/channel)
            limit: Максимальное количество сообщений для анализа
            max_date: Максимальная дата сообщений в формате YYYY-MM-DD (анализируются только сообщения старше этой даты)
            only_with_text: Если True, учитываются только сообщения с текстом
            
        Returns:
            Dict: Статистика канала
        """
        # Нормализуем URL канала
        if channel_url.startswith('https://t.me/'):
            channel_username = channel_url.split('/')[-1]
        elif channel_url.startswith('@'):
            channel_username = channel_url[1:]
        else:
            channel_username = channel_url

        # Преобразуем дату в datetime объект с часовым поясом UTC
        max_date_obj = None
        if max_date:
            try:
                # Создаем datetime с часовым поясом UTC
                max_date_obj = datetime.strptime(max_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError:
                raise ValueError("Неверный формат даты. Используйте формат YYYY-MM-DD")

        # Получаем сообщения
        total_views = 0
        total_forwards = 0
        message_count = 0
        messages = []

        # Получаем сообщения старше указанной даты
        async for message in self.client.iter_messages(channel_username, limit=None):
            # Пропускаем сообщения новее указанной даты
            if max_date_obj and message.date > max_date_obj:
                continue
                
            # Пропускаем сообщения без текста, если включен фильтр
            if only_with_text and not message.text:
                continue
                
            # Если достигли лимита сообщений, прекращаем сбор
            if message_count >= limit:
                break

            views = getattr(message, 'views', 0)
            forwards = getattr(message, 'forwards', 0)

            total_views += views
            total_forwards += forwards
            message_count += 1

            messages.append({
                'id': message.id,
                'date': message.date.isoformat(),
                'text': message.text,
                'views': views,
                'forwards': forwards
            })

        # Рассчитываем средние значения
        avg_views = total_views / message_count if message_count > 0 else 0
        avg_forwards = total_forwards / message_count if message_count > 0 else 0

        return {
            'total_messages_analyzed': message_count,
            'total_views': total_views,
            'total_forwards': total_forwards,
            'average_views': round(avg_views, 2),
            'average_forwards': round(avg_forwards, 2),
            'messages': messages
        }

    async def get_message_stats(self, message_url: str) -> Dict[str, Any]:
        """
        Получение статистики конкретного сообщения
        
        Args:
            message_url: URL сообщения в формате https://t.me/channel/123
            
        Returns:
            Dict: Статистика сообщения
        """
        # Извлекаем username канала и ID сообщения из URL
        parts = message_url.split('/')
        if len(parts) < 5:
            raise ValueError("Неверный формат URL сообщения. Используйте формат https://t.me/channel/123")

        channel_username = parts[3]
        message_id = int(parts[4])

        # Получаем сообщение
        message = await self.client.get_messages(channel_username, ids=message_id)
        if not message:
            raise ValueError("Сообщение не найдено")

        return {
            'id': message.id,
            'date': message.date.isoformat(),
            'text': message.text,
            'views': getattr(message, 'views', 0),
            'forwards': getattr(message, 'forwards', 0),
            'has_media': message.media is not None,
            'reactions': getattr(message, 'reactions', None)
        }

    async def export_channel_csv(self, channel_url: str, output_path: str, limit: Optional[int] = None) -> None:
        """Экспорт сообщений канала в CSV-файл.

        Args:
            channel_url: URL или username канала.
            output_path: Путь для сохранения CSV-файла.
            limit: Ограничение количества экспортируемых сообщений. ``None`` экспортирует всю историю.
        """
        # Нормализуем URL канала
        if channel_url.startswith('https://t.me/'):
            channel_username = channel_url.split('/')[-1]
        elif channel_url.startswith('@'):
            channel_username = channel_url[1:]
        else:
            channel_username = channel_url

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'date', 'text', 'views', 'forwards'])

            count = 0
            async for message in self.client.iter_messages(channel_username, limit=limit):
                writer.writerow([
                    message.id,
                    message.date.isoformat(),
                    (message.text or '').replace('\n', ' ').replace('\r', ''),
                    getattr(message, 'views', None),
                    getattr(message, 'forwards', None)
                ])
                count += 1
                if count % 100 == 0:
                    await asyncio.sleep(1)
