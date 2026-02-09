'''
Food Basket MODEL class
'''
import pulp

class Model():
    '''
    This class creates a concrete multi-objective linear programming model for diet optimization using the PuLP library.
    '''
    def __init__(self, data, population_group, region):
        self.data = data # Data object
        self.population_group = population_group
        self.region = region

        self.pulp_model = None # Defined in create_model()
        self.objectives = None # Defined in create_model()
        self.original_objectives = None # Defined in create_model()
        self.variables = None # Defined in get_variables()

        # Create the model
        self.create_model(population_group, region)

    def create_model(self, population_group, region):    
        # SETS AND PARAMETERS
        I = self.data.I_c(region)
        N = self.data.N
        G = self.data.G
        S = self.data.S
        I_g = self.data.I_g(region)
        I_s = self.data.I_s(region)
        a = self.data.a # nutritional supply for each 100 g of food item
        c = self.data.c(region)
        f = self.data.f
        p = self.data.p
        p_sign = self.data.p_sign
        afe_factor = self.data.afe_factor(population_group) # Age factor for energy intake
        
        # Current consumption data (already scaled by AFE factor)
        q_lower = self.data.q_lower(population_group, region) #Current consumption lower limit (5th percentile)
        q_upper = self.data.q_upper(population_group, region) #Current consumption upper limit (95th percentile)
        q_mean = self.data.q_mean(population_group, region) # Current consumption mean
        q_median = self.data.q_median(population_group, region) # Current consumption median (50th percentile)
        q_std = self.data.q_std(population_group, region) # Current consumption standard deviation

        # Lower and upper limits
        b_lower = self.data.b_lower(population_group)
        b_upper = self.data.b_upper(population_group)
        S_lower = self.data.S_lower(population_group, region)
        S_upper = self.data.S_upper(population_group, region)
        offal_food_items = self.data.offal_food_items
        fg_lower = self.data.fg_lower # Total quantity of food groups lower limit
        fsg_lower = self.data.fsg_lower # Total quantity of food subgroups lower limit
        fsg_importance = self.data.fsg_importance # Food subgroup importance (1-5, 5 being the most important)

        
        # Modify lower limits of food subgroups based on food subgroup importance
        q_lower_mod = {}
        for s in S:
            if s in S_lower:
                q_lower_mod[s] = q_lower[s] + fsg_importance[s]*(q_median[s] - q_lower[s])
            elif fsg_importance[s] > 0:
                S_lower.append(s) # If the food subgroup is not in S_lower, add it to S_lower
                q_lower_mod[s] = fsg_importance[s]*q_median[s]# Increase lower limit by a % of the difference between the median and lower limit, based on the food subgroup importance

        #q_lower_mod = q_lower
        
        # Global parameters
        self.I = I
        self.S_lower = S_lower
        self.S_upper = S_upper
        
        # MODEL
        self.pulp_model = pulp.LpProblem('molp-food-basket', pulp.LpMinimize)

        # DECISION VARIABLES
        self.x = pulp.LpVariable.dicts('x', I, lowBound=0, cat='Continuous') # Amount of each food item
        self.z_lower = pulp.LpVariable.dicts('z_lower', S_lower, lowBound=0, cat='Continuous') # Deviation from the lower limit of the food subgroup
        self.z_upper = pulp.LpVariable.dicts('z_upper', S_upper, lowBound=0, cat='Continuous') # Deviation from the upper limit of the food subgroup
        self.y = pulp.LpVariable.dicts('y', S, cat='Binary') # Binary variable to force that only one of the z_lower or z_upper is greater than 0

        # OBJECTIVES (defined as variables and constraints)
        self.f1 = pulp.LpVariable('Cost (KHR.day)', cat='Continuous') # Total cost of the food basket
        self.f2 = pulp.LpVariable('Dietary-shift index (unitless)', cat='Continuous') # Mean deviation from current intake in standard deviation units
        self.f3 = pulp.LpVariable('CO2e (Kg.day)', cat='Continuous') # Total greenhouse gas emissions of the food basket

        # (1) Total cost
        self.pulp_model += self.f1 == pulp.lpSum([c[i]*self.x[i] for i in I]), 'Cost (KHR.day)'

        # (2) Mean deviation from current intake (5th and 95th percentiles) of each food subgroup, in standard deviation units
        self.pulp_model += self.f2 == (1/len(S))*(pulp.lpSum([(1/(q_std[s]))*self.z_lower[s] for s in S_lower]) + \
                                                      pulp.lpSum([(1/(q_std[s]))*self.z_upper[s] for s in S_upper])), 'Dietary-shift index (unitless)'
        
        # (3) Total greenhouse gas emissions of the food basket
        self.pulp_model += self.f3 == (1/1000)*pulp.lpSum([f[i]*self.x[i] for i in I]), 'CO2e (Kg.day)'

        # CONSTRAINTS
        # (4) Nutritional adequacy lower limits
        for n in N:
            if n in b_lower:
                self.pulp_model += (1/100)*pulp.lpSum([a[i][n]*self.x[i] for i in I]) >= b_lower[n], f'nutrient_{n}_lower'

        # (5) Nutritional adequacy upper limits
            if n in b_upper:
                self.pulp_model += (1/100)*pulp.lpSum([a[i][n]*self.x[i] for i in I]) <= b_upper[n], f'nutrient_{n}_upper'

        # (6) Food subgroup deviation from current consumption lower limit
        for s in S_lower:
            self.pulp_model += pulp.lpSum([self.x[i] for i in I_s[s]]) + self.z_lower[s] >= q_lower_mod[s], f'food_subgroup_{s}_lower'

        # (7) Food subgroup deviation from current consumption upper limit
        for s in S_upper:
            self.pulp_model += pulp.lpSum([self.x[i] for i in I_s[s]]) - self.z_upper[s] <= q_upper[s], f'food_subgroup_{s}_upper'

        # (*) Only one of the z_lower or z_upper can be greater than 0 (theoretically f2 already forces this, but results showed some solutions with both greater than 0)
        for s in S_lower:
            self.pulp_model += self.z_lower[s] <= 10000*self.y[s], f'food_subgroup_{s}_y_z_lower'
        for s in S_upper:
            self.pulp_model += self.z_upper[s] <= 10000*(1-self.y[s]), f'food_subgroup_{s}_y_z_upper'

        # (8) Healthy food basket constraints (energy contribution of food groups)
        for g in G:
            if g in p_sign['<']:
                self.pulp_model += pulp.lpSum([a[i]['Energy (kcal)']*self.x[i] for i in I_g[g]]) <= p[g]*pulp.lpSum([a[i]['Energy (kcal)']*self.x[i] for i in I]), f'food_group_{g}_lower'
            elif g in p_sign['>']:
                self.pulp_model += pulp.lpSum([a[i]['Energy (kcal)']*self.x[i] for i in I_g[g]]) >= p[g]*pulp.lpSum([a[i]['Energy (kcal)']*self.x[i] for i in I]), f'food_group_{g}_upper'

        # (9) Limit offal to 10 g maximum
        for i in offal_food_items:
            self.pulp_model += self.x[i] <= afe_factor*10, f'offal_{i}_limit'

        # (10) Lower limit of total quantity of food groups
        for g in G:
            self.pulp_model += pulp.lpSum([self.x[i] for i in I_g[g]]) >= afe_factor*fg_lower[g], f'food_group_{g}_lower_limit'

        # (11) Lower limit of total quantity of food subgroups
        if True:
            for s in S:
                self.pulp_model += pulp.lpSum([self.x[i] for i in I_s[s]]) >= afe_factor*fsg_lower[s], f'food_subgroup_{s}_lower_limit'
        

        # DEFINE OBJECTIVES AND VARIABLES ATTRIBUTES
        self.objectives = [self.f1, self.f2, self.f3]
        self.original_objectives = [self.f1, self.f2, self.f3]
        self.variables = [self.x[i] for i in I] + [self.z_lower[s] for s in S_lower] + [self.z_upper[s] for s in S_upper]
    
    # METHODS
    def limit_cost(self, cost_limit):
        """Add a constraint to limit the total cost of the food basket."""
        self.pulp_model += self.f1 <= cost_limit, 'total_cost_limit'

    def limit_deviation_from_consumption(self, deviation_limit):
        """Add a constraint to limit the total deviation from the current consumption of the food basket."""
        self.pulp_model += self.f2 <= deviation_limit, 'total_deviation_limit'

    def limit_co2e(self, co2e_limit):
        """Add a constraint to limit the total CO2e of the food basket."""
        self.pulp_model += self.f3 <= co2e_limit, 'total_co2e_limit'

    def set_objective_limits(self, objective_upper_bounds_dict):
        # Set upper bounds for the objective functions if specified
        for key, value in objective_upper_bounds_dict.items():
            if key == 'Cost (KHR/day)' and value is not None:
                self.limit_cost(value)
            if key == 'Dietary-shift index (unitless)' and value is not None:
                self.limit_deviation_from_consumption(value)
            if key == 'CO2e (Kg/day)' and value is not None:
                self.limit_co2e(value)