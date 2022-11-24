from pandas import ExcelWriter
import pandas as pd
import sqlite3


def create_db(table, cursor):
    """
    Создание таблицы в БД
    :param table: Название таблицы
    :param cursor: Подключение к БД
    :return: Заголовки столбцов
    """
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table}
                               (date TEXT,
                               van INT,
                               gruj TEXT,
                               start_road TEXT,
                               destination_road TEXT,
                               cost INT TEXT,
                               downtime_loading INT,
                               downtime_uploading INT,
                               travel_time INT,
                               distance road INT,
                               expenses INT,
                               station_start_id INT,
                               station_destination_id INT)"""
                   )
    print(f'table {table} created!')
    path = 'Данные.xlsx'
    df = pd.read_excel(io=path, sheet_name=0)
    columns = df.columns
    output = df.itertuples(index=False)
    data = tuple(output)
    wildcards = ','.join(['?'] * 13)
    insert_sql = f"""INSERT INTO {table} VALUES ({wildcards})"""
    cursor.executemany(insert_sql, data)
    conn.commit()
    return columns


def drop_table(table, cursor):
    """
    Удалить таблицу
    """
    cursor.execute(f"""DROP TABLE IF EXISTS {table}""")
    print(f'table {table} removed!')


def add_data_to_df(df, van_dict=None, numbers=False, some_data=None):
    """
    :param df: Pandas DataFrame
    :param van_dict:
    :param numbers:
    :param some_data:
    :return:
    """
    if some_data:
        profit_column, daily_profit = [], []
        for row in df.itertuples(index=False):
            profit_column.append(some_data[row[0]]['sum'])
            daily_profit.append(some_data[row[0]]['profit'])
        return profit_column, daily_profit
    scheme = []
    numbers_arr = []
    last_van = None
    numb = 0
    for row in df.itertuples(index=False):
        if numbers:
            if (last_van is None) or row[1] != last_van:
                last_van, numb = row[1], 0
            else:
                numb += 1
            numbers_arr.append(numb)
        scheme.append(van_dict[row[1]])
    if numbers:
        return scheme, numbers_arr
    else:
        return scheme


def task_3_1(df, numbers=False, to_add=None):
    """
    :param df: Pandas DataFrame
    :param numbers: Получить номера рейсов
    :param to_add: Добавить в Pandas DataFrame дополнительные данные основанные на номерах схем
    :return:
    """
    if to_add:
        profit_column, daily_profit = add_data_to_df(df, some_data=to_add)
        df['profit'] = profit_column
        df['daily_profit'] = daily_profit
    else:
        uniq_van = pd.unique(df['van'].values)
        van_dict = {}
        for van in range(1, len(uniq_van) + 1):
            van_dict.update({uniq_van[van - 1]: van})
        scheme, numbers = add_data_to_df(df, van_dict, numbers=numbers)
        df.insert(0, 'number', numbers)
        df.insert(0, 'scheme', scheme)

    print(df.head(10))
    return df


def total_sum(dictionary: dict):
    """
    - Посуточная дохождность схем
    - Формула: (Итого начислено без НДС – затраты) / кол-во суток в схеме
    """
    for scheme, items in dictionary.items():
        daily_profit = round(items['sum'] / round(items['days']), 2)
        dictionary[scheme].update({'profit': daily_profit})
    return dictionary


def task_3_2(df):
    """
    - Общая дохождность схем
    - Формула: (Итого начислено без НДС – затраты)
    """
    scheme_dict = {}
    for row in df.itertuples(index=False):
        if row[0] not in scheme_dict.keys():
            scheme_dict[row[0]] = {
                'sum': row[7] if row[7] != 0 else (0 - row[12]),
                'days': row[8] + row[9] + row[10]
            }
        else:
            scheme_dict[row[0]]['sum'] = (scheme_dict[row[0]]['sum'] + row[7]) if row[7] != 0 else \
                (scheme_dict[row[0]]['sum'] - row[12])
            scheme_dict[row[0]]['days'] = scheme_dict[row[0]]['days'] + row[8] + row[9] + row[10]
    scheme_dict = total_sum(scheme_dict)
    return scheme_dict


if __name__ == '__main__':
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    table = 'data'
    drop_table(table, cursor)
    columns = create_db(table, cursor)

    df = pd.read_sql_query(f"SELECT * FROM {table}", conn, parse_dates={'date': "%Y-%m-%d %H:%M:%S.%"})
    df.sort_values(['van', 'date', 'gruj'], ascending=[True, True, True], inplace=True)
    # 3.1
    df = task_3_1(df, numbers=True)
    # 3.2
    scheme_profit = task_3_2(df)
    df = task_3_1(df, to_add=scheme_profit)
    # 3.3
    new_columns = dict(zip(list(df.columns), ['scheme', 'Номер рейса'] + list(columns) + ['Общая доходность схемы',
                                                                                          'Доходность схемы в сутки']))
    df = df.rename(new_columns, axis=1)
    writer = ExcelWriter('Результат.xlsx')
    df.to_excel(writer, 'Лист1', index=False)
    writer.save()

    conn.close()
