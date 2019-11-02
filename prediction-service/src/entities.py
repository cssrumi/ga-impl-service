import operator

from sanic_motor import BaseModel
from sanic_motor import logger


class ExtendedModel(BaseModel):
    __entities__ = []
    __coll_env__ = ''
    __coll_default__ = ''

    @staticmethod
    def init_app(app, open_listener='before_server_start',
                 close_listener='before_server_stop', name=None, uri=None):
        BaseModel.init_app(app, open_listener, close_listener, name, uri)
        [entity.set_coll()
         for entity in ExtendedModel.__entities__
         if not isinstance(entity, ExtendedModel)]

    @classmethod
    def add_entity(cls):
        ExtendedModel.__entities__.append(cls)

    @classmethod
    def set_coll(cls):
        if BaseModel.__app__:
            cls.__coll__ = BaseModel.__app__.config.get(
                cls.__coll_env__,
                cls.__coll_default__)
            logger.info("Entity<{}> collection set to '{}'".format(cls.__name__, cls.__coll__))
        else:
            raise Exception('Base Model has not been initialized.')

    def to_dict(self):
        dct = {}
        for k, v in vars(self).items():
            if not isinstance(v, (int, float, list, dict, tuple)):
                v = str(v)
            dct[k] = v
        return dct


class Sensor(ExtendedModel):
    __coll_env__ = 'COLL_CONFIG'
    __coll_default__ = 'config'


Sensor.add_entity()


class Individual(ExtendedModel):
    __coll_env__ = 'COLL_INDIVIDUALS'
    __coll_default__ = 'individuals'


Individual.add_entity()


class Data(ExtendedModel):
    __coll_env__ = 'COLL_DATA'
    __coll_default__ = 'data'

    def predict(self, sensor: Sensor, individual: Individual):
        return sum(map(operator.mul, individual.genotype, self.to_array(sensor)))

    def to_array(self, sensor: Sensor):
        return [self.to_number(key) for key in sensor.fields]

    def to_number(self, key: str):
        v = getattr(self, key, 0)
        if isinstance(v, str):
            v = float(v.replace(',', '.'))
        return v


Data.add_entity()
