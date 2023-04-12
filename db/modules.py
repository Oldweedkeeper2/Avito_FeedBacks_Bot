import asyncio
import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    fullname = Column(String)
    nickname = Column(String(30))


class Avito_Users(Base):
    __tablename__ = "avito_users"

    number = Column(Text, primary_key=True)
    email = Column(Text)
    password = Column(Text)
    full_name = Column(Text)
    working = Column(Boolean, default=True)
    problems = Column(Integer, default=0)
    reviews_count = Column(Integer, default=0)
    proxy = Column(JSON)
    last_review = Column(TIMESTAMP)
    session_cookies = Column(JSON)
    avito_cookies = Column(JSON)
    google_cookies = Column(JSON)
    # прописать колонки


alchemy_engine = str(os.getenv("ALCHEMY_ENGINE"))


async def create_session():
    async_engine = create_async_engine(alchemy_engine)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return AsyncSession(async_engine)


async def get_one_user() -> Avito_Users:
    async with await create_session() as session:
        stmt = select(Avito_Users).where(Avito_Users.number == '125521515')
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def create_new_user():
    async with await create_session() as session:
        try:
            user = Avito_Users(number='125521515',
                               email='user@avito.com',
                               password='password',
                               full_name='user@avito.com',
                               working=True,
                               proxy={},
                               last_review=datetime.datetime.now(),
                               session_cookies={},
                               avito_cookies={},
                               google_cookies={})
            session.add(user)
            await session.flush() # выдаёт в одной сессии
            print(await get_one_user())
            await session.commit()
        except Exception as e:
            print(e)


async def get_user_data():
    user = await get_one_user()
    print(user.email)


print(asyncio.run(create_new_user()))

# new_product = Products(
#                             Name=product['item_name'] + " " + cigars[item_id]['item_taste'],
#                             BrandId=int(brandId),
#                             CategoryId=int(product['category_id']),
#                             ChargingId=item_charging_type,
#                             Price=int(product['item_price']),
#                             Description=f"Количество затяжек: {cigars[item_id]['item_count_traction']}",
#                             Sale=None,
#                             DateAdd=datetime.utcnow().date(),
#                             PhotoId=None
#                         )
#
#                         session.add(new_product)
#                         await session.flush()
#                         productId = new_product.ProductId


async def add_stuff_user(Name, Surname, Phone, RoleId):
    async with await create_session() as session:
        result = await session.execute(select(Users).where(Users.Phone == Phone))
        user = result.scalar_one_or_none()
        if user == None:
            # Создаем нового пользователя с заданными параметрами
            user_add = Users(
                TelegramId=0,
                Name=Name,
                Surname=Surname,
                Phone=Phone,
                RoleId=RoleId,
                Point=0
            )

            # Добавляем пользователя в сессию и сохраняем изменения
            session.add(user_add)
        else:
            user.Name = Name
            user.Surname = Surname
            user.Phone = Phone
            user.RoleId = RoleId
    await session.commit()