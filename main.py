import datetime
import os
import time

import sqlalchemy as sa

from utilites import convert_valute, get_sheet_data, get_valute

SAMPLE_SPREADSHEET_ID = os.environ.get('SAMPLE_SPREADSHEET_ID', '')
SAMPLE_RANGE_NAME = os.environ.get('SAMPLE_RANGE_NAME', '')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

"""Данные для подключения к базе"""
md = sa.MetaData(os.environ.get('DATABASE_URL', ''))

"""Создаёт таблицу в базе"""
product_table = sa.Table('product', md,
    sa.Column('id',   sa.types.Integer, primary_key=True),
    sa.Column('num',   sa.types.Integer),
    sa.Column('order',   sa.types.Integer),
    sa.Column('cost_usd',   sa.types.Numeric(10, 2)),
    sa.Column('cost_rub',   sa.types.Numeric(10, 2)),
    sa.Column('delivery_time', sa.types.Date)
)
md.create_all()

"""Подключается к базе"""
con = md.bind.connect()

current_course = get_valute('USD')


def main():
    """Очищаем данные из таблицы"""
    con.execute(
        product_table.delete()
    )

    for row in get_sheet_data(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, SCOPES):
        """Вставляет данные в базу"""
        con.execute(
            product_table.insert().values(
                num=row[0],
                order=row[1],
                cost_usd=row[2],
                cost_rub=convert_valute(current_course['Value'], row[2]),
                delivery_time=datetime.datetime.strptime(row[3], "%d.%m.%Y").date()
            )
        )


if __name__ == '__main__':
    while True:
        main()
        time.sleep(5)
        print('Данные сохранены')
