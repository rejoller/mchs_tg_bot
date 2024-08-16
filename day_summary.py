from aiogram.filters import Command
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message

from aiogram import Router, F

from sqlalchemy import  text
from sqlalchemy.orm import aliased

from database.models import Fires

from datetime import timedelta, datetime as dt


from images import daily_rep_animation

main_router = Router()


@main_router.message(Command('daily_rep'), F.chat.type == 'private')
async def dayly_rep(message: Message, session: AsyncSession):

    f2 = aliased(Fires)
    now = dt.now()
    yesterday_start = (now - timedelta(days=1)
                       ).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = now.replace(hour=9,minute=0, second=0, microsecond=0)
    
    yesterday_end_lie = (now - timedelta(days=1)).replace(hour=23,minute=59, second=59, microsecond=999)

    df_query = text(f"""
                            select   f.fire_zone
            , count(f.fire_ext_id), round(sum(f.fire_area)::numeric,1) as fire_area
        from fires f     
        Where  f.ext_log <>2
            and f.date_actual between '{yesterday_start}' and '{yesterday_end}'
            and f.date_import between '{yesterday_start}' and '{yesterday_end}'
            and not exists(
                Select 1 from fires f2 
                Where f.fire_id <> f2.fire_id and f2.fire_ext_id = f.fire_ext_id
                    and (f2.date_actual > f.date_actual or f2.date_import > f.date_import)
                    and f2.date_actual between '{yesterday_start}' and '{yesterday_end}'
                    and f2.date_import between '{yesterday_start}' and '{yesterday_end}'
            )
        Group by Grouping sets ( (f.fire_zone),())
        Order by f.fire_zone; 
        ;
                    """)

    result = await session.execute(df_query)

    df_query_result = result.all()

    df_1 = pd.DataFrame(df_query_result)
    df_1 = df_1.fillna('Всего')

    response = ''

    yesterday_end_lie = yesterday_end_lie.strftime('%H:%M %d.%m.%Y')
    summary = df_1.query('fire_zone == "Всего"')
    if not summary.empty:
        for index, row in summary.iterrows():
            if row['count'] != 0:
                response += (f'По состоянию на {yesterday_end_lie} на территории Красноярского края количество действующих лесных пожаров '
                             f'<b>{row["count"]}</b> на площади <b>{row["fire_area"]} га.</b>\n')

    acc = df_1.query('fire_zone == "АСС"')
    if not acc.empty:
        for index, row in acc.iterrows():

            response += (f'пожаров в авиазоне - <b>{row["count"]}</b>, площадь <b>'
                         f'{row["fire_area"]} га</b>;')
    nss = df_1.query('fire_zone == "НСС"')
    if not nss.empty:
        for index, row in nss.iterrows():

            response += (f'\nпожаров в наземной зоне -  <b>'
                         f'{row["count"]}</b>, площадь <b>{row["fire_area"]} га</b>;')

    zk = df_1.query('fire_zone == "ЗК"')
    if not zk.empty:
        for index, row in zk.iterrows():

            response += (f'\nпожаров в зоне контроля -  <b>'
                         f'{row["count"]}</b>, площадь <b>{row["fire_area"]} га</b>.')
            
    

    if response != '':
        await message.answer_animation(animation=daily_rep_animation, caption=response, width=50, height=100, parse_mode='HTML')
    else:
        await message.answer('Данных для ежедневного отчета нет')
