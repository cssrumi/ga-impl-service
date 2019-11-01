import logging
from typing import Optional

import connector
import enums
from config import Config
from sensor import Sensor
from ga_impl import GeneticAlgorithm


class TaskQueue:
    def __init__(self):
        self._bootstrapped = False
        self.logger = logging.getLogger('genetic_algorithm.tasks.TaskQueue')
        self.cfg = Config()
        self.connector = connector.get_connector()
        self.tasks = []
        self.generate_tasks()

    def __iter__(self):
        return self

    def __next__(self):
        if self.tasks:
            return self.tasks.pop(0)
        else:
            self.generate_tasks()
            return self.__next__()

    def create_new_genotype(self):
        training_data = [[1, 2, 3], [2, 3, 3], [5, 5, 5]]
        ga = GeneticAlgorithm(training_data, len(training_data[0]))
        self.connector = ga.get_best()

    def generate_tasks(self):
        if self.cfg.environment == enums.EnvironmentTypes.DEV \
                and self.cfg.bootstrap \
                and not self._bootstrapped:
            self.logger.info("Environment: {}".format(self.cfg.environment.name))
            self.tasks.append(BootstrapTask())
            self._bootstrapped = True

        for sensor in self.connector.get('ALL', self.cfg.config_collection):
            sensor_obj = Sensor()
            sensor_obj.update(sensor)
            self.tasks.append(GeneticAlgorithmTask(sensor=sensor_obj))


class Task:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('genetic_algorithm.tasks.{}'.format(__class__.__name__))
        self.cfg = Config()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def run(self):
        pass


class GeneticAlgorithmTask(Task):
    def __init__(self, sensor: Sensor):
        super().__init__()
        self.sensor = sensor
        self.connector = connector.get_connector()

    def run(self):
        self.logger.info('{} is running...'.format(__class__.__name__))
        self.sensor.calculate_new_genotype()
        self.logger.info('{} completed!'.format(__class__.__name__))


class BootstrapTask(Task):
    def __init__(self):
        super().__init__()
        self.connector = connector.get_connector()

    def run(self):
        self.logger.info('Bootstrapping...')
        self.connector.remove(self.cfg.data_collection)
        self.connector.remove(self.cfg.config_collection)
        key_dict = {
            'date': 'date_time',
            'pm10': 'pm10',
            'wind direction': 'wind_direction',
            'wind strength': 'wind',
            'temp': 'temperature',
            'humidity': 'humidity',
            'dew point': 'dew_point',
            'air pres.': 'pressure'
        }
        from bootstrap.bootstrap import get_data_from_csv
        data = get_data_from_csv(key_dict=key_dict)

        sensor = Sensor(fields=list(data[0].keys()), vendor='bootstrap', vendor_id=0,
                        datetime_col='date_time', predict='pm10')
        sensor.save()

        [d.update({'sensor_id': sensor.id}) for d in data]

        saved_data = self.connector.save(data, self.cfg.data_collection).inserted_ids
        self.logger.info('Saved data count: {}'.format(len(saved_data)))
