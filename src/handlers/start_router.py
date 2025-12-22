from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.types.callback_query import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, JOIN_TRANSITION, LEAVE_TRANSITION, PROMOTED_TRANSITION, ChatMemberUpdated
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from create_bot import bot
from database.dao import get_groups, get_thread_id, set_user, set_group, delete_group
from create_bot import logger
from settings import settings

start_router = Router()


class SendMessasgeStage(StatesGroup):
    message_by_link = State() # выбор группы



def cancel_kb():
    kb_list = [
        [KeyboardButton(text="🚫Отмена")],
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )

@start_router.message(CommandStart(), F.chat.type.in_({"private"}))
async def cmd_start(message: Message, command: CommandObject,  state: FSMContext):
    await state.clear()
    user = await set_user(tg_id=message.from_user.id)
    payload = command.args
    if not payload:
        greeting = "Приветствую! Здесь вы можете отправить поздравление другому человеку!"
        await message.answer(greeting, reply_markup=ReplyKeyboardRemove())
    else:
        await state.update_data(user_id=payload)
        await message.answer("Введите текст поздравления", reply_markup=cancel_kb())
        await state.set_state(SendMessasgeStage.message_by_link)


@start_router.message(F.text == "🚫Отмена")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    greeting = "Отправка сообщения отменена."
    await message.answer(greeting, reply_markup=ReplyKeyboardRemove())


@start_router.message(CommandStart(), F.chat.type.in_({"group", "supergroup"}))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
  
    greeting = "Бот предназначен для поздравлений!"
    await message.answer(greeting)


@start_router.message(SendMessasgeStage.message_by_link)
async def handle_user_note_message(message: Message, state: FSMContext):
    data = await state.get_data()
    congratulation = f"📨Вам пришло анонимное поздравление!\n{message.text}"
    chat_id = data["user_id"]
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=congratulation,
            parse_mode=ParseMode.HTML,
            )
        success_content = "Анонимное поздравление отпрвлено"
        await message.answer(success_content, reply_markup=ReplyKeyboardRemove())
    except TelegramBadRequest:
        logger.error(f"Не получилось отправить сообщение пользователю {chat_id}")
        await message.answer("Не получилось отправить сообщение пользователю. Возможно пользователя нет в боте.",  reply_markup=ReplyKeyboardRemove())
    except TelegramForbiddenError:
        logger.error(f"Не получилось отправить сообщение пользователю {chat_id}")
        await message.answer("Не получилось отправить сообщение пользователю. Возможно пользователь заблокировал чат с ботом.",  reply_markup=ReplyKeyboardRemove())

    await state.clear()


@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_bot_joined_chat(update: ChatMemberUpdated):
    if update.new_chat_member.user.id == bot.id  and update.new_chat_member.status == "member":
        await set_group(update.chat.id)
        await bot.send_message(chat_id=update.chat.id, text=f"Вы добавили поздравлятора в беседу.\nПожалуйста, сделайте его администратором.")
        logger.info(f"Бот добавлен в чат ID: {update.chat.id}")
        logger.info(f"Тип чата: {update.chat.type}")
    if update.new_chat_member.user.id == bot.id  and update.new_chat_member.status == "administrator":
        await set_group(update.chat.id)
        await bot.send_message(chat_id=update.chat.id, text=f"Вы добавили поздравлятора в беседу.\n")
        logger.info(f"Бот добавлен в чат ID: {update.chat.id}")
        logger.info(f"Тип чата: {update.chat.type}")
        

@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION))
async def on_bot_removed_chat(update):
    if update.new_chat_member.user.id == bot.id and update.new_chat_member.status == "left":
        await delete_group(update.chat.id)
        logger.info(f"Бот удалили из чата ID: {update.chat.id}")
