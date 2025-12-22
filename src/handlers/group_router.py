from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State, StateFilter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,  InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.callback_query import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, JOIN_TRANSITION, LEAVE_TRANSITION, PROMOTED_TRANSITION, ChatMemberUpdated
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, KeyboardButton, KeyboardButtonRequestUsers, ReplyKeyboardMarkup
from aiogram.enums.parse_mode import ParseMode
from database.dao import get_groups, get_thread_id
from create_bot import bot


group_router = Router()


class MyCallback(CallbackData, prefix="my"):
    data_name: str
    data: int

class GroupSendMessasgeStage(StatesGroup):
    select_group = State() # выбор группы
    select_user = State() 
    group_content = State() 


def send_msg_kb():
    kb_list = [
        [KeyboardButton(text="👤Выбрать пользователя", request_users=KeyboardButtonRequestUsers(request_id=1, first_name=True, last_name=True, request_username=True))],
        [KeyboardButton(text="🚫Отмена")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите пользователя👇"
    )


def group_start_kb():
    kb_list = [
        [KeyboardButton(text="🚫Отмена")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите группу"
    )



@group_router.message(Command("group"), F.chat.type.in_({"private"}))
async def cmd_group(message: Message, state: FSMContext):
    await state.clear()

    start_content = "<b>Давайте напишем поздравление участнику вашей группы.</b>"
    await message.answer(start_content, reply_markup=group_start_kb(), parse_mode="HTML")

    content = "Выберите группу, в которую хотите отправить поздравление"
    groups = await get_groups()
    builder = InlineKeyboardBuilder()
    for group in groups:  
        chat_member = await bot.get_chat_member(chat_id=group['group_id'], user_id=message.chat.id)
        status = chat_member.status
        if status == ChatMemberStatus.CREATOR or status == ChatMemberStatus.MEMBER or status == ChatMemberStatus.ADMINISTRATOR:
            chat = await bot.get_chat(group['group_id'])
            group_name = chat.title
            builder.row(InlineKeyboardButton(
                text=group_name, callback_data=MyCallback(data_name="data_name", data=group['group_id']).pack())
            )
    await message.answer(content, reply_markup=builder.as_markup())
    await state.set_state(GroupSendMessasgeStage.select_group)
    

@group_router.message(F.text == "🚫Отмена")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    greeting = "Отправка сообщения отменена."
    await message.answer(greeting, reply_markup=ReplyKeyboardRemove())

    
@group_router.callback_query(MyCallback.filter(F.data_name == "data_name"))
async def send_message(callback: CallbackQuery, callback_data: MyCallback, state: FSMContext):
    await callback.answer()
    group_id = callback_data.data
    await state.update_data(group_id=group_id)
    thread_id = await get_thread_id(group_id)
    await state.update_data(thread_id=thread_id)
    content = "Выберите пользователя, которому будет адресована анонимка"
    await callback.message.answer(content, reply_markup=send_msg_kb())
    await state.set_state(GroupSendMessasgeStage.select_user)


@group_router.message(GroupSendMessasgeStage.select_user)
@group_router.message(F.user_shared)
async def handle_user_note_message(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.update_data(user_id=message.users_shared.users[0].user_id)
    await state.update_data(username=message.users_shared.users[0].first_name)
    await state.update_data(username=message.users_shared.users[0].last_name)
    await state.update_data(username=message.users_shared.users[0].username)
    kb_list = [
           [KeyboardButton(text="🚫Отмена")]
    ]
    await message.answer("Введите текст поздравления", reply_markup= ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Введите поздравление здесь👇"
    ))
    await state.set_state(GroupSendMessasgeStage.group_content)



@group_router.message(StateFilter(GroupSendMessasgeStage.group_content))
async def handle_user_note_message(message: Message, state: FSMContext):
    data = await state.get_data()
    congratulation = message.text
    username = data["username"]
    recipient = "не определено"
    if data["username"] != None:
        recipient = f"@{username}"

    content = f"<b>📨Тук-Тук-Тук. Пришлёл почтальон и принёс открытку.</b>\n\n<b>Кому</b>: {recipient}\n<b>Текст открытки</b>\n{congratulation}"
    await bot.send_message(
            chat_id=data["group_id"],
            message_thread_id=data["thread_id"],
            text=content,
            parse_mode=ParseMode.HTML
        )
    success_content = "Поздравление отрправлено"
    await message.answer(success_content, reply_markup=ReplyKeyboardRemove())
    await state.clear()
