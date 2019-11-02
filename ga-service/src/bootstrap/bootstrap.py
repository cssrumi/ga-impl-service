import csv
import os
from datetime import datetime
from typing import List

d_key_dict = {
    'Czas Pomiaru': 'date_time',
    'PmGdaPoWie01-PM10-1g': 'pm10',
    'Kierunek wiatru': 'wind_direction',
    'Predkosc wiatru': 'wind',
    'Temperatura powietrza': 'temperature',
    'Wilgotnosc': 'humidity',
    'Temperatura punktu rosy': 'dew_point',
    'Cisnienie': 'pressure'

}


def csv_repair(filename):
    final = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            final.append('20' + line)
    repaired_name = "{}_fixed".format(filename)
    with open(repaired_name, 'w') as f:
        f.writelines(final)
    return repaired_name


def get_abs_path(file):
    this_file = os.path.abspath(__file__)
    f_dir = os.path.dirname(this_file)
    csv_file = os.path.join(f_dir, file)
    return os.path.abspath(csv_file)


def export_data_from_xls(filename, db, key_dict):
    pass


def get_data_from_csv(filename=get_abs_path('daneArka.csv'), key_dict=d_key_dict, delimiter=',',
                      dt_format="%Y-%m-%d %H:%M") -> List[dict]:
    result = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for r in reader:
            temp_dict = {}
            if '' in r.values():
                continue
            for k, v in key_dict.items():
                if v == 'date_time':
                    temp_dict[v] = int(datetime.strptime(r.get(k).strip(), dt_format).timestamp())
                else:
                    temp_dict[v] = r.get(k).strip()

            result.append(temp_dict)
    return result
