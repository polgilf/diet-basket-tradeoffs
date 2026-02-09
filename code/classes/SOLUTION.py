"""Encapsulates an optimization solution with accessors for objective and variable values."""
import numpy as np
from copy import deepcopy, copy


class Solution():
    '''
    This class defines a solution object for a multi-objective linear program.

    Attributes:
    - id: unique identifier
    - objectives: list of objective functions (Pulp variables)
    - variables: list of variables (Pulp variables)

    Methods:
    - objective_values(): returns the values of the objective functions (numpy array)
    - variable_values(): returns the values of the variables (numpy array)
    - objective_dict(): returns a dictionary with the objective values {objective_name: value}
    - variable_dict(): returns a dictionary with the variable values {variable_name: value}
    '''
    def __init__(self, objectives, variables, report=None):
        self.sol_id = None # Unique identifier
        self.objectives = deepcopy(objectives)
        self.variables = deepcopy(variables)
        self.report = deepcopy(report)

    def objective_values(self):
        return np.array([float(obj.value()) for obj in self.objectives])

    def variable_values(self):
        return np.array([float(var.value()) for var in self.variables])
    
    def objective_dict(self):
        return {obj.name: float(obj.value()) for obj in self.objectives}
    
    def variable_dict(self):
        return {var.name: float(var.value()) for var in self.variables}
    
    def variable_dict_nonzero(self):
        return {var.name: float(var.value()) for var in self.variables if var.value() > 0}
    
    def remove_variable(self, variable_to_remove):
        self.variables = [var for var in self.variables if var.name not in variable_to_remove]

    def value_by_name(self, name):
        '''
        Returns the value of an objective or variable by its name.
        If the name contains a space, it replaces it with an underscore.
        '''
        name = name.replace(' ', '_')
        obj_dict = {obj.name: float(obj.value()) for obj in self.objectives}
        var_dict = {var.name: float(var.value()) for var in self.variables}
        combined_dict = {**obj_dict, **var_dict}
        if name in combined_dict:
            return combined_dict[name]
        raise ValueError(f"Name '{name}' not found in objectives or variables.")