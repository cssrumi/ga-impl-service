from enum import Enum


class EnvironmentTypes(Enum):
    DEV = 1
    QA = 2
    PREP = 3
    PROD = 4


class SaveIntervalTypes(Enum):
    TIME = 1
    GENERATION = 2
    GENERATIONS = GENERATION


class TimeUnitTypes(Enum):
    S = 1
    SEC = S
    M = 2
    MIN = M
    H = 3
    HOUR = H
    HOURS = H
    D = 4
    DAYS = 4


class DatabaseTypes(Enum):
    MYSQL = 1
    MARIADB = MYSQL
    MSSQL = 2
    POSTGRES = 3
    POSTGRESQL = POSTGRES
    MONGODB = 4
    MONGO = MONGODB


class CrossingOverTypes(Enum):
    pass
