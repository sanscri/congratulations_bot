from pstats import Stats
from create_bot import logger
from .base import connection
from .models import Group, User
from sqlalchemy import inspect, select, update
from typing import List, Dict, Any, Optional
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID


@connection
async def set_user(session, tg_id: int) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))

        if not user:
            new_user = User(id=tg_id)
            session.add(new_user)
            await session.commit()
            logger.info(f"Зарегистрировал пользователя с ID {tg_id}!")
            return None
        else:
            logger.info(f"Пользователь с ID {tg_id} найден!")
            return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        await session.rollback()




@connection
async def set_group(session, group_id: int) -> Optional[User]:
    try:
        group = await session.scalar(select(Group).filter_by(group_id=group_id))

        if not group:
            new_group = Group(group_id=group_id)
            session.add(new_group)
            await session.commit()
            logger.info(f"Зарегистрировал  группу с ID {group_id}!")
            return None
        else:
            logger.info(f"Группы с ID {group_id} найденв!")
            return group
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении группы: {e}")
        await session.rollback()


@connection
async def get_thread_id(session, group_id: int) -> int:
    try:
        group = await session.scalar(select(Group).filter_by(group_id=group_id))
        if not group:
            return None
        else:
            logger.info(f"Группы с ID {group_id} найденв!")
            return group.thread_id

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении группы: {e}")
        await session.rollback()

@connection
async def set_thread(session, group_id: int, thread_id: int):
    try:
        group = await session.scalar(select(Group).filter_by(group_id=group_id))
        if group:
            group.thread_id = thread_id
            await session.commit()

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении группы: {e}")
        await session.rollback()

@connection
async def get_groups(session) -> List[Dict[str, Any]]:
    try:
        result = await session.execute(select(Group).filter_by())
        groups = result.scalars().all()

        if not groups:
            logger.info(f"Группы не найдены.")
            return []

        grpup_list = [
            {
                'id': group.id,
                'group_id': group.group_id,
            } for group in groups
        ]

        return grpup_list
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении групп: {e}")
        return []
    

@connection
async def delete_group(session, group_id) -> Optional[Group]:
    try:
        group = await session.scalar(select(Group).filter_by(group_id=group_id))
        if not group:
            logger.error(f"Группа с ID {group_id} не найдена.")
            return None

        await session.delete(group)
        await session.commit()
        logger.info(f"Группа с ID {group_id} успешно удалена.")
        return group
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении группв: {e}")
        await session.rollback()
        return None