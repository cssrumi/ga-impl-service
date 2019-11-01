import logging


from tasks import TaskQueue

logger = logging.getLogger('genetic_algorithm')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


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
