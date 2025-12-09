from aiogram import Router, F

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, KeyboardButtonRequestUsers
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, ChatMemberUpdated
from create_bot import bot
from database.dao import set_user
from create_bot import logger
start_router = Router()


def main_kb():
    kb_list = [
        [KeyboardButton(text="Отправить анонимку")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await set_user(tg_id=message.from_user.id)
    
    greeting = "Приветствую! Здесь вы можете отправить поздравление другому человеку!"
    await message.answer(greeting, reply_markup=main_kb())


@start_router.message(F.text == "Отправить анонимку")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    builder = ReplyKeyboardMarkup(resize_keyboard=True)
    request_user_button = KeyboardButton(text="Выбрать пользователя", request_user=KeyboardButtonRequestUsers(request_id=1, user_is_bot=False))
    builder.add(request_user_button)
    request_user_button = KeyboardButton(text="Назад")
    builder.add(request_user_button)
    greeting = "Приветствую! Здесь вы можете отправить поздравление другому человеку!"
    await message.answer(greeting, reply_markup=main_kb())


@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
async def on_bot_joined_chat(update: ChatMemberUpdated):
    #print(update.from_user.id, bot.id)
    #if update.from_user.id == bot.id:
     await bot.send_message(chat_id=id, text=f"Бот добавлен в {update.chat.title}, username: {update.chat.username}")
     logger.info(f"Бот добавлен в чат ID: {update.chat.id}")
     logger.info(f"Тип чата: {update.chat.type}")
        

@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_NOT_MEMBER))
async def on_bot_removed_chat(update):
    if update.from_user.id == bot.id:
        print(f"Бот удалили из чата ID: {update.chat.id}")

