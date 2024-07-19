from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Municipalities, Subscriptions
from handlers import Form
from datetime import datetime as dt
from images import main_photo
from images import map_image
from bot import bot



callback_router = Router()

@callback_router.callback_query(F.data == 'choise_munic')
async def handle_waiting_for_choise(query: types.CallbackQuery, state: FSMContext, session: AsyncSession):

    subscribe_query = select(Municipalities.map_id, Municipalities.municipality_name).order_by(Municipalities.municipality_name.asc())
    
    result = await session.execute(subscribe_query)
    all_municipalities = result.all() 
    
    builder = ReplyKeyboardBuilder()
    
    for _, mun in enumerate(all_municipalities, start=1):
        button_text = mun[1]
        builder.button(text=button_text)
    builder.button(text='Отмена')
    builder.adjust(1)
    keyboard_1 = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.answer_photo(caption='Выберите муниципальное образование',
                                   reply_markup=keyboard_1, photo=map_image, parse_mode='HTML')
    
    
    await state.set_state(Form.waiting_for_munic)
    
    
    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])


@callback_router.callback_query(F.data == 'choise_all_munic')
async def handle_waiting_for_choise(query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = query.from_user.id

    subscribe_query = select(Municipalities.municipality_id, Municipalities.municipality_name).order_by(
        Municipalities.municipality_name.asc())
    result = await session.execute(subscribe_query)
    all_municipalities = result.all()
    municipality_ids = [item[0] for item in all_municipalities]
    municipality_names = [item[1] for item in all_municipalities]
    subscribers_data = [
        {
            "user_id": user_id,
            "municipality_id": municipality_ids,
            "date_subscribed": dt.now()
        }
        for municipality_ids, municipality_name in zip(municipality_ids, municipality_names)
    ]
    add_subscriber_query = insert(Subscriptions).values(
        subscribers_data).on_conflict_do_nothing()
    await query.answer('Вы подписались на все муниципальные образования', show_alert=True)
    await session.execute(add_subscriber_query)
    await session.commit()

    await bot.delete_message(chat_id=user_id, message_id= query.message.message_id)



@callback_router.callback_query(F.data == 'main_menu')
async def handle_waiting_for_choise(query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    
    caption = ("Вы вернулись в главное меню бота по инцидентам МЧС Красноярского края. Чтобы подписаться на одно из муниципальных "
               "образований для получения новостей воспользуйтесь командой /subscribe \n Чтобы подписаться "
               "на все обновления нажмите на команду /subscribe_all\n")
    await state.clear()

    await query.message.answer_photo(caption=caption, photo=main_photo)
    
    
    
    
