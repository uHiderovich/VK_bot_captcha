import random, asyncio
from typing import Dict

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from environs import Env

env = Env()
env.read_env()

# Настройки
GROUP_ID = int(env("GROUP_ID"))
TOKEN = env("TOKEN")

# Инициализация VK API
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

pending_users: Dict[int, tuple] = {}


def generate_captcha():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    return f"{a} + {b}", str(a + b)


def sync_send_message(user_id: int, message: str):
    """Синхронная отправка сообщения"""
    vk.messages.send(user_id=user_id, message=message, random_id=get_random_id())


async def send_message(user_id: int, message: str):
    """Асинхронная обёртка для отправки сообщения"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_send_message, user_id, message)


async def handle_new_member(user_id: int):
    question, answer = generate_captcha()
    await asyncio.create_task(
        send_message(
            user_id,
            f"Подтвердите, что вы не бот. Решите пример: {question} = ?",
        )
    )
    pending_users[user_id] = answer


async def handle_user_message(user_id: int, message: str):
    if user_id in pending_users:
        _, correct_answer = pending_users[user_id]
        if message.strip() == correct_answer:
            await send_message(user_id, "✅ Проверка пройдена! Добро пожаловать!")
            del pending_users[user_id]
        else:
            await send_message(user_id, "❌ Неверно! Попробуй еще раз.")


async def main():
    print("Бот запущен!")

    # Запускаем фоновую задачу для проверки ожидающих пользователей
    # asyncio.create_task(check_pending_users())

    for event in longpoll.listen():
        if event.type == VkBotLongPoll.EVENT_GROUP_JOIN:
            user_id = event.message.user_id
            await asyncio.create_task(handle_new_member(user_id))
        elif event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.message.from_id
            message = event.message.text
            await asyncio.create_task(handle_user_message(user_id, message))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
