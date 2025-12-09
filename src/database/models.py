import enum
from typing import List
from uuid import uuid4
from sqlalchemy import BigInteger, CheckConstraint, Column, Enum, Integer, Table, Text, ForeignKey, String, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from .database import Base
from sqlalchemy.dialects.postgresql import UUID

# Модель для таблицы пользователей
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

