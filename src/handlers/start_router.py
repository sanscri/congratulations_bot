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

class MyCallback(CallbackData, prefix="my"):
    foo: str
    bar: int

class SendMessasgeStage(StatesGroup):
    group = State() # выбор группы
    group_content = State()  # Ожидаем любое сообщение от пользователя
    user_content = State()  # Ожидаем любое сообщение от пользователя
    user = State()  # Юзер пользователя

def main_kb():
    kb_list = [
        [KeyboardButton(text="💬Отправить анонимку")],
        [KeyboardButton(text="🔗 Получить ссылку")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )

def cancel_kb():
    kb_list = [
        [KeyboardButton(text="Отмена")],
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
        await message.answer(greeting, reply_markup=main_kb())
    else:
        await state.update_data(user_id=payload)
        await message.answer("Введите текст поздравления", reply_markup=cancel_kb())
        await state.set_state(SendMessasgeStage.user_content)



@start_router.message(CommandStart(), F.chat.type.in_({"group", "supergroup"}))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
  
    greeting = "Бот предназначен для поздравлений!"
    await message.answer(greeting)


@start_router.message(F.text == "🔗 Получить ссылку")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    link = settings.BOT_LINK + str(message.chat.id)
    msg = f"Вот твоя персональная ссылка: {link}"
    await message.answer(msg, reply_markup=main_kb())


@start_router.message(F.text == "Отмена")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    greeting = "Приветствую! Здесь вы можете отправить поздравление другому человеку!"
    await message.answer(greeting, reply_markup=main_kb())


@start_router.message(F.text == "💬Отправить анонимку")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

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
                text=group_name, callback_data=MyCallback(foo="group", bar=group['group_id']).pack())
            )
    await message.answer(content, reply_markup=builder.as_markup())
    await state.set_state(SendMessasgeStage.group)
    


    
@start_router.callback_query(MyCallback.filter(F.foo == "group"))
async def send_message(callback: CallbackQuery, callback_data: MyCallback, state: FSMContext):
    await callback.answer()
    group_id = callback_data.bar
    await state.update_data(group_id=group_id)
    thread_id = await get_thread_id(group_id)
    await state.update_data(thread_id=thread_id)
    content = "Напешите тег пользователя, которому будет адресована анонимка"
    builder = ReplyKeyboardBuilder()
    #builder.row(KeyboardButton(text="Выбрать пользователя", request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False, request_username=True)))
    builder.row(
      KeyboardButton(text="Отмена"))
    await callback.message.answer(content, reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(SendMessasgeStage.user)


@start_router.message(SendMessasgeStage.user)
async def handle_user_note_message(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Введите текст поздравления")
    await state.set_state(SendMessasgeStage.group_content)


'''
@start_router.message(F.user_shared)
async def on_user_shared(message:Message, state: FSMContext):
    print(
        f"Request {message.user_shared.request_id}. "
        f"User ID: {message.user_shared.user_id}"
    )
    await state.update_data(user_id=message.user_shared.user_id)
    await state.update_data(username=message.user_shared.username)

    kb_list = [
           [KeyboardButton(text="Назад")]
    ]
    await message.answer("Введите поздравление", reply_markup= ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    ))
    await state.set_state(SendMessasgeStage.content)
'''


@start_router.message(SendMessasgeStage.group_content)
async def handle_user_note_message(message: Message, state: FSMContext):
    data = await state.get_data()
    congratulation = message.text
    username = data["username"]
    content = f"Туки-Туки. Пришла анонимка.\n<b>Кому</b>: {username}\n<b>Текст</b>\n{congratulation}"
    await bot.send_message(
            chat_id=data["group_id"],
            message_thread_id=data["thread_id"],
            text=content,
            parse_mode=ParseMode.HTML,
            reply_markup=main_kb()
        )
    success_content = "Анонимка отрпавлена"
    await message.answer(success_content, reply_markup=main_kb())
    await state.clear()



@start_router.message(SendMessasgeStage.user_content)
async def handle_user_note_message(message: Message, state: FSMContext):
    data = await state.get_data()
    congratulation = message.text
    try:
        await bot.send_message(
            chat_id=data["user_id"],
            text=congratulation,
            parse_mode=ParseMode.HTML,
            reply_markup=main_kb()
            )
        success_content = "Анонимка отрпавлена"
        await message.answer(success_content, reply_markup=main_kb())
    except TelegramBadRequest:
        logger.error(f"Не получилось отправить сообщение пользователю {data["user_id"]}")
        await message.answer("Не получилось отрпавить сообщение пользователю. Возможно пользователя нет в боте.")
    except TelegramForbiddenError:
        logger.error(f"Не получилось отправить сообщение пользователю {data["user_id"]}")
        await message.answer("Не получилось отрпавить сообщение пользователю. Возможно пользователь заблокировал чат с ботом.")

    await state.clear()

@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_bot_joined_chat(update: ChatMemberUpdated):
    if update.new_chat_member.user.id == bot.id  and update.new_chat_member.status == "member":
        await set_group(update.chat.id)
        await bot.send_message(chat_id=update.chat.id, text=f"Бот добавлен в {update.chat.title}")
        logger.info(f"Бот добавлен в чат ID: {update.chat.id}")
        logger.info(f"Тип чата: {update.chat.type}")
        
@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_bot_joined_chat(update: ChatMemberUpdated):
    if update.new_chat_member.user.id == bot.id  and update.new_chat_member.status == "member":
        await set_group(update.chat.id)
        await bot.send_message(chat_id=update.chat.id, text=f"Бот стал администратором в {update.chat.title}")
        logger.info(f"Бот добавлен в чат ID: {update.chat.id}")
        logger.info(f"Тип чата: {update.chat.type}")

@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION))
async def on_bot_removed_chat(update):
    if update.new_chat_member.user.id == bot.id and update.new_chat_member.status == "left":
        await delete_group(update.chat.id)
        logger.info(f"Бот удалили из чата ID: {update.chat.id}")

