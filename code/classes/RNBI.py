import os
import sys
import pulp
import math
import time
import numpy as np
import pandas as pd
import pickle
from copy import deepcopy, copy
from matplotlib import pyplot as plt

# Adding src directory to module search path (sys.path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'classes')))

from SOLUTION import Solution
from MODEL import Model
from MOLP import Molp
from utils import distribute_line_points, distribute_triangle_points

class RNBI():
    '''
    This class implements the RNBI (Revised Normal Boundary Intersection) method for multi-objective linear programming problems.
    
    The cutting points parameter defines the number of evenly distributed reference points along the line (for bi-objective problems)
    or the number of points along each edge of the triangle (for tri-objective problems).
    '''
    def __init__(self, model, cutting_points=None, normalize=True, plane_point='nadir'):
        self.method = 'RNBI'
        self.original_model = copy(model)
        self.cutting_points = cutting_points
        self.normalize = normalize
        self.plane_point = plane_point
        self.reference_point = None

        # Attributes to store execution times
        self.total_execution_time = None
        self.total_execution_cputime = None

        # Initialize attributes for the RNBI algorithm
        self.original_molp = Molp(model)
        # Set the model to apply RNBI
        if self.normalize:
            # Normalize the model
            self.model = self.original_molp.normalize_model()
        else:
            self.model = self.original_molp.model
        # Set the Molp object with the model to apply RNBI
        self.molp = Molp(self.model)
        # Compute individual optima
        self.molp.compute_all_individual_optima()
        self.original_molp.compute_all_individual_optima()
        # Set the reference point
        if self.plane_point == 'nadir':
            self.reference_point = self.molp.nadir_point()
        elif self.plane_point == 'anti-ideal':
            self.reference_point = self.molp.anti_ideal_point()
        else:
            raise ValueError("Invalid reference point. Choose 'nadir' or 'anti-ideal'.")
        
        #---------------------------------------------------------------------#
        # RNBI method
        #---------------------------------------------------------------------#
        start_time = time.time()
        start_cputime = time.process_time()

        # Compute and set the beta value
        self.beta_value = self.compute_beta_value()
        # Compute and set the reference plane points
        self.reference_plane_points = self.compute_reference_plane_points()
        # Compute and set the reference points (used to produce the solutions)
        self.reference_points_dict = self.compute_reference_points()
        # Run the RNBI algorithm
        self.RNBI_algorithm()
        # Check dominance
        self.check_dominance()
        #self.bypass_dominance()  # Bypass dominance check for testing purposes
        # Store execution time in seconds
        self.total_execution_time = round(time.time() - start_time, 2)
        # Store execution time in CPU time
        self.total_execution_cputime = round(time.process_time() - start_cputime, 2)


    #-------------------------------------------------------------------------#
    # Methods to run the RNBI algorithm
    #-------------------------------------------------------------------------#
    def compute_beta_value(self):
        '''
        Beta value is the manhattan distance of the solution closest to the origin
        '''
        sub_problem = copy(self.model.pulp_model)
        # Set the objective to minimize the sum of all objectives
        sum_y = pulp.LpVariable("sum_y", 0, None)
        sub_problem.setObjective(sum_y)
        sub_problem.sense = pulp.LpMinimize
        sub_problem += sum_y == sum([o for o in self.model.objectives])
        # Solve the problem
        sub_problem.solve(pulp.HiGHS(msg=0))
        # Set beta value
        return sum_y.value()
    
    def compute_reference_plane_points(self):
        '''
        Compute the reference plane points for the RNBI algorithm: The points that define the reference plane
        '''
        p = len(self.model.objectives)
        beta = self.beta_value
        e = np.ones(p) # Normal vector
        eTv0 = np.dot(e, self.reference_point) # Dot product of the normal vector and the reference point (nadir or anti-ideal)
        # Define p points for k=1,2,...,p
        v = np.zeros((p, p))
        for k in range(p): # Points
            for l in range(p):
                if k != l:
                    v[k][l] = self.reference_point[l]
                else:
                    v[k][l] = beta + self.reference_point[k] - eTv0
        return v

    def compute_reference_points(self):
        '''
        Compute the reference points for the RNBI algorithm: The points used to produce the solutions (for each subproblem)
        '''
        # Bi-objective problems
        if len(self.model.objectives) == 2:
            # Compute the reference points for the bi-objective problem
            A = self.reference_plane_points[0]
            B = self.reference_plane_points[1]
            ref_points_dict = distribute_line_points(A, B, self.cutting_points)
            ref_points_dict = {f'q{i+1}': ref_points_dict[i] for i in range(ref_points_dict.shape[0])}
        # Tri-objective problems
        elif len(self.model.objectives) == 3:
            # Compute the reference points for the tri-objective problem
            A = self.reference_plane_points[0]
            B = self.reference_plane_points[1]
            C = self.reference_plane_points[2]
            ref_points_dict = distribute_triangle_points(A, B, C, self.cutting_points)
            ref_points_dict = {f'q{i+1}': ref_points_dict[i] for i in range(ref_points_dict.shape[0])}
        return ref_points_dict

    def solve_RNBI_subproblem(self, ref_point):
        '''
        Solve the RNBI subproblem for a given reference point
        '''
        # Create a copy of the original model
        sub_problem = deepcopy(self.model.pulp_model)
        # Define the normal vector (ones vector)
        e = np.ones(len(self.model.objectives))
        # Create a variable for the t value (distance to the reference point)
        t = pulp.LpVariable("t", 0, None)
        # Set the objective function to minimize the distance to the reference point
        sub_problem.setObjective(t)
        # Add the constraint to define the distance to the reference point
        for i in range(len(self.model.objectives)):
            sub_problem += ref_point[i] + t * e[i] == self.model.objectives[i]
        # Solve the problem
        sub_problem.solve(pulp.HiGHS(msg=0))
        #sub_problem.solve(pulp.PULP_CBC_CMD(msg=0))
        # If the solution is not feasible return 'Infeasible'
        if pulp.LpStatus[sub_problem.status] == 'Infeasible':
            return 'Infeasible', 'Infeasible'
        # If feasible create a solution object
        else:
            # Variable values
            variable_values = []
            for varaible in self.model.variables:
                variable = sub_problem.variablesDict()[varaible.name]
                variable_values.append(variable)
            original_objectives = []
            for objective in self.model.original_objectives:
                objective = sub_problem.variablesDict()[objective.name]
                original_objectives.append(objective)
            solved_objectives = []
            for objective in self.model.objectives:
                objective = sub_problem.variablesDict()[objective.name]
                solved_objectives.append(objective)
            # Solution in space where is solved
            solution = Solution(solved_objectives, variable_values, report=self.molp.write_report(sub_problem))
            solution.sol_id = ref_point
            # Solution in the original space
            solution_original = Solution(original_objectives, variable_values, report=self.molp.write_report(sub_problem))
            solution_original.sol_id = ref_point
            return solution, solution_original
        
    def RNBI_algorithm(self):
        '''
        Run the RNBI algorithm to solve the multi-objective linear program
        Beta value, reference plane points and reference points are computed in the constructor
        '''
        # Solve the RNBI subproblems for each reference point
        self.all_solutions_dict = {}
        self.all_solutions_status = {}
        self.all_solutions_original = {}

        # Add the extreme points to the reference points dictionary
        original_extreme_points = self.original_molp.individual_optima
        normalized_extreme_points = self.molp.individual_optima
        
        for i in range(1,self.original_molp.num_objectives() + 1):
            self.all_solutions_dict[f'e{i}'] = normalized_extreme_points[i-1]
            self.all_solutions_status[f'e{i}'] = 'Efficient'
            self.all_solutions_original[f'e{i}'] = original_extreme_points[i-1]

        # Iterate over the reference points
        for ref_id, ref_point in self.reference_points_dict.items():
            solution, solution_original = self.solve_RNBI_subproblem(ref_point)
            if solution == 'Infeasible':
                self.all_solutions_status[ref_id] = 'Infeasible'
                self.all_solutions_dict[ref_id] = None
                self.all_solutions_original[ref_id] = None
            else:
                self.all_solutions_status[ref_id] = 'Feasible'
                self.all_solutions_dict[ref_id] = solution
                self.all_solutions_original[ref_id] = solution_original
    
    def check_dominance(self):
        for ref_id, solution in self.all_solutions_original.items():
            if solution is not None and not ref_id.startswith('e') and self.all_solutions_status[ref_id] != 'Infeasible':
                candidate_sol = copy(solution.objective_values())
                dominance_problem = deepcopy(self.original_model.pulp_model)
                lam = np.ones(self.original_molp.num_objectives())
                # Set objective and sense
                obj = pulp.LpVariable("obj", lowBound=0, cat='Continuous')
                dominance_problem.setObjective(obj)
                dominance_problem.sense = pulp.LpMinimize
                dominance_problem += obj == pulp.lpSum([lam[i] * self.original_model.objectives[i] for i in range(len(self.original_model.objectives))]), "Dominance objective"
                # Constraints
                for i in range(len(self.original_model.objectives)):
                    dominance_problem += self.original_model.objectives[i] <= candidate_sol[i], f"Dominance_constraint_{i}"
                dominance_problem.solve()
                #dominance_problem.solve(pulp.HiGHS(msg=0))
                # Check if the solution is non-dominated
                optimal_objective_value = obj.value()
                candidate_weighted_sum = sum(lam[i] * candidate_sol[i] for i in range(len(candidate_sol)))
                non_dominated = math.isclose(optimal_objective_value, candidate_weighted_sum, rel_tol=1e-6)
                if non_dominated:
                    self.all_solutions_status[ref_id] = 'Efficient'
                else:
                    self.all_solutions_status[ref_id] = 'Dominated'

    def bypass_dominance(self):
        '''
        Bypass the dominance check by setting all solutions to 'Efficient'
        '''
        for ref_id, solution in self.all_solutions_original.items():
            if solution is not None and not ref_id.startswith('e'):
                self.all_solutions_status[ref_id] = 'Efficient'

    #-------------------------------------------------------------------------#
    # Methods to access the solutions
    #-------------------------------------------------------------------------#
    def efficient_normalized_solutions_dict(self):
        '''
        Return the efficient solutions dictionary (if normalized .objective_values() are in the normalized space)
        '''
        sol_dict = {ref_id: solution for ref_id, solution in self.all_solutions_dict.items() if self.all_solutions_status[ref_id] == 'Efficient'}
        # Sort
        sorted_dict = dict(sorted(sol_dict.items(), key=lambda item: (item[1].objective_values()[1], item[1].objective_values()[0]), reverse=False))
        # Rename keys to s1, s2, s3, ... to be consecutive numbers
        new_dict = {}
        for i, (key, value) in enumerate(sorted_dict.items()):
            if key.startswith('e'):
                new_dict[key] = value
            elif not key.startswith('e'):
                new_key = f's{i}'
                new_dict[new_key] = value
        return new_dict 
    
    def efficient_solutions_dict(self):
        '''
        Return the efficient solutions dictionary (original model)
        '''
        sol_dict = {ref_id: solution for ref_id, solution in self.all_solutions_original.items() if self.all_solutions_status[ref_id] == 'Efficient'}
        # Sort
        sorted_dict = dict(sorted(sol_dict.items(), key=lambda item: (item[1].objective_values()[1], item[1].objective_values()[0]), reverse=False))
        # Rename keys to s1, s2, s3, ... to be consecutive numbers        
        new_dict = {}
        for i, (key, value) in enumerate(sorted_dict.items()):
            if key.startswith('e'):
                new_dict[key] = value
            elif not key.startswith('e'):            
                new_key = f's{i}'
                new_dict[new_key] = value
        return new_dict

    def efficient_reference_points(self):
        '''
        Return the reference points that lead to efficient solutions
        IMPORTANT: Reference points are in the normalized space if normalize=True
        '''
        return {ref_id: ref_point for ref_id, ref_point in self.reference_points_dict.items() if self.all_solutions_status[ref_id] == 'Efficient'}
    
    def solution_objectives_dict(self):
        '''
        Return the objectives of the efficient solutions as a dictionary of dictionaries {ref_id: {objective_name: objective_value}}
        IMPORTANT: Objectives are in the original space always
        '''
        solution_dict = self.efficient_solutions_dict()
        solution_objective_values_dict = {ref_id: solution.objective_dict() for ref_id, solution in solution_dict.items()}
        return solution_objective_values_dict
    
    def solution_objective_values_dict(self):
        '''
        Return the objectives of the efficient solutions as a dictionary of lists {ref_id: [objective_value1, objective_value2, ...]}
        IMPORTANT: Objectives are in the original space always
        '''
        solution_dict = self.efficient_solutions_dict()
        solution_objective_values_dict = {ref_id: solution.objective_values() for ref_id, solution in solution_dict.items()}
        return solution_objective_values_dict

    def solution_objectives_df(self):
        '''
        Return the objectives of the efficient solutions as a pandas DataFrame
        IMPORTANT: Objectives are in the original space always
        '''
        solution_objective_values_df = pd.DataFrame(self.solution_objectives_dict()).T
        return solution_objective_values_df
    
    def solution_list(self):
        '''
        Return the efficient solutions as a list of solution objects from efficient_solutions_dict()
        IMPORTANT: Objectives are in the original space always
        '''
        solution_list = [solution for solution in self.efficient_solutions_dict().values()]
        return solution_list
    
    #-------------------------------------------------------------------------#
    # Methods to get the number of solutions of each type
    #-------------------------------------------------------------------------#
    def num_efficient_solutions(self):
        '''
        Return the number of efficient solutions
        '''
        return len([ref_id for ref_id in self.all_solutions_status if self.all_solutions_status[ref_id] == 'Efficient'])
    
    def num_dominated_solutions(self):
        '''
        Return the number of dominated solutions
        '''
        return len([ref_id for ref_id in self.all_solutions_status if self.all_solutions_status[ref_id] == 'Dominated'])
    
    def num_infeasible_solutions(self):
        '''
        Return the number of infeasible solutions
        '''
        return len([ref_id for ref_id in self.all_solutions_status if self.all_solutions_status[ref_id] == 'Infeasible'])
    
    def num_solutions_report(self):
        '''
        Return the number of solutions report as a dictionary
        '''
        total_ref_points = len(self.reference_points_dict)
        return {
            'Reference Points': total_ref_points,
            'Efficient': self.num_efficient_solutions(),
            'Dominated': self.num_dominated_solutions(),
            'Infeasible': self.num_infeasible_solutions(),
            '% Efficient': round(100*self.num_efficient_solutions()/total_ref_points, 3),
            '% Dominated': round(100*self.num_dominated_solutions()/total_ref_points, 3),
            '% Infeasible': round(100*self.num_infeasible_solutions()/total_ref_points, 3),
        }
    #-------------------------------------------------------------------------#
    # Methods to export the results
    #-------------------------------------------------------------------------#
    def export_to_pickle(self, route):
        '''
        Export the RNBI object to a pickle file
        '''
        with open(route, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

                


