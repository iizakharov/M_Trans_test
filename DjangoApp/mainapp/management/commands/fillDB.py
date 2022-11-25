from datetime import datetime

from django.core.management.base import BaseCommand
from mainapp.models import Flight, Scheme
import os
import pandas as pd
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

JSON_PATH = 'mainapp/management/data'


def load_data(file_name):
    path = os.path.join(JSON_PATH, file_name + '.xlsx')
    df = pd.read_excel(io=path, sheet_name=0)
    columns = df.columns
    df.sort_values([columns[1], columns[0], columns[2]], ascending=[True, True, True], inplace=True)
    print(df.head())
    output = df.itertuples(index=False)
    data = tuple(output)
    return data


class Command(BaseCommand):
    help = 'Filling database.'

    def handle(self, *args, **options):
        Flight.objects.all().delete()
        Scheme.objects.all().delete()
        flights = load_data('Данные')
        ROAD_DICT = {
            'ЮВС': 'jvs',
            'ДВС': 'dvs',
            'ОКТ': 'okt',
            'ЗСБ': 'zcb',
            'ГОР': 'gor',
            'МСК': 'msc',
            'СКВ': 'ckv',
            'СВР': 'cvr',
            'ЗАБ': 'zab',
            'КРС': 'krc',
        }
        for flight in flights:
            try:
                print(flight)
                Flight.objects.create(
                    date=make_aware(datetime.strptime(flight[0].split('.')[0],  "%Y-%m-%d %H:%M:%S")),
                    van=flight[1],
                    gruj='gruj' if flight[2] == 'ГРУЖ' else 'por',
                    start_road=ROAD_DICT[flight[3]],
                    destination_road=ROAD_DICT[flight[4]],
                    cost=flight[5],
                    downtime_loading=flight[6],
                    downtime_uploading=flight[7],
                    travel_time=flight[8],
                    distance_road=flight[9],
                    expenses=flight[10],
                    station_start_id=flight[11],
                    station_destination_id=flight[12]
                )

            except Exception as e:
                print('ERROR ', e)
                # Создаем суперпользователя при помощи менеджера модели
            if not User.objects.filter(username='w').exists():
                User.objects.create_superuser('w', 'w@w.ru', '1')

        print(len(flights))
