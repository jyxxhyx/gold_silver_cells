from typing import Optional, Tuple

import pulp
from pulp import PULP_CBC_CMD, GUROBI_CMD

from model.abstract_model import AbstractModel


class GoldSilverCells(AbstractModel):
    def __init__(self, grid_size: Tuple[int, int], k: int):
        self.grid_size = grid_size
        self.k = k
        self.big_m = 8
        self.model = pulp.LpProblem("GoldSilverCells", pulp.LpMaximize)

    def _set_iterables(self):
        self.cap_g = [(i, j) for i in range(self.grid_size[0])
                      for j in range(self.grid_size[1])]
        self.neighbors = dict()
        for (i, j) in self.cap_g:
            temp_list = list()
            if i > 0 and j > 0:
                temp_list.append((i - 1, j - 1))
            if i > 0:
                temp_list.append((i - 1, j))
            if i > 0 and j < self.grid_size[1] - 1:
                temp_list.append((i - 1, j + 1))
            if j > 0:
                temp_list.append((i, j - 1))
            if j < self.grid_size[1] - 1:
                temp_list.append((i, j + 1))
            if i < self.grid_size[0] - 1 and j > 0:
                temp_list.append((i + 1, j - 1))
            if i < self.grid_size[0] - 1:
                temp_list.append((i + 1, j))
            if i < self.grid_size[0] - 1 and j < self.grid_size[1] - 1:
                temp_list.append((i + 1, j + 1))
            self.neighbors[(i, j)] = temp_list
        return

    def _set_variables(self):
        self.x = pulp.LpVariable.dicts('x', self.cap_g, cat=pulp.LpBinary)
        self.y = pulp.LpVariable.dicts('y', self.cap_g, cat=pulp.LpBinary)
        return

    def _set_objective(self):
        self.model += pulp.lpSum(self.y[i, j] for (i, j) in self.cap_g)
        return

    def _set_constraints(self):
        for (i, j) in self.cap_g:
            self.model += (self.x[i, j] + self.y[i, j] <= 1, f'assign_{i}_{j}')
            self.model += (pulp.lpSum(self.x[i2, j2]
                                      for (i2, j2) in self.neighbors[i, j]) >=
                           self.k + self.big_m * (self.y[i, j] - 1),
                           f'con1_{i}_{j}')
            self.model += (pulp.lpSum(self.x[i2, j2]
                                      for (i2, j2) in self.neighbors[i, j]) <=
                           self.k + self.big_m * (1 - self.y[i, j]),
                           f'con2_{i}_{j}')
        return

    def _optimize(self):
        time_limit_in_seconds = 4 * 60 * 60
        self.model.writeLP('test.lp')
        self.model.solve(PULP_CBC_CMD(timeLimit=time_limit_in_seconds))
        # self.model.solve(GUROBI_CMD(timeLimit=time_limit_in_seconds))
        return

    def _is_feasible(self):
        return True

    def _process_infeasible_case(self):
        return list(), list()

    def _post_process(self):
        silver_cells = list()
        gold_cells = list()
        for (i, j) in self.cap_g:
            if self.x[i,j].value() > 0.9:
                silver_cells.append((i,j))
            elif self.y[i, j].value() > 0.9:
                gold_cells.append((i, j))
        return silver_cells, gold_cells
