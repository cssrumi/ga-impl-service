import logging
from typing import List, Optional

import ga

from config import Config


class GeneticAlgorithm:
    def __init__(self, training_data: List[list], row_size: int):
        self.logger = logging.getLogger('genetic_algorithm.ga_impl.GeneticAlgorithm')
        self._training_data = training_data
        self._row_size = row_size
        self.cfg = Config()

        self._population = ga.Population(training_data,
                                         row_size,
                                         logger=logging.getLogger('genetic_algorithm.external_lib.ga'),
                                         initial_population_size=self.cfg.initial_population_size,
                                         max_age=self.cfg.max_age,
                                         max_children_size=self.cfg.max_children_size,
                                         mutation_chance=self.cfg.mutation_chance,
                                         crossover_chance=self.cfg.crossover_chance)

    def evolve(self, n: int = None) -> ga.Individual:
        best = None
        if not n and self.cfg.max_generation:
            n = self.cfg.max_generation
        elif not n:
            n = 1000
        for i in range(n):
            self._population.evolve()
            if best:
                if self.get_best().fitness < best.fitness:
                    best = self.get_best()
                    self.logger.debug('Current best at iteration {}: {}'.format(i, best))
            else:
                best = self.get_best()
        self.logger.info('Best individual: {}'.format(best))
        return best

    def get_best(self):
        return self._population.get_best()

    def add(self, individual: ga.Individual):
        self._population.add_individual(individual)
