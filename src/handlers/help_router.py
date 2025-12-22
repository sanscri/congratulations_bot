from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,  InlineKeyboardButton, InlineKeyboardMarkup

from settings import settings

help_router = Router()

def main_help_kb():
    kb_list = [
        [InlineKeyboardButton(text="Техподдержка", url=str(settings.SUPPORT_LINK))],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=kb_list
        )

def back_help_kb():
    kb_list = [
        [InlineKeyboardButton(text="Назад", callback_data="help_back")],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=kb_list
    )


@help_router.message(Command("help"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    help_text='''
<b>"Праздник к нам приходит!"</b>

Бот позволяет писать писать поздравления c праздниками как в личные чаты, так и в группы.

/group - команда, которая позволяет писать поздравления в определённую группу, в которой вы общаетесь со своими друзьями. Если у вас - суппергруппа, то напишите команду /add_topic в теме, в которую должны отправляться сообщения.

/send - С помощью этой команды вы можете написать анонимное поздравление любому пользователю, который уже использует данный бот.

/link - ссылка, которую вы можете написать в любых соцсетях. Благодаря ей другие пользователи смогут поздравить вас с праздниками.

/help - Помощь с функционалом.

Вы можете обратиться в техподдержку, если вы хотите сообщить о баге или предложить новый функионал.
'''

    await message.answer(help_text, reply_markup=main_help_kb())