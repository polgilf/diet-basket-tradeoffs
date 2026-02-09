'''
This class defines a Food Baskets MOLP object and have specific methods to analyze food baskets in a MOLP model
'''
import os
import sys
import numpy as np
import pandas as pd
import pickle
from copy import copy, deepcopy
from matplotlib import pyplot as plt

# Adding classes directory to module search path (sys.path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'classes')))

from FOODBASKET import FoodBasket

class MultipleFoodBaskets():
    def __init__(self, nbi):
        self.population_group = deepcopy(nbi.model.population_group)
        self.region = deepcopy(nbi.model.region)
        self.data = nbi.model.data
        self.model = deepcopy(nbi.model)
        self.nbi = deepcopy(nbi)

    def multiple_baskets_dict(self):
        '''
        This method returns a dictionary with the food baskets and their corresponding values.
        '''
        food_baskets_dict = {}
        for sol_id, solution in self.nbi.efficient_solutions_dict().items():
            food_basket = FoodBasket(sol_id, self.model, solution)
            food_baskets_dict[sol_id] = food_basket
        return food_baskets_dict

    def multiple_baskets_list(self):
        '''
        This method returns a list with the food baskets (food basket object).
        '''
        return list(self.multiple_baskets_dict().values())
    
    def multiple_baskets_composition_dict(self):
        '''
        Returns a dictionary with the food basket id as key and the food basket composition (dictionary of food items and their amounts) as value.
        '''
        return {sol_id: food_basket.basket_composition_dict() for sol_id, food_basket in self.multiple_baskets_dict().items()}
    
    def multiple_baskets_composition_df(self, fillna=None):
        '''
        Returns a dataframe with the food basket id as column and the food items as index. It uses food_basket.basket_composition_df() merging all columns
        '''
        food_baskets_df = pd.DataFrame()
        for basket_id, food_basket in self.multiple_baskets_dict().items():
            basket_df = food_basket.basket_composition_df()
            basket_df.columns = [basket_id]
            food_baskets_df = pd.concat([food_baskets_df, basket_df], axis=1)
        if fillna is not None:
            food_baskets_df = food_baskets_df.fillna(fillna)
        return food_baskets_df
    
    def multiple_baskets_method_dict(self, method):
        '''
        Returns a dictionary with the food basket id as key and the return of the method of the food basket
        For example, if method='basket_food_subgroups_dict' it returns a dictionary with the food basket id as key and dictionary that returns food_basket.basket_food_subgroups_dict() as value
        '''
        food_baskets_dict = {}
        for sol_id, solution in self.nbi.efficient_solutions_dict().items():
            food_basket = FoodBasket(sol_id, self.model, solution)
            food_baskets_dict[sol_id] = getattr(food_basket, method)()
        return food_baskets_dict
    
    def multiple_baskets_method_df(self, method, fillna=None):
        '''
        Returns a dataframe with the food basket id as column and the dataframe that returns the method of the food basket merging all columns
        For example, if method='basket_food_subgroups_df' it returns a df with the food basket id as colname, concatenating the dataframes that returns food_basket.basket_food_subgroups_df()
        IMPORTANT: method must return a dataframe
        '''
        food_baskets_df = pd.DataFrame()
        for basket_id, food_basket in self.multiple_baskets_dict().items():
            basket_df = getattr(food_basket, method)()
            basket_df.columns = [basket_id]
            food_baskets_df = pd.concat([food_baskets_df, basket_df], axis=1)
        if fillna is not None:
            food_baskets_df = food_baskets_df.fillna(fillna)
        return food_baskets_df
    #-------------------------------------------------------------------------#
    # Methods to export the results
    #-------------------------------------------------------------------------#
    def export_to_pickle(self, route):
        '''
        Export the RNBI object to a pickle file
        '''
        with open(route, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)