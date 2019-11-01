import datetime
import logging
from typing import Union, Optional, List

from ga import Individual

from config import Config
from connector import Connector
from ga_impl import GeneticAlgorithm


class Sensor:
    def __init__(self, _id=None, fields=None, predict=None, vendor=None, vendor_id=None, datetime_col=None):
        self._id = _id
        self.fields = fields
        self.predict = predict
        self.vendor = vendor
        self.vendor_id = vendor_id
        self.datetime_col = datetime_col

        self.cfg = Config()
        self.con = Connector()
        self.logger = logging.getLogger('genetic_algorithm.entities.Sensor')

    @property
    def query(self):
        return {'sensor_id': self.id}

    @property
    def id(self):
        return self._id

    def calculate_new_genotype(self):
        self.logger.info('Collecting data for: {}'.format(self.to_dict()))
        data = self.get_data()
        training_data = TrainingData.from_data(data, self)
        if not training_data:
            self.logger.warning('Empty training data... Unable to calculate new genotype')
            return None
        row_size = len(training_data[0])
        self.logger.info('Collected: {} items'.format(len(training_data)))

        self.logger.info('Init of Genetic Algorithm...')
        ga = GeneticAlgorithm(training_data, row_size=row_size)
        prev_bests = [best for best in self.get_individual(1)]
        for individual in prev_bests:
            ga.add(individual)
        best = ga.evolve()
        if any(best == prev for prev in prev_bests):
            self.logger.info('New best not found.')
        else:
            self.logger.info('New best Individual generated!')
            self.save_individual(best)
        self.logger.info('Calculation completed!')

    def save(self):
        new_id = self.con.save(self.to_dict(), self.cfg.config_collection).inserted_id
        self.update({'_id': new_id})
        self.logger.info('Saved: {}'.format(self.to_dict()))
        return self

    def save_individual(self, individual: Individual):
        json = individual.to_json()
        self.logger.info('Saving individual: {}'.format(json))
        json.update(self.query)
        date_time = datetime.datetime.now().timestamp()
        json.update({self.datetime_col: date_time})
        new_id = self.con.save(json, self.cfg.individuals_collection).inserted_id
        json.update({'_id': new_id})
        return json

    def get_individual(self, quantity: Union[str, int] = 1) -> List[Individual]:
        import json

        individuals = []
        result = self.con.get(quantity, self.cfg.individuals_collection, self.query, datetime_col=self.datetime_col)

        for r in result:
            r.pop('_id')
            r.pop(self.datetime_col)
            r.pop('sensor_id')
            json_str = json.dumps(r)
            individual = Individual.from_json(json_str)
            individual.logger = logging.getLogger('genetic_algorithm.external_lib.ga')
            individuals.append(individual)

        return individuals

    def to_dict(self) -> dict:
        dct = {
            'fields': self.fields,
            'predict': self.predict,
            'vendor': self.vendor,
            'vendor_id': self.vendor_id,
            'datetime_col': self.datetime_col
        }
        if self._id:
            dct['_id'] = self.id
        return dct

    def get_data(self, quantity: Union[str, int] = 'ALL'):
        data = self.con.get(quantity, self.cfg.data_collection, self.query, self.datetime_col)
        data = filter(lambda row: self.validate(row), data)
        data = list(data)
        return data

    def update(self, json: dict):
        for k, v in json.items():
            setattr(self, k, v)

    def validate(self, row: dict) -> bool:
        if all(f in list(row.keys()) for f in self.fields):
            return True
        return False


class TrainingData:
    @staticmethod
    def from_data(data: List[dict], sensor: Sensor) -> List[List[float]]:
        def to_list(obj: dict, obj_after_24h: dict):
            lst = [obj.get(k) for k in sensor.fields]
            lst.append(obj_after_24h.get(sensor.predict))
            return lst

        def min_date(date):
            date = datetime.datetime.fromtimestamp(date)
            date += datetime.timedelta(hours=23, minutes=30)
            return date.timestamp()

        def max_date(date):
            date = datetime.datetime.fromtimestamp(date)
            date += datetime.timedelta(days=1, minutes=30)
            return date.timestamp()

        def nearest(items, pivot):
            if items:
                return min(items, key=lambda x: abs(x.get(sensor.datetime_col) - pivot))

        def equal_date(date):
            date = datetime.datetime.fromtimestamp(date)
            date += datetime.timedelta(days=1)
            return date.timestamp()

        td = []
        data_size = len(data)
        if data_size > 1:
            data.sort(key=lambda x: x.get(sensor.datetime_col))
        for i in range(data_size):
            d = data[i]
            dt = d.get(sensor.datetime_col)
            max_dt = max_date(dt)
            min_dt = min_date(dt)
            j = 0 + i
            temp = data[j]
            items = []
            while temp.get(sensor.datetime_col) < max_dt and j < data_size:
                temp = data[j]
                if temp.get(sensor.datetime_col) > min_dt:
                    items.append(temp)
                j += 1
            d_after_24h = nearest(items, equal_date(dt))
            if d_after_24h:
                td.append(to_list(d, d_after_24h))
        return td
