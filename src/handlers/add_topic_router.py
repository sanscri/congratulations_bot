from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from create_bot import bot
from database.dao import set_thread

add_topic_router = Router()


@add_topic_router.message(Command("add_topic"), F.chat.type.in_({"supergroup"}))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    thread_id = message.message_thread_id
    group_id = message.chat.id
    await set_thread(group_id, thread_id)
    msg = await message.answer(f"ok")
    await message.delete()
    await msg.delete()
