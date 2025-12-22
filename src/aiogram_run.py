import asyncio
from create_bot import bot, dp, admins
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

from database.base import create_tables
from handlers.group_router import group_router
from handlers.send_router import send_router
from handlers.link_router import link_router
from handlers.start_router import start_router
from handlers.add_topic_router import add_topic_router
from handlers.help_router import help_router
# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    private_commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='group', description='Отправить поздравление в группу'),
                BotCommand(command='send', description='Отправить анонимку'),
                BotCommand(command='link', description='Ссылка'),
                BotCommand(command='help', description='Помощь')]
    await bot.set_my_commands(private_commands, BotCommandScopeAllPrivateChats())
    common_commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='link', description='Ссылка'),
                BotCommand(command='help', description='Помощь')]
    await bot.set_my_commands(common_commands, BotCommandScopeAllGroupChats())


# Функция, которая выполнится когда бот запустится
async def start_bot():
    await set_commands()
    await create_tables()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except:
        pass


async def main():
    # регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(link_router)
    dp.include_router(group_router)
    dp.include_router(send_router)
    dp.include_router(help_router)
    dp.include_router(add_topic_router)
    # регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())