import asyncio
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time
from typing import Dict

from environs import Env

env = Env()

env.read_env()

# Настройки
GROUP_ID = int(env("GROUP_ID"))  # Число (без кавычек)
TOKEN = env("TOKEN_GOD")  # Ключ доступа из настроек группы

# Инициализация VK API
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# Ожидающие проверки пользователи {user_id: (timestamp, captcha_answer)}
pending_users: Dict[int, tuple] = {}


# Асинхронная отправка сообщения
async def send_message(user_id: int, message: str):
    vk.messages.send(user_id=user_id, message=message, random_id=0)


# Проверка капчи
async def check_captcha(user_id: int, captcha_answer: str) -> bool:
    # Здесь можно усложнить проверку (например, рандомные вопросы)
    return captcha_answer.strip() == "4"


# Обработка нового участника
async def handle_new_member(user_id: int):
    await send_message(
        user_id, "Привет! Докажи, что ты не бот. Ответь на вопрос: Сколько будет 2+2?"
    )
    # pending_users[user_id] = (time.time(), "4")  # (timestamp, правильный ответ)

    # if user_id in pending_users:
    #     await send_message(user_id, "Время вышло! Вы удалены из группы.")
    #     vk.groups.removeUser(group_id=GROUP_ID, user_id=user_id)
    #     del pending_users[user_id]


# Обработка сообщений от пользователей
async def handle_user_message(user_id: int, message: str):
    if user_id in pending_users:
        _, correct_answer = pending_users[user_id]
        if await check_captcha(user_id, message):
            await send_message(user_id, "✅ Проверка пройдена! Добро пожаловать!")
            del pending_users[user_id]
        else:
            await send_message(user_id, "❌ Неверно! Попробуй еще раз.")


# Основной цикл бота
async def main():
    print("Бот запущен!")

    for event in longpoll.listen():
        # if event.type == VkBotEventType.GROUP_JOIN:
        #     user_id = event.object.user_id
        #     asyncio.create_task(handle_new_member(user_id))

        # elif event.type == VkBotEventType.MESSAGE_NEW:
        #     user_id = event.object.from_id
        #     message = event.object.text
        #     asyncio.create_task(handle_user_message(user_id, message))
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.message.from_id
            message = event.message.text
            print(user_id, message)
            asyncio.create_task(
                send_message(
                    user_id,
                    "Привет! Докажи, что ты не бот. Ответь на вопрос: Сколько будет 2+2?",
                )
            )


if __name__ == "__main__":
    asyncio.run(main())
