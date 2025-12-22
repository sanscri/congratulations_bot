from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from create_bot import logger
from settings import settings

link_router = Router()


@link_router.message(Command("link"))
async def cmd_link(message: Message, state: FSMContext):
    await state.clear()
    link = settings.BOT_LINK + str(message.from_user.id)

    msg = f"<b>💌Получай сообщения прямо сейчас!</b>\n\n🔗Вот твоя персональная ссылка: {link}\n\nОпубликуй её в любой соцсети и получай анонимные сообщения!"
    await message.answer(msg, parse_mode="HTML")


