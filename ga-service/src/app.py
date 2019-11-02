import logging

import enums
from config import Config
from tasks import TaskQueue


def get_logger() -> logging.Logger:
    cfg = Config()

    logger = logging.getLogger('genetic_algorithm')
    logger.setLevel(cfg.log_level.value)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handler to the logger
    logger.addHandler(ch)

    if cfg.environment == enums.EnvironmentTypes.DEV:
        # create file handler which logs even debug messages
        fh = logging.FileHandler('app.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


logger = get_logger()
logger.info('Environment: {}'.format(Config().environment))


class App:
    def __init__(self):
        self.logger = logging.getLogger('genetic_algorithm.App')
        self.tasks = TaskQueue()
        self.logger.info('Genetic algorithm app initialized!')

    def run(self):
        [task.run() for task in self.tasks]


if __name__ == '__main__':
    app = App()
    app.run()
