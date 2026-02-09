'''
Food Basket class 
'''
import os
import sys
import numpy as np
import pandas as pd
from copy import deepcopy

# Adding classes directory to module search path (sys.path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'classes')))

#from MOLP import Solution
#from MODEL import Model

class FoodBasket():
    '''
    This class defines a Food Basket object for a given population group and region, based on a solution of a diet optimization model.
    '''
    def __init__(self, basket_id, model, solution):
        self.basket_id = basket_id
        self.population_group = deepcopy(model.population_group)
        self.region = deepcopy(model.region)
        self.solution = deepcopy(solution)
        self.data = model.data

    def cost(self):
        return float(self.solution.value_by_name('Cost (KHR.day)'))
    
    def deviation_from_current_consumption(self):
        return float(self.solution.value_by_name('Dietary-shift index (unitless)'))
    
    def co2e(self):
        return float(self.solution.value_by_name('CO2e (Kg.day)'))
    
    def objectives_df(self):
        '''
        Returns a pandas DataFrame with objective values using consistent, human-readable labels.
        '''
        df = pd.DataFrame(self.solution.objective_dict(), index=['Value']).T
        label_map = {
            'Cost_(KHR.day)': 'Cost (KHR/day)',
            'Dietary_shift_index_(unitless)': 'Dietary-shift index (unitless)',
            'CO2e_(Kg.day)': 'CO2e (Kg/day)',
        }
        df.index = df.index.map(lambda name: label_map.get(name, name))
        # Round the values to 3 decimal places
        df = df.round(3)
        return df
    
    def basket_composition_dict_pulp_names(self):
        '''
        Returns a dictionary with the food items (names as in pulp model) and their corresponding quantities in the basket
        '''
        return {key: value for key, value in self.solution.variable_dict_nonzero().items() if key.startswith('x_')}
    
    def basket_composition_dict(self):
        '''
        Returns a dictionary with the food items and their corresponding quantities in the basket
        '''
        basket_composition = self.basket_composition_dict_pulp_names()
        # Values lower than 0.1 are set to Nan
        bc = {key: value if value > 0.01 else np.nan for key, value in basket_composition.items()}
        # Rename all the keys by dropping the 'x_' prefix and substituting the '_' with a space
        return {key[2:].replace('_', ' '): value for key, value in basket_composition.items()}
    
    def basket_composition_df(self):
        '''
        Returns a DataFrame with the food items and their corresponding quantities in the basket
        '''
        basket_composition = self.basket_composition_dict()
        return pd.DataFrame(basket_composition, index=['Quantity (g)']).T

    def basket_food_subgroups_dict(self):
        '''
        Returns a dictionary with the food subgroups and their corresponding quantities in the basket
        '''
        basket_composition = self.basket_composition_dict()
        # Create a dictionary with the food subgroups and their corresponding quantities in the basket, starting with 0 for each subgroup
        food_subgroups = {subgroup: 0 for subgroup in self.data.S}
        I_s = self.data.I_s(self.region)
        for subgroup, food_items_in_subgroup in I_s.items():
            food_subgroups[subgroup] = sum(value for food_item, value in basket_composition.items() 
                                           if food_item in food_items_in_subgroup and not np.isnan(value))
        # Remove food subgroups with 0 quantity
        food_subgroups = {key: value for key, value in food_subgroups.items() if value > 0.01}
        return food_subgroups
    
    def basket_food_subgroups_df(self):
        '''
        Returns a DataFrame with the food subgroups and their corresponding quantities in the basket
        '''
        basket_composition = self.basket_food_subgroups_dict()
        # Sort rows by quantities in descending order: basket_composition = dict(sorted(basket_composition.items(), key=lambda item: item[1], reverse=True))
        # Sort rows by id
        food_subgroups_id = self.data.food_subgroup_id_dict # {food_subgroup_name : id_int}
        basket_composition = dict(sorted(basket_composition.items(), key=lambda item: food_subgroups_id[item[0]]))
        return pd.DataFrame(basket_composition, index=['Quantity (g)']).T
    
    def basket_food_groups_dict(self):
        '''
        Returns a dictionary with the food subgroups and their corresponding quantities in the basket
        '''
        basket_composition = self.basket_composition_dict()
        # Create a dictionary with the food subgroups and their corresponding quantities in the basket, starting with 0 for each subgroup
        food_groups = {group: 0 for group in self.data.G}
        I_g = self.data.I_g(self.region)
        for group, food_items_in_group in I_g.items():
            food_groups[group] = sum(value for food_item, value in basket_composition.items() 
                                           if food_item in food_items_in_group and not np.isnan(value))
        # Remove food subgroups with 0 quantity
        food_groups = {key: value for key, value in food_groups.items() if value > 0.01}
        return food_groups

    def basket_food_groups_df(self):
        '''
        Returns a DataFrame with the food groups and their corresponding quantities in the basket
        '''
        basket_composition = self.basket_food_groups_dict()
        # Sort rows by quantities in descending order: basket_composition = dict(sorted(basket_composition.items(), key=lambda item: item[1], reverse=True))
        # Sort rows by id
        food_groups_id = self.data.food_group_id_dict # {food_group_name : id_int}
        basket_composition = dict(sorted(basket_composition.items(), key=lambda item: food_groups_id[item[0]]))
        return pd.DataFrame(basket_composition, index=['Quantity (g)']).T
    
    def basket_nutritional_supply_dict(self):
        '''
        Returns a dictionary with the nutritional supply of the basket {nutrient: quantity}
        '''
        basket_composition = self.basket_composition_dict()
        nutritional_supply = {nutrient: 0 for nutrient in self.data.N}
        for food_item, quantity in basket_composition.items():
            for nutrient in self.data.N:
                nutritional_supply[nutrient] += self.data.a[food_item].get(nutrient, 0) * quantity
        nutritional_supply = {key: value/100 for key, value in nutritional_supply.items()}
        return nutritional_supply
    
    def basket_nutritional_supply_df(self):
        '''
        Returns a DataFrame with the nutritional supply of the basket
        '''
        nutritional_supply = self.basket_nutritional_supply_dict()
        return pd.DataFrame(nutritional_supply, index=['Content']).T
    
    #-------------------------------------------------------------------------#
    # Methods to get solutions relative to the basket energy supply 
    #-------------------------------------------------------------------------#
    # 1) % of energy supply of each food item, food group and food subgroup
    # 2) basket composition divided by energy supply for each food item, food group and food subgroup (to compare across different population groups)
    # 3) objectives / kcal (to compare across different population groups)
    #-------------------------------------------------------------------------#

    def basket_energy_supply(self):
        '''
        Returns the energy supply (float) of the basket in Kcal
        '''
        return self.basket_nutritional_supply_dict()['Energy (kcal)']
    
    def basket_energy_contribution_food_items_dict(self):
        basket_composition = self.basket_composition_dict()
        energy_contribution = {food_item: self.data.a[food_item]['Energy (kcal)'] * quantity / 100
                               for food_item, quantity in basket_composition.items()}
        return energy_contribution
    
    def basket_energy_contribution_percentage_food_subgroups_dict(self):
        '''
        Returns a dictionary with the food subgroups and their corresponding % of energy contribution in the basket
        '''
        basket_energy_food_items = self.basket_energy_contribution_food_items_dict()
        energy_food_subgroups = {}
        I_s = self.data.I_s(self.region)
        for subgroup, food_items_in_subgroup in I_s.items():
            energy_food_subgroups[subgroup] = sum(basket_energy_food_items[food_item] for food_item in food_items_in_subgroup if food_item in basket_energy_food_items.keys()) / self.basket_energy_supply() * 100
        return energy_food_subgroups
    
    def basket_energy_contribution_percentage_food_subgroups_df(self):
        '''
        Returns a DataFrame with the food subgroups and their corresponding % of energy contribution in the basket
        '''
        energy_food_subgroups = self.basket_energy_contribution_percentage_food_subgroups_dict()
        # Sort rows by quantities in descending order:  energy_food_subgroups = dict(sorted(energy_food_subgroups.items(), key=lambda item: item[1], reverse=True))        
        # Sort rows by id
        food_subgroups_id = self.data.food_subgroup_id_dict # {food_subgroup_name : id_int}
        energy_food_subgroups = dict(sorted(energy_food_subgroups.items(), key=lambda item: food_subgroups_id[item[0]]))
        return pd.DataFrame(energy_food_subgroups, index=['Percentage (%)']).T
    
    def basket_energy_contribution_percentage_food_groups_dict(self):
        '''
        Returns a dictionary with the food groups and their corresponding % of energy contribution in the basket
        '''
        basket_energy_food_items = self.basket_energy_contribution_food_items_dict()
        energy_food_groups = {}
        I_g = self.data.I_g(self.region)
        for group, food_items_in_group in I_g.items():
            energy_food_groups[group] = sum(basket_energy_food_items[food_item] for food_item in food_items_in_group if food_item in basket_energy_food_items.keys()) / self.basket_energy_supply() * 100
        return energy_food_groups
    
    def basket_energy_contribution_percentage_food_groups_df(self):
        '''
        Returns a DataFrame with the food groups and their corresponding % of energy contribution in the basket
        '''
        energy_food_groups = self.basket_energy_contribution_percentage_food_groups_dict()
        # Sort rows by quantities in descending order: energy_food_groups = dict(sorted(energy_food_groups.items(), key=lambda item: item[1], reverse=True))        
        # Sort rows by id
        food_groups_id = self.data.food_group_id_dict # {food_group_name : id_int}
        energy_food_groups = dict(sorted(energy_food_groups.items(), key=lambda item: food_groups_id[item[0]]))    
        return pd.DataFrame(energy_food_groups, index=['Percentage (%)']).T
    

    def objectives_by_kcal_dict(self):
        '''
        Returns a dictionary with the objective values divided by the energy supply of the basket 
        '''
        objectives_dict = self.solution.objective_dict()
        normalized_objectives_dict = {}
        # Add to keys ' / cal' and divide the values by the energy supply of the basket
        for key, value in objectives_dict.items():
            normalized_objectives_dict[key + ' / kcal'] = value / self.basket_energy_supply()
        return normalized_objectives_dict
    
    def objectives_by_kcal_df(self):
        '''
        Returns a DataFrame with the objective values divided by the energy supply of the basket 
        '''
        df = self.objectives_df() / self.basket_energy_supply()
        # Add to the index ' / kcal'
        df.index = df.index + ' / kcal'
        return df

    def basket_composition_by_kcal_dict(self):
        '''
        Returns a dictionary with the food items and their corresponding quantities in the basket divided by the energy supply of the basket 
        '''
        basket_composition = self.basket_composition_dict()
        # Divide the values by the energy supply of the basket
        return {key: value / self.basket_energy_supply() for key, value in basket_composition.items()}
    
    def basket_composition_by_kcal_df(self):
        '''
        Returns a DataFrame with the food items and their corresponding quantities in the basket divided by the energy supply of the basket 
        '''
        df = self.basket_composition_df() / self.basket_energy_supply()
        # Add to the index ' / kcal'
        df.index = df.index + ' / kcal'
        return df
