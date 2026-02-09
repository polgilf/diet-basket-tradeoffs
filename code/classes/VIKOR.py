"""VIKOR multi-criteria decision-making method for ranking and selecting compromise solutions."""
import pandas as pd
from copy import deepcopy
from collections import Counter
from itertools import permutations

class VIKOR():
    '''
    VIKOR method for multi-criteria decision making.

    v: weight of the strategy of maximum group utility (0 ≤ v ≤ 1).
    S: overall group utility measure vector.
    R: individual regret measure vector.
    Q: measure of closeness to the ideal solution based on S and R.
    '''
    def __init__(self, criteria_values, criteria_weights, v):
        self.criteria_values = criteria_values # df with alternatives as columns and criteria as rows
        self.original_weights = deepcopy(criteria_weights)
        self.v = v
        self.Q = None
        self.S = None
        self.R = None
        self.S_norm = None
        self.R_norm = None


    def compute_S_R_Q(self, criteria_weights):
        # Sort weights to follow the order of the objectives in criteria_values df
        weights = [criteria_weights[c] for c in self.criteria_values.index]
        df = self.criteria_values
        # Compute the ideal and anti-ideal values for each criterion
        f_best_i = df.min(axis=1)
        f_worst_i = df.max(axis=1)
        # Normalize the values
        df_norm = ((f_best_i - df.T) / (f_best_i - f_worst_i)).T
        df_norm_weighted = (df_norm.T * weights).T
        # Compute Sj and Rj
        S_j = df_norm_weighted.sum(axis=0)
        R_j = df_norm_weighted.max(axis=0)
        # Normalize Sj and Rj
        S_norm_j = (S_j - S_j.min()) / (S_j.max() - S_j.min())
        R_norm_j = (R_j - R_j.min()) / (R_j.max() - R_j.min())
        # Compute the Qj
        Q_j = self.v*S_norm_j + (1-self.v)*R_norm_j
        self.S_norm = S_norm_j
        self.R_norm = R_norm_j
        self.S = S_j
        self.R = R_j
        self.Q = Q_j

    def df_S_R_Q(self):
        # return pd.DataFrame({'S': self.S, 'R': self.R, 'Snorm': self.S_norm, 'Rnorm': self.R_norm, 'Q': self.Q}).T
        return pd.DataFrame({'S': self.S, 'R': self.R, 'Q': self.Q}).T
    
    def best_alternative(self, method='Q'):
        if method == 'Q':
            return self.Q.idxmin()
        elif method == 'S':
            return self.S.idxmin()
        elif method == 'R':
            return self.R.idxmin()
    
    def sorted_alternatives(self, method='Q'):
        if method == 'Q':
            return list(self.Q.sort_values(ascending=True).index)
        elif method == 'S':
            return list(self.S.sort_values(ascending=False).index)
        elif method == 'R':
            return list(self.R.sort_values(ascending=False).index)
        
    def sorted_df_S_R_Q(self, method='Q'):
        alternatives = self.sorted_alternatives(method)
        SRQ_df = self.df_S_R_Q()[alternatives]
        # Add a row from 1 to n to represent the ranking (integer)
        SRQ_df.loc['Rank'] = range(1, len(alternatives)+1)
        return SRQ_df
    
    def weight_sensitivity_analysis(self, weights_dict):
        """
        Perform weight sensitivity analysis for the VIKOR method.
        """
        sensitivity_results = {}
        for key, weights in weights_dict.items():
            # Compute the VIKOR method with the new weights
            self.compute_S_R_Q(weights)
            # Recalculate the best alternative using the new weights
            best_alternative = self.best_alternative('Q')
            # Store the result
            sensitivity_results[key] = best_alternative

        list_of_bests = list(sensitivity_results.values())
        #Get the frequency of each element in the list
        frequency = Counter(list_of_bests)
        # Sort the dictionary by value in descending order
        sorted_frequency = dict(sorted(frequency.items(), key=lambda item: item[1], reverse=True))
        
        return sensitivity_results, sorted_frequency
    
    def sensitivity_results_formating_df(self, sensitivity_results):
        # Dict with 'original name' : '%increment of OBJECTIVE NAME' { str : str}
        sensitivity_increments_names = {objective_name : f'% added to weight: {objective_name}' for objective_name in self.original_weights.keys()}
        # Create a list of lists with tuple (key) unpacked as the first elements and the value as the second element
        sensitivity_results_list = []
        for key, value in sensitivity_results.items():
            sensitivity_results_list.append([*key, value])
        # Create a DataFrame from the list of lists
        sensitivity_results_df = pd.DataFrame(sensitivity_results_list, columns=list(sensitivity_increments_names.values())+['Selected basket']).T
        return sensitivity_results_df
    
    def compute_sensitivity_weights(self, criteria_weights_dict=None, percentages_to_change=None):
        if percentages_to_change is None:
            list_of_percentages_to_change = [(+5, -2.5, -2.5), (-5, +2.5, +2.5), (+10, -5, -5), (-10, +5, +5)] #, (+20, -10, -10), (-20, +10, +10)]
        if criteria_weights_dict is None:
            criteria_weights_dict = self.original_weights
        # Create a dict to store all the weight combinations (dict of dicts)
        all_weights_dict = {}
        # Iterate over the percentage changes
        for tuple_of_percentages_to_change in list_of_percentages_to_change:
            weight_permutations = list(set(permutations(tuple_of_percentages_to_change)))
            # Sort by first element of the tuple in descending order
            weight_permutations.sort(key=lambda x: x[0], reverse=True)
            for permutation in weight_permutations:
                # Create a copy of the original weights
                baseline_weights_dict = deepcopy(criteria_weights_dict)
                # Update the weights based on the permutation
                modified_weights_dict = {}
                for i, objective in enumerate(criteria_weights_dict.keys()):
                    modified_weights_dict[objective] = baseline_weights_dict[objective] + permutation[i]/100
                all_weights_dict[permutation] = modified_weights_dict
        # Sort new_weights dict by the third element of the key tuple (ascending order), then by the first element (ascending order)
        sorted_new_weights = dict(sorted(all_weights_dict.items(), key=lambda item: (-item[0][2], -item[0][0])))
        return sorted_new_weights