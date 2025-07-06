from vkbottle.bot import Bot, Message
from environs import Env

env = Env()
env.read_env()

bot = Bot(token="token")


@bot.on.chat_message()
async def echo(message: Message):
    await message.answer(message.text)


def main():
    print("Бот запущен!")
    bot.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Бот остановлен")
