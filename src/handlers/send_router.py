from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, KeyboardButtonRequestUser, ReplyKeyboardMarkup
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from create_bot import logger, bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

send_router = Router()


class SendMessasgeStage(StatesGroup):
    user = State() 
    content = State()



def send_msg_kb():
    kb_list = [
        [KeyboardButton(text="👤Выбрать пользователя", request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False, request_username=True))],
        [KeyboardButton(text="🚫Отмена")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите пользователя👇"
    )

@send_router.message(Command("send"), F.chat.type.in_({"private"}))
async def cmd_send(message: Message, state: FSMContext):
    await state.clear()

    msg = f"<b>Поздравьте с праздником любого человека, даже если его нет в боте!</b>\n\nВыберите пользователя с помощью кнопки ниже и поздравьте его анонимно."
    await message.answer(msg, reply_markup=send_msg_kb(), parse_mode="HTML")
    await state.set_state(SendMessasgeStage.user)


@send_router.message(F.text == "🚫Отмена")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    greeting = "Отправка сообщения отменена."
    await message.answer(greeting, reply_markup=ReplyKeyboardRemove())

@send_router.message(F.user_shared, SendMessasgeStage.user)
async def on_user_shared(message:Message, state: FSMContext):
    print(
        f"Request {message.user_shared.request_id}. "
        f"User ID: {message.user_shared.user_id}"
    )
    await state.update_data(user_id=message.user_shared.user_id)


    kb_list = [
           [KeyboardButton(text="🚫Отмена")]
    ]
    await message.answer("Введите текст поздравления", reply_markup= ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Введите поздравление здесь👇"
    ))
    await state.set_state(SendMessasgeStage.content)



@send_router.message(SendMessasgeStage.content)
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
        await message.answer("Не получилось отрпавить сообщение пользователю. Возможно пользователя нет в боте.",  reply_markup=ReplyKeyboardRemove())
    except TelegramForbiddenError:
        logger.error(f"Не получилось отправить сообщение пользователю {chat_id}")
        await message.answer("Не получилось отрпавить сообщение пользователю. Возможно пользователь заблокировал чат с ботом.",  reply_markup=ReplyKeyboardRemove())

    await state.clear()
