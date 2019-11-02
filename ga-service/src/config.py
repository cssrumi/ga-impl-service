import logging
import threading
import os
from enum import Enum
from typing import List, Union

import enums
import yaml

module_logger = logging.getLogger('genetic_algorithm.config')
module_location = os.path.dirname(os.path.abspath(__file__))


class Config:
    __instance = None
    __lock = threading.Lock()
    __props = {
        'save_interval_type': {'type': enums.SaveIntervalTypes, 'default': enums.SaveIntervalTypes.TIME},
        'initial_population_size': {'type': int, 'default': 200},
        'crossover_type': {'type': str, 'default': None},
        'max_age': {'type': int, 'default': 7},
        'pass_best': {'type': bool, 'default': True},
        'max_generation': {'type': int, 'default': None},
        'max_children_size': {'type': int, 'default': 50},
        'time_interval': {'type': int, 'default': 1},
        'time_unit': {'type': enums.TimeUnitTypes, 'default': enums.TimeUnitTypes.H},
        'log_level': {'type': enums.LoggerLevels, 'default': enums.LoggerLevels.INFO},
        'crossover_chance': {'type': float, 'default': 0.8},
        'mutation_chance': {'type': float, 'default': 0.9},
        'bootstrap': {'type': bool, 'default': False},
        'database_type': {'type': enums.DatabaseTypes, 'default': enums.DatabaseTypes.MONGODB},
        'database_ip': {'type': str, 'default': 'localhost'},
        'database_port': {'type': str, 'default': 27017},
        'database_user': {'type': str, 'default': None},
        'database_password': {'type': str, 'default': None},
        'database_name': {'type': str, 'default': 'sensors'},
        'table_name': {'type': str, 'default': None},
        'config_collection': {'type': str, 'default': 'config'},
        'individuals_collection': {'type': str, 'default': 'individuals'},
        'data_collection': {'type': str, 'default': 'data'},
        'environment': {'type': enums.EnvironmentTypes, 'default': enums.EnvironmentTypes.DEV},
        'redis_url': {'type': str, 'default': 'redis://localhost'},
    }

    @staticmethod
    def get_instance():
        return Config()

    def __new__(cls):
        with Config.__lock:
            if not Config.__instance:
                Config.__instance = object.__new__(cls)
                Config.__instance.logger = logging.getLogger('genetic_algorithm.config.Config')
                Config.__instance._load()
        return Config.__instance

    def _load(self):
        default_config = self.convert(self.read_default())
        yaml_config = self.convert(self.read_yaml())
        env_config = self.convert(self.read_env())
        config = self.merge([default_config, yaml_config, env_config])
        for key, value in config.items():
            setattr(self, key, value)

    def reload(self):
        with self.__lock:
            self._load()

    def read_env(self) -> dict:
        try:
            env_data = self._load_from_env()
        except Exception as e:
            env_data = {}
            self.logger.warning('Error while loading config from Environments, {}'.format(e))
        self.logger.debug('Raw env config: {}'.format(env_data))
        return env_data

    def read_yaml(self, filename='config.yaml') -> dict:
        try:
            yaml_data = self._read_yaml_file(filename)
        except Exception as e:
            yaml_data = {}
            self.logger.warning('Unable to read config'.format(e))
        self.logger.debug('Raw yaml config: {}'.format(yaml_data))
        return yaml_data

    def read_default(self) -> dict:
        try:
            default_data = self._load_default()
        except Exception as e:
            default_data = {}
            self.logger.warning(e)
        self.logger.debug('Raw default config: {}'.format(default_data))
        return default_data

    def _read_yaml_file(self, filename: str = 'config.yaml') -> dict:
        if os.path.isfile(filename):
            full_path = os.path.abspath(filename)
        else:
            full_path = os.path.join(module_location, filename)
        if os.path.isfile(full_path):
            with open(full_path, 'r') as stream:
                yaml_data = yaml.safe_load(stream)
            if isinstance(yaml_data, dict):
                result_dict = {}
                for key in [key for key in yaml_data.keys() if key.lower() in self.__props.keys()]:
                    result_dict[key.lower()] = yaml_data[key]
                return result_dict
            raise Exception('Invalid config {}'.format(filename))
        raise FileNotFoundError('{} not found'.format(filename))

    def _load_from_env(self) -> dict:
        result_dict = {}
        for key in self.__props.keys():
            value = os.getenv(key.upper())
            if value:
                result_dict[key] = value
        return result_dict

    def _load_default(self) -> dict:
        result_dict = {}
        for key, info in self.__props.items():
            default = info.get('default')
            result_dict[key] = default
        return result_dict

    def convert(self, data: dict) -> dict:
        result = {}
        try:
            for key, value in data.items():
                r_type = self.get_type(key)
                result[key] = self.cast(value, r_type)
        except (TypeError, ValueError) as e:
            error_message = str(e) + '\n\tConverting {} from {} to {}'.format(value, key, r_type)
            self.logger.exception(error_message)
            raise
        return result

    def merge(self, config_list: List[dict]) -> dict:
        final_config = {}
        for cfg in config_list:
            final_config.update(cfg)
        self.logger.debug('Merged config: {}'.format(final_config))
        return final_config

    def cast(self, variable: object, to: callable, safe: bool = False) -> object:
        self.logger.debug(
            'Safe Casting {} to {}'.format(variable, to)
            if safe else
            'Unsafe Casting {} to {}'.format(variable, to)
        )
        if issubclass(to, Enum):
            return self.as_enum(variable, to)
        elif not safe and variable is None:
            return None
        if not safe and isinstance(variable, str):
            if variable.upper() == 'NONE':
                return None
            else:
                return to(variable)
        else:
            return to(variable)

    def get_type(self, key: str) -> object:
        key_dict = self.__props.get(key)
        if key_dict:
            r_type = key_dict.get('type')
        else:
            raise KeyError('Invalid key: {}'.format(key))
        if r_type:
            return r_type
        else:
            raise TypeError('Type not found')

    def check_type(self, variable, r_type, none=True):
        if isinstance(variable, r_type) or issubclass(type(variable), r_type):
            return True
        if none and variable is None:
            return True
        raise TypeError('Value: {} isn\'t instance or child of type: '.format(variable, r_type))

    def as_enum(self, variable: Union[str, Enum], enum: Enum) -> object:
        enum_values = [e.name for e in enum]
        if variable in enum_values:
            return enum[variable]
        elif isinstance(variable, enum):
            return variable
        else:
            raise TypeError('Invalid enum type: "{}"\n\tValid types: {}'.format(variable, enum_values))
