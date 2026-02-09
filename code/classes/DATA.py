'''
Food Basket DATA class
'''
import os
import sys
import pandas as pd
import numpy as np

class Data():
    '''
    This class loads and processes all data required for the diet optimization model.
    '''
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.load_data()

    def load_data(self):
        # READ DATA
        # FOOD ITEMS: food_items_df 
        food_items_df = pd.read_excel(os.path.join(self.data_dir, 'food_items_match.xlsx'), index_col=0, header=0)
        food_items_df.drop(columns='Comments', inplace=True)
        self.food_items_df = food_items_df

        # IDs of food items, food groups and food subgroups
        self.food_items_id_dict = food_items_df.loc[:, ['food_id', 'food_name']].set_index('food_name').to_dict()['food_id']
        self.food_group_id_dict = food_items_df.loc[:, ['food_group_id', 'food_group_name']].set_index('food_group_name').to_dict()['food_group_id']
        self.food_subgroup_id_dict = food_items_df.loc[:, ['food_subgroup_id', 'food_subgroup_name']].set_index('food_subgroup_name').to_dict()['food_subgroup_id']

        # NUTRIENTS: nutrient_match_df 
        nutrient_match_df = pd.read_excel(os.path.join(self.data_dir, 'nutrient_match.xlsx'), index_col=0, header=0)

        # FOOD GROUPS ENERGY CONTRIBUTION: food_group_percentages_df
        food_group_percentages_df = pd.read_excel(os.path.join(self.data_dir, 'food_group_percentages.xlsx'), index_col=0, header=0)

        # FOOD NUTRITIONAL VALUES: food_nutritional_values_df
        food_nutritional_values_df = pd.read_excel(os.path.join(self.data_dir, 'food_nutritional_composition.xlsx'), index_col=0, header=0)

        # FOOD PRICES: food_prices_df (food_prices.xlsx in processed-data)
        food_prices_df = pd.read_excel(os.path.join(self.data_dir, 'food_prices.xlsx'), index_col=0, header=0)

        # FOOD ENVIRONMENTAL: food_environmental_df
        food_environmental_df = pd.read_excel(os.path.join(self.data_dir, 'food_environmental.xlsx'), index_col=0, header=0)

        # POPULATION GROUPS NUTRITIONAL REQUIREMENTS: nutritional_requirements_df
        nutritional_requirements_df = pd.read_excel(os.path.join(self.data_dir, 'nutritional_requirements.xlsx'), sheet_name='population_groups', index_col=0, header=[0,1])

        # REGIONAL FOOD CONSUMPTION: food_consumption_df
        self.food_consumption_df = pd.read_excel(os.path.join(self.data_dir, 'food_consumption.xlsx'), index_col=0, header=0)

        # POPULATION GROUPS AFE FACTORS: afe_factors_df
        self.afe_factors_df = pd.read_excel(os.path.join(self.data_dir, 'afe_factors.xlsx'), index_col=0, header=0)

        # Offal food items
        self.offal_food_items = pd.read_excel(os.path.join(self.data_dir, 'offal_food_items.xlsx'), index_col=None, header=0)['food_name'].to_list()

        # Lower limits to food groups
        self.food_group_lower_limits = pd.read_excel(os.path.join(self.data_dir, 'food_group_lower_limits.xlsx'), index_col=0, header=0)

        # Lower limits to food subgroups
        self.food_subgroup_lower_limits = pd.read_excel(os.path.join(self.data_dir, 'food_subgroup_lower_limits.xlsx'), index_col=0, header=0)

        # Importance of food subgroups to narrow the lower limit
        self.food_subgroup_importance = pd.read_excel(os.path.join(self.data_dir, 'food_subgroup_importance.xlsx'), index_col=0, header=0)

        # Current environmental impact (for food basket comparison)
        self.current_environmental_impact_df = pd.read_excel(os.path.join(self.data_dir, 'current_environmental_impact.xlsx'), index_col=0, header=0)

        # Current food expenditure
        self.current_food_expenditure_df = pd.read_excel(os.path.join(self.data_dir, 'current_food_expenditure.xlsx'), index_col=0, header=0)

        # DATA STRUCTURES

        # Sets
        # Nutrient list (N)
        self.N = nutrient_match_df.index.to_list()

        # Food items list (I)
        self.I = food_items_df['food_name'].to_list()

        # Food groups list (G)
        self.G = food_group_percentages_df.index.to_list()

        # Food subgroups list (S)
        self.S = list(set(food_items_df['food_subgroup_name']))

        # Nutritional values of food items (I): food_name is the key, and the value is a dictionary with the nutritional values nutrients as keys
        food_nutritional_values_df_mod = food_nutritional_values_df.set_index('food_name')
        self.a = food_nutritional_values_df_mod[self.N].to_dict(orient='index')

        # Nutritional requirements of all population groups
        self.b_dict_all_pop = nutritional_requirements_df.T.to_dict()

        # Food prices of all regions
        self.food_prices_df = food_prices_df.set_index('food_name')

        # Environmental impact of food items (I): food_name is the key, and the value is a dictionary with the environmental impact ('total_ghg_co2e') indicators as keys
        self.f = food_environmental_df.set_index('food_name')['total_ghg_co2e'].to_dict()

        # Food group percentages
        self.p = food_group_percentages_df['adj_HDB'].to_dict()

        # p_sign is a dict with 'sign' (that is '<' or '>') as key and list of food groups (index in food_group_percentages_df) as values
        self.p_sign = {'<': [], '>': []}
        for food_group, sign in self.p.items():
            self.p_sign[food_group_percentages_df.loc[food_group, 'sign']].append(food_group)

        self.fg_lower = self.food_group_lower_limits['lower_limit_afe'].to_dict()
        self.fsg_lower = self.food_subgroup_lower_limits['lower_limit_afe'].to_dict()
        self.fsg_importance = self.food_subgroup_importance['importance'].to_dict()

    # METHODS TO ACCESS DATA (SPECIFIC TO THE POPULATION GROUP AND/OR REGIONS)

    # Nutritional requirements of a population group   
    def b_dict(self, population_group):
        return self.b_dict_all_pop[population_group]
    
    # Lower bounds of nutritional requirements of a population group
    def b_lower(self, population_group):
        b_dict = self.b_dict(population_group)
        b_lower = {nutrient: value for (nutrient, limit), value in b_dict.items() if limit == 'RNI' and not np.isnan(value)}
        return b_lower
    
    # Upper bounds of nutritional requirements of a population group
    def b_upper(self, population_group):
        b_dict = self.b_dict(population_group)
        b_upper = {nutrient: value for (nutrient, limit), value in b_dict.items() if limit == 'UL' and not np.isnan(value)}
        return b_upper
    
    # Cost of food items in a region
    def c(self, region):
        return self.food_prices_df[self.food_prices_df['region_name'] == region]['Cost wg (KHR/g)'].to_dict()
    
    # Filter food items that have prices in a region
    def I_c(self, region):
        return [i for i in self.I if i in self.c(region)]

    # Food items of food group g (I_g) dictionary
    def I_g(self, region):
        Ig = {}
        I_c = self.I_c(region)
        for g in self.G:
            Ig[g] = self.food_items_df[(self.food_items_df['food_group_name'] == g) & (self.food_items_df['food_name'].isin(I_c))]['food_name'].to_list()
        return Ig
    
    # Food items of food subgroup s (I_s) dictionary
    def I_s(self, region):
        Is = {}
        I_c = self.I_c(region)
        for s in self.S:
            Is[s] = self.food_items_df[(self.food_items_df['food_subgroup_name'] == s) & (self.food_items_df['food_name'].isin(I_c))]['food_name'].to_list()
        return Is

    # AFE factor of food group
    def afe_factor(self, population_group):
        return float(self.afe_factors_df.loc[population_group, 'AFE_factor'])
    
    # Food consumption of the REGION: food_subgroup_name is the key
    def q_dict(self, region):
        return self.food_consumption_df[self.food_consumption_df['region_name'] == region][['grams_afe_p5','grams_afe_p95','grams_afe_mean','grams_afe_med','grams_afe_sd']].to_dict(orient='index')
    
    # Lower bounds of food consumption of the REGION and POPULATION GROUP
    def q_lower(self, population_group, region):
        q_dict = self.q_dict(region)
        q_lower = {food_subgroup: value['grams_afe_p5']*self.afe_factor(population_group) for food_subgroup, value in q_dict.items()}
        return q_lower
    
    # Upper bounds of food consumption of the REGION and POPULATION GROUP
    def q_upper(self, population_group, region):
        q_dict = self.q_dict(region)
        q_upper = {food_subgroup: value['grams_afe_p95']*self.afe_factor(population_group) for food_subgroup, value in q_dict.items()}
        return q_upper
    
    # Mean food consumption of the REGION and POPULATION GROUP
    def q_mean(self, population_group, region):
        q_dict = self.q_dict(region)
        q_mean = {food_subgroup: value['grams_afe_mean']*self.afe_factor(population_group) for food_subgroup, value in q_dict.items()}
        return q_mean
    
    # Standard deviation of food consumption of the REGION and POPULATION GROUP
    def q_std(self, population_group, region):
        q_dict = self.q_dict(region)
        q_std = {food_subgroup: value['grams_afe_sd'] * self.afe_factor(population_group) for food_subgroup, value in q_dict.items()}

        return q_std
    
    def q_median(self, population_group, region):
        q_dict = self.q_dict(region)
        q_median = {food_subgroup: value['grams_afe_med'] * self.afe_factor(population_group) for food_subgroup, value in q_dict.items()}
        return q_median
    
    # Food subgroups with lower bounds of food consumption
    def S_lower(self, population_group, region):
        q_lower = self.q_lower( population_group, region)
        S_lower = [s for s in self.S if q_lower[s] > 0]
        return S_lower
    
    # Food subgroups with upper bounds of food consumption
    def S_upper(self, population_group, region):
        q_upper = self.q_upper(population_group, region)
        S_upper = [s for s in self.S if q_upper[s] > 0]
        return S_upper
    
    def current_food_subgroup_consumption_dict(self, population_group, region):
        q_dict = self.q_dict(region)
        q_current = {food_subgroup: value['grams_afe_mean']*self.afe_factor(population_group) for food_subgroup, value in q_dict.items()}
        return q_current

    def current_food_subgroup_consumption_df(self, population_group, region):
        q_current = self.current_food_subgroup_consumption_dict(population_group, region)
        q_current_df = pd.DataFrame.from_dict(q_current, orient='index', columns=['grams_afe_mean'])
        q_current_df.index.name = 'food_subgroup'
        # Replace column name 'grams_afe_mean' with 'quantity (grams/day)'
        q_current_df.rename(columns={'grams_afe_mean': 'Current'}, inplace=True)
        return q_current_df
    
    def current_food_subgroup_consumption_df_filtered(self, population_group, region):
        # Only with food subgroups containing food items
        food_subgroups = self.I_s(region).keys()
        q_current_df = self.current_food_subgroup_consumption_df(population_group, region)
        q_current_df_filtered = q_current_df[q_current_df.index.isin(food_subgroups)]
        return q_current_df_filtered
    
    def current_food_subgroup_metrics_df(self, population_group, region):
        q_dict = self.q_dict(region)
        afe_factor = self.afe_factor(population_group)
        q_dict_pop = {food_subgroup : {metric: value * afe_factor for metric, value in quantity_dict.items()} for food_subgroup, quantity_dict in q_dict.items()}
        df = pd.DataFrame(q_dict_pop).T
        # Rename columns
        df.rename(columns={'grams_afe_p5': '5th percentile (grams/day)', 'grams_afe_mean': 'mean (grams/day)', 'grams_afe_med': 'median (grams/day)','grams_afe_p95': '95th percentile (grams/day)', 'grams_afe_sd': 'Std (grams/day)'}, inplace=True)
        return df
    
    def current_food_subgroup_metrics_df_filtered(self, population_group, region):
        df = self.current_food_subgroup_metrics_df(population_group, region)
        # Only with food subgroups containing food items
        food_subgroups = self.I_s(region).keys()
        df_filtered = df[df.index.isin(food_subgroups)]
        return df_filtered
    
    def current_environmental_impact_afe_by_group_df(self, region):
        # region is the index of self.current_environmental_impact_df
        environmental_impact = self.current_environmental_impact_df.loc[region]
        # set food_group as index
        environmental_impact.set_index('food_group', inplace=True)
        return environmental_impact
    
    def current_environmental_impact_afe_total_dict(self, region):
        environmental_impact_by_group_df = self.current_environmental_impact_afe_by_group_df(region)
        # Sum the environmental impact by food group
        environmental_impact_total = environmental_impact_by_group_df.sum(axis=0).to_dict()
        return environmental_impact_total
    
    def current_food_expenditure_afe_by_percentile_df(self, region):
        # region is the index of self.current_food_expenditure_df
        expenditure = self.current_food_expenditure_df.loc[:, region]
        return expenditure
    
    def current_food_expenditure_afe_quartile_dict(self, region):
        expenditure_by_percentile_df = self.current_food_expenditure_afe_by_percentile_df(region)
        # Get the 25th, 50th and 75th percentiles
        expenditure_quartiles = {
            '1th': expenditure_by_percentile_df.loc[1],
            '25th': expenditure_by_percentile_df.loc[25],
            '50th': expenditure_by_percentile_df.loc[50],
            '75th': expenditure_by_percentile_df.loc[75],
            '99th': expenditure_by_percentile_df.loc[99]
        }
        return expenditure_quartiles
    
    def current_food_expenditure_afe_quintile_dict(self, region):
        expenditure_by_percentile_df = self.current_food_expenditure_afe_by_percentile_df(region)
        # Get the 5th, 50th and 95th percentiles
        expenditure_quintiles = {
            '1th': expenditure_by_percentile_df.loc[1],
            '20th': expenditure_by_percentile_df.loc[20],
            '40th': expenditure_by_percentile_df.loc[40],
            '60th': expenditure_by_percentile_df.loc[60],
            '80th': expenditure_by_percentile_df.loc[80],
            '99th': expenditure_by_percentile_df.loc[99]
        }
        return expenditure_quintiles


