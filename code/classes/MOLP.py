import sys
import os
import pulp
import numpy as np
from copy import deepcopy, copy
import matplotlib.pyplot as plt

# Adding classes directory to module search path (sys.path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'classes')))

from SOLUTION import Solution

class Molp():
    '''
    This class defines a custom multi-objective linear programming (MOLP) problem for diet optimization.
    It includes methods to compute individual optima, the payoff matrix, ideal and nadir points, and to normalize the model.
    '''
    def __init__(self, model):
        self.molp_id = None # Unique identifier
        self.model = deepcopy(model) # Model object
        self.individual_optima = []
        self.anti_ideal_point_attribute = None

    def num_objectives(self):
        return len(self.model.objectives)
    
    def num_variables(self):
        return len(self.model.variables)

    def compute_individual_optima(self, objective_index):
        model = deepcopy(self.model)
        sub_problem = model.pulp_model
        main_objective = model.objectives[objective_index]
        order_secondary = [0, 1]
        secondary_objectives = [obj for obj in model.objectives if obj != main_objective]
        objective_values = {}
        # First lexicographic optimization
        sub_problem.setObjective(main_objective)
        sub_problem.solve(pulp.HiGHS(msg=0))
        objective_values[main_objective.name] = copy(sub_problem.objective.value())
        # Second lexicographic optimization
        sub_problem.setObjective(secondary_objectives[order_secondary[0]])
        # Add constraint for the first objective
        sub_problem += main_objective <= objective_values[main_objective.name] #+ 1e-10
        sub_problem.solve(pulp.HiGHS(msg=0))
        objective_values[secondary_objectives[order_secondary[0]].name] = copy(sub_problem.objective.value())
        # Third lexicographic optimization
        sub_problem.setObjective(secondary_objectives[order_secondary[1]])
        # Add constraints for the first and second objectives
        sub_problem += main_objective <= objective_values[main_objective.name] #+ 1e-10
        sub_problem += secondary_objectives[order_secondary[0]] <= objective_values[secondary_objectives[order_secondary[0]].name] #+ 1e-10
        sub_problem.solve(pulp.HiGHS(msg=0))
        objective_values[secondary_objectives[order_secondary[1]].name] = copy(sub_problem.objective.value())
        # Create solution object
        solution = Solution(model.objectives, model.variables, self.write_report(sub_problem))
        return solution

    def compute_all_individual_optima(self):
        self.individual_optima = []
        for i in range(self.num_objectives()):
            solution = copy(self.compute_individual_optima(i))
            self.individual_optima.append(solution)
        return self.individual_optima
    
    def anti_ideal_point(self):
        if self.anti_ideal_point_attribute is None:
            anti_ideal_point = np.zeros(self.num_objectives())
            sense_original = self.model.pulp_model.sense
            for o in range(self.num_objectives()):
                objective = self.model.objectives[o]
                sub_problem = copy(self.model.pulp_model)
                sub_problem.sense = -sense_original # if original problem is minimization, we need to maximize the objective and vice versa
                sub_problem.setObjective(objective)
                sub_problem.solve(pulp.HiGHS(msg=0))
                anti_ideal_point[o] = objective.varValue
            self.anti_ideal_point_attribute = anti_ideal_point
        return self.anti_ideal_point_attribute
    
    def payoff_matrix(self):
        # Compute individual optima if not already computed
        if self.individual_optima == []:
            self.compute_all_individual_optima()
        # Compute payoff table
        payoff_matrix = np.array([[solution.objective_values()[j] for j in range(self.num_objectives())] for solution in self.individual_optima])
        return payoff_matrix
    
    def ideal_point(self):
        return np.min(self.payoff_matrix(), axis=0)
    
    def nadir_point(self):
        return np.max(self.payoff_matrix(), axis=0)
    
    def normalize_model(self):
        model = copy(self.model)
        ideal_point = self.ideal_point()
        nadir_point = self.nadir_point()
        new_objective_variables = []
        # Create a new variable and constraint for each objective
        for i in range(len(model.objectives)):
            # Get the original objective function
            objective = self.model.objectives[i]
            # Create new variable
            new_objective_variable = pulp.LpVariable(f'norm_{objective.name}', lowBound=0, upBound=1, cat='Continuous')
            new_objective_variables.append(new_objective_variable)
            # Create new constraint to define the normalized objective function
            model.pulp_model += new_objective_variable == (objective - ideal_point[i]) / (nadir_point[i] - ideal_point[i]), f'Normalization_{objective.name}'
        model.objectives = new_objective_variables
        return model

    def denormalizing_vectors(self):
        vectors = []
        for i in range(len(self.model.objectives)):
            # Get the original objective function
            vectors.append([(self.ideal_point()[i] + self.nadir_point()[i]), self.ideal_point()[i]]) 
        return vectors
    
    def write_report(self, pulp_prob):
        report = {'name': pulp_prob.name,
                'solver': pulp_prob.solver.name,
                'objective': pulp_prob.objective,
                'num_variables': len(pulp_prob.variables()),
                'num_constraints': len(pulp_prob.constraints),
                'solutionTime': pulp_prob.solutionTime,
                'solutionCpuTime': pulp_prob.solutionCpuTime,
                'status': pulp_prob.status,
                'sol_status': pulp_prob.sol_status,
                'noOverlap': pulp_prob.noOverlap}
        return report