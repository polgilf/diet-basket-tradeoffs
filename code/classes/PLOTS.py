"""Visualization routines for Pareto fronts, basket compositions, and comparative plots."""
import os
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from adjustText import adjust_text
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from matplotlib.lines import Line2D
def plot_NBI_3D_to_2D_with_color_scale(nbi, objectives_to_use, normalize_scale=False, swap_axes=False, best_alternative=None, title=True, tags=True, export=False):
    objective_values = nbi.solution_objective_values_dict()  # Dict with refpoint_id: [objective_values_of_solution]

    cmap_color = "viridis_r" #'YlGnBu_r'

    # Filter the objective values based on objectives_to_use
    filtered_objective_values = {
        ref_id: [obj for obj, use in zip(obj_values, objectives_to_use) if use]
        for ref_id, obj_values in objective_values.items()}
    # Extract the objective not included in the plot for color scale
    color_values = [
            obj_values[objectives_to_use.index(0)]
            for obj_values in objective_values.values()]
    # Plot the Pareto front
    if not export:
        plt.figure(figsize=(6, 5))
    # Plot solution points with color scale
    if swap_axes == False:
        x = [values[0] for values in filtered_objective_values.values()]
        y = [values[1] for values in filtered_objective_values.values()]
    else:
        x = [values[1] for values in filtered_objective_values.values()]
        y = [values[0] for values in filtered_objective_values.values()]
    if len(objective_values) < 100:
        scatter = plt.scatter(x, y, c=color_values, cmap=cmap_color, edgecolor='black', linewidth=0.5, s=50, zorder=5)
    else:
        scatter = plt.scatter(x, y, c=color_values, cmap=cmap_color, edgecolor='black', linewidth=0.2, s=20, zorder=5)
    # Create text annotations for each point
    if tags:
        texts = []
        y_offset = (plt.ylim()[1] - plt.ylim()[0]) * 0.01  # Use 1% of y-axis range as offset
        for i, (ref_id, values) in enumerate(filtered_objective_values.items()):
            if ref_id == best_alternative:
                texts.append(plt.text(x[i], y[i]+y_offset, str(ref_id), fontsize=9, color='red', weight='bold',
                    ha='center', va='bottom', zorder=7))
            else:
                texts.append(plt.text(x[i], y[i]+y_offset, {'e1':'L_C','e2':'L_DS','e3':'L_E'}.get(ref_id, str(ref_id)), fontsize=9, color='black', #weight='bold',
                        ha='center', va='bottom', zorder=7))
        # Use adjust_text to prevent overlapping
        adjust_text(texts, force_text=(1, 0))
    # Add color bar
    colorbarlabel = nbi.model.original_objectives[objectives_to_use.index(0)].name.replace('_', ' ').replace('.', ' / ')
    cbar = plt.colorbar(scatter) #, label=colorbarlabel)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label(colorbarlabel, fontsize=11)
    xlabel = nbi.model.original_objectives[objectives_to_use.index(1)].name
    ylabel = nbi.model.original_objectives[objectives_to_use.index(1, objectives_to_use.index(1) + 1)].name
    
    # Change '_' to ' ' in the labels and '.' to '/'
    xlabel = xlabel.replace('_', ' ').replace('.', ' / ')
    ylabel = ylabel.replace('_', ' ').replace('.', ' / ')
    plt.xlabel(ylabel if swap_axes else xlabel, fontsize=11)
    plt.ylabel(xlabel if swap_axes else ylabel, fontsize=11)

    xlabel = 'GHGe (kg CO2e / day)' if xlabel == 'CO2e (Kg / day)' else xlabel

    # Set first x value to 1
    plt.xlim(left=1.5)
    # If cost is the ylabel 'Cost' string is in ylabel, then set ylim from 3000 to 12000
    if swap_axes:
        if xlabel == 'Cost (KHR / day)':
            plt.ylim(bottom=3000, top=12000)
        elif xlabel == 'Dietary-shift index (unitless)':
            plt.ylim(bottom=0, top=225)

    # Axis x ticks every 0.5 units
    plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(0.5))
    if title:
        plt.title(str(nbi.num_efficient_solutions()) + ' computed Diet Baskets', fontsize=12)
    plt.grid(True)
    if not normalize_scale:
        plt.gca().set_aspect('equal', adjustable='box')  # Ensure the same scale for x and y axes
    if not export:
        plt.show()


'''
TWO SUBPLOTS OF PARETO FRONT IN 2D FOR 2 OBJECTIVES AND 3RD OBJECTIVE AS COLOR SCALE
'''

def two_plots_NBI_3D_to_2D_with_color_scale(nbi, normalize_scale=True, best_alternative=None, title=True, tags=True, export=False):
    # Create figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    # Set the current axes to first subplot
    plt.sca(ax1)
    plot_NBI_3D_to_2D_with_color_scale(nbi, objectives_to_use=[1,0,1], normalize_scale=normalize_scale, swap_axes=True, best_alternative=best_alternative, title=title, tags=tags, export=True)
    # Set the current axes to second subplot
    plt.sca(ax2)
    plot_NBI_3D_to_2D_with_color_scale(nbi, objectives_to_use=[0,1,1], normalize_scale=normalize_scale, swap_axes=True, best_alternative=best_alternative, title=title, tags=tags, export=True)
    # Adjust layout to prevent overlap
    plt.tight_layout()
    if not normalize_scale:
        plt.gca().set_aspect('equal', adjustable='box')  # Ensure the same scale for x and y axes
    if not export:
        plt.show()
    else:
        return fig


'''
PLOT OF PARETO FRONT IN 2D FOR 2 OBJECTIVES AND 3RD OBJECTIVE AS COLOR SCALE + ADDITIONAL SOLUTIONS + INTERQUARTILE RANGE + BEST SELECTED BASKETS
'''
def plot_NBI_3D_to_2D_complete(nbi, objectives_to_use, best_baskets, colors_baskets, 
                               normalize_scale=False, swap_axes=False, title=False, 
                               tags=True, export=False, additional_solutions=None,
                               interquartile_range=None, fig=None, ax=None):
    
    # Create figure if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
        created_fig = True
    else:
        created_fig = False
    
    # Prepare data
    objective_values = nbi.solution_objective_values_dict()
    if additional_solutions:
        objective_values.update(additional_solutions)
    
    colors_solutions = {solution: colors_baskets[scenario] for scenario, solution in best_baskets.items()}
    filtered_values = {ref_id: [obj for obj, use in zip(obj_values, objectives_to_use) if use] 
                      for ref_id, obj_values in objective_values.items()}
    
    color_index = objectives_to_use.index(0)
    color_values = [obj_values[color_index] for obj_values in objective_values.values()]
    coords = list(filtered_values.values())
    x_coords = [values[1 if swap_axes else 0] for values in coords]
    y_coords = [values[0 if swap_axes else 1] for values in coords]
    
    # Add interquartile range background
    if interquartile_range and len(interquartile_range) == 2:
        ax.axhspan(interquartile_range[0], interquartile_range[1], color='gray', 
                  linewidth=0, alpha=0.25, zorder=1, label='IQR Food Expenditure')
    
    # Plot settings
    vmin, vmax = 0, max(color_values)
    size, edge_width = (50, 0.5) if len(objective_values) < 100 else (20, 0.2)
    nbi_solution_ids = set(nbi.solution_objective_values_dict().keys())
    
    # Plot NBI solutions (circles) and additional solutions (diamonds)
    nbi_indices = [i for i, ref_id in enumerate(filtered_values.keys()) if ref_id in nbi_solution_ids]
    additional_indices = [i for i, ref_id in enumerate(filtered_values.keys()) if ref_id not in nbi_solution_ids]
    
    scatter = None

    cmap_color = "viridis_r" #'YlGnBu' #

    if nbi_indices:
        scatter = ax.scatter([x_coords[i] for i in nbi_indices], [y_coords[i] for i in nbi_indices], 
                           c=[color_values[i] for i in nbi_indices], cmap=cmap_color, vmin=vmin, vmax=vmax, 
                           edgecolor='black', linewidth=edge_width, s=size, zorder=5,
                           label='Generated Diet Baskets')

    if additional_indices:
        additional_scatter = ax.scatter([x_coords[i] for i in additional_indices], [y_coords[i] for i in additional_indices], 
                                      c=[color_values[i] for i in additional_indices], cmap=cmap_color, vmin=vmin, vmax=vmax, 
                                      marker='D', s=size * 0.5, edgecolor='black', linewidth=1, zorder=6,
                                      label='Current and ideal diet baskets')
        if scatter is None:
            scatter = additional_scatter
    
    # Add point labels
    if tags:
        y_offset = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.01
        texts = []
        for i, ref_id in enumerate(filtered_values.keys()):
            if ref_id in best_baskets.values():
                text_color, weight = colors_solutions[ref_id], 'bold'
            elif ref_id not in nbi_solution_ids:
                text_color, weight = 'black', 'bold'
            else:
                text_color, weight = 'black', 'normal'
            
            texts.append(ax.text(x_coords[i], y_coords[i] + y_offset, {'e1': 'L_C', 'e2': 'L_DS', 'e3': 'L_E'}.get(ref_id, str(ref_id)), 
                               fontsize=10, color=text_color, weight=weight,
                               ha='center', va='bottom', zorder=7))
        adjust_text(texts, force_text=(1, 0), ax=ax)
    
    # Setup axis labels and colorbar
    objectives = nbi.model.original_objectives
    x_idx, y_idx = objectives_to_use.index(1), objectives_to_use.index(1, objectives_to_use.index(1) + 1)
    clean_name = lambda name: name.replace('_', ' ').replace('.', ' / ')
    
    # Resolve axis labels (respecting swap_axes)
    x_label = clean_name(objectives[y_idx if swap_axes else x_idx].name)
    y_label = clean_name(objectives[x_idx if swap_axes else y_idx].name)

    # Rename specific labels
    AXIS_LABEL_MAP = {'CO2e (Kg / day)': 'GHGe (kg CO2e / day)'}

    x_label = AXIS_LABEL_MAP.get(x_label, x_label)
    y_label = AXIS_LABEL_MAP.get(y_label, y_label)

    # Apply labels
    ax.set_xlabel(x_label, fontsize=14, labelpad=14)
    ax.set_ylabel(y_label, fontsize=14, labelpad=14)

    # x and y ticks fontsize
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    if scatter is not None:
        colorbarlabel = clean_name(objectives[color_index].name)
        cbar = fig.colorbar(scatter, ax=ax, label=colorbarlabel)
        cbar.ax.tick_params(labelsize=12)
        cbar.set_label(colorbarlabel, fontsize=14, labelpad=14)
    
    # Create legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='none', label='Computed Diet Baskets',
               markerfacecolor='black', markersize=6, linestyle='None'),
        Line2D([0], [0], marker='D', color='none', label='Current and Ideal Baskets',
               markerfacecolor='black', markersize=6, linestyle='None'),
        Line2D([0], [0], marker='s', markersize=12, color='gray', linestyle='None', markeredgewidth=0,
               alpha=0.25, label='IQR Food Expenditure'),
        Line2D([0], [0], color='none', label=''),
        Line2D([0], [0], color='none', label=r'$\mathbf{Selected\ healthy\ diet\ baskets:}$')
    ]
    
    for scenario, color in colors_baskets.items():
        legend_elements.append(Line2D([0], [0], marker='$\\mathbf{s}$', color=color,
                                    label=scenario, markerfacecolor=color, markersize=6, 
                                    linewidth=0, linestyle='None', markeredgewidth=0.1))
    
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.3, 1), loc='upper left', fontsize=12, frameon=False)
    # Axis limits
    plt.xlim(left=1.5, right=6)
    # Axis x ticks every 0.5 units
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.5))
    
    plt.ylim(bottom=3000, top=12000)  # Adjusted for better visibility    
    # Final styling
    if title:
        ax.set_title(f'Discrete set of {nbi.num_efficient_solutions()} Diet Baskets', fontsize=12, pad=20)
    
    ax.grid(True, alpha=0.4)
    if not normalize_scale:
        ax.set_aspect('equal', adjustable='box')
    
    if created_fig and not export:
        plt.tight_layout()
        plt.show()
    
    return fig, ax

'''
PLOT OF FOOD BASKETS COMPOSITION (SUBGROUPS) IN STACKED BAR CHART
'''
def OLD_plot_food_baskets_subgroups(all_baskets_composition_subgroups_df, colors_df, title_label_dict={}, best_alternative=None, export=False):
    '''
    Define title and labels
    '''
    if title_label_dict is {}:
        title = False
        title_name = ''
        xlabel = ''
        ylabel = ''
        legend_title = ''
    else:
        title = True
        title_name = title_label_dict['title']
        xlabel = title_label_dict['xlabel']
        ylabel = title_label_dict['ylabel']
        legend_title = title_label_dict['legend_title']
    '''
    Load data and make the plot
    '''
    plot_data = all_baskets_composition_subgroups_df
    color_dict = colors_df['color_code'].to_dict()
    # Get the ordered list of food categories from df_colors
    ordered_foods = colors_df.index.tolist()
    # Reorder the plot_data DataFrame based on the order in df_colors
    common_foods = [food for food in ordered_foods if food in plot_data.index]
    plot_data = plot_data.loc[common_foods]
    # Create a figure and axis with a larger size for better visibility
    number_of_columns = len(plot_data.columns)
    #fig, ax = plt.subplots(figsize=(6+number_of_columns*0.3, 4))
    fig, ax = plt.subplots(figsize=(12, 5))
    # Create the stacked bar chart
    plot_data.T.plot(kind='bar', stacked=True, ax=ax, 
                    color=[color_dict.get(food, '#333333') for food in plot_data.index])
    # Add labels and title
    if title:
        plt.title(title_name, fontsize=12)
    plt.xlabel(xlabel, fontsize=11)
    plt.ylabel(ylabel, fontsize=11)
    # Add a legend with the food categories
    #plt.legend(title='Food subgroup', bbox_to_anchor=(1.1, 1.1), loc='upper left', fontsize=9)
    plt.legend(title=legend_title, bbox_to_anchor=(-0.2, 1), loc='upper right', fontsize=12)
    # Adjust layout to make room for the legend
    plt.tight_layout()
    # After plotting, get the current tick labels
    solution_names = plot_data.columns.tolist()  # Original column names before transposing
    # Set x-tick labels first
    ax.set_xticklabels(solution_names, rotation=45, fontsize=11, ha='right')
    # Set y-tick labels
    #ax.set_yticklabels(ax.get_yticks(), fontsize=10) #UserWarning: set_ticklabels() should only be used with a fixed number of ticks
    # Highlight the best alternative if specified
    if best_alternative is not None:
        # Now we can modify the tick labels
        for i, sol in enumerate(solution_names):
            if sol == best_alternative:
                # Get the specific label and modify it
                label = ax.get_xticklabels()[i]
                label.set_color('red')
                label.set_fontweight('bold')
                break
    # Show the plot
    if not export:
        plt.show()

def plot_food_baskets_subgroups(all_baskets_composition_subgroups_df, colors_df, title_label_dict={}, best_alternative=None, export=False, ax=None):
    '''
    Define title and labels
    '''
    if title_label_dict is {}:
        title = False
        title_name = ''
        xlabel = ''
        ylabel = ''
        legend_title = ''
    else:
        title = True
        title_name = title_label_dict['title']
        xlabel = title_label_dict['xlabel']
        ylabel = title_label_dict['ylabel']
        legend_title = title_label_dict['legend_title']
    
    '''
    Load data and make the plot
    '''
    plot_data = all_baskets_composition_subgroups_df
    color_dict = colors_df['color_code'].to_dict()
    # Get the ordered list of food categories from df_colors
    ordered_foods = colors_df.index.tolist()
    # Reorder the plot_data DataFrame based on the order in df_colors
    common_foods = [food for food in ordered_foods if food in plot_data.index]
    plot_data = plot_data.loc[common_foods]
    
    # Use provided axes or create new ones
    if ax is None:
        number_of_columns = len(plot_data.columns)
        fig, ax = plt.subplots(figsize=(12, 5))
        created_fig = True
    else:
        created_fig = False
    
    # Create the stacked bar chart
    plot_data.T.plot(kind='bar', stacked=True, ax=ax, 
                    color=[color_dict.get(food, '#333333') for food in plot_data.index])
    
    # Add labels and title
    if title:
        ax.set_title(title_name, fontsize=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    
    # Add a legend with the food categories
    legend = ax.legend(title=legend_title, bbox_to_anchor=(-0.2, 1), loc='upper right', fontsize=11)
    if legend and legend.get_title():
        legend.get_title().set_fontsize(12)
    
    # After plotting, get the current tick labels
    solution_names = plot_data.columns.tolist()
    # Set x-tick labels
    ax.set_xticklabels(solution_names, rotation=45, fontsize=10, ha='right')
    
    # Highlight the best alternative if specified
    if best_alternative is not None:
        for i, sol in enumerate(solution_names):
            if sol == best_alternative:
                label = ax.get_xticklabels()[i]
                label.set_color('red')
                label.set_fontweight('bold')
                break
    
    # Show the plot only if we created the figure and not exporting
    if created_fig and not export:
        plt.tight_layout()
        plt.show()
    
    return ax  # Return the axes for further manipulation

'''
PLOT OF FOOD GROUP DISTRIBUTION (5TH TO 95TH PERCENTILE AND MEAN) VS SELECTED BASKET
'''
def plot_food_group_distribution(df, colors_df, title=True, export=False):
    """
    Creates a horizontal plot for food groups showing the range from 5th to 95th percentile
    and a black dot for the mean, with color coding and sorting based on colors_df.
    """
    # Sort df based on the order in colors_df
    colors_df = colors_df.reindex(colors_df.index[::-1])
    df = df.reindex(colors_df.index)
    # Extract data
    food_groups = df.index
    fifth_percentile = df['5th percentile (grams/day)']
    ninety_fifth_percentile = df['95th percentile (grams/day)']
    mean = df['mean (grams/day)']
    basket = df['Selected basket']
    colors = colors_df['color_code']
    # Create the plot
    # fig, ax = plt.subplots(figsize=(10, len(food_groups) * 0.32))
    #fig, ax = plt.subplots(figsize=(12, 6))
    fig, ax = plt.subplots(figsize=(8, 6))
    for i, food_group in enumerate(food_groups):
        ax.hlines(y=food_group, 
                  xmin=fifth_percentile.iloc[i], 
                  xmax=ninety_fifth_percentile.iloc[i], 
                  color=colors.iloc[i], 
                  linewidth=10)
    # Plot mean values as black square markers (NOT CIRCLES)
    ax.scatter(mean, food_groups, color='black', zorder=5, label='Mean consumption in current diets', s=200, marker='|')
    ax.scatter(basket, food_groups, color='black', edgecolors='white', zorder=5, label='Selected healthy diet basket', s=50, marker='D', linewidth=1)
    # Add vertical grid lines every 20 grams
    ax.xaxis.set_minor_locator(plt.MultipleLocator(20))
    ax.xaxis.grid(which='both', linestyle='--', linewidth=0.5)
    # Add labels and title
    ax.set_xlabel('Grams per Day', fontsize=11)
    if title:
        ax.set_title('Food subgroup Distribution (5th to 95th Percentile and mean)', fontsize=12)
    #Legend in bottom right corner inside the plot
    ax.legend(loc='lower right', fontsize=11, frameon=True)
    # Show the plot
    plt.tight_layout()
    # Show the plot
    if not export:
        plt.show()
    else:
        return fig


'''
PLOT OF FOOD GROUP DISTRIBUTION (5TH TO 95TH PERCENTILE AND MEAN) VS MULTIPLE SELECTED BASKETS
'''

def plot_food_group_distribution_selected_baskets(current_df, optimized_baskets, colors_df, colors_baskets, size_baskets, title=True, export=False, ax=None):
    # Sort df based on the order in colors_df
    colors_df = colors_df.reindex(colors_df.index[::-1])
    current_df = current_df.reindex(colors_df.index)
    optimized_baskets = optimized_baskets.reindex(colors_df.index)
    # Convert '' to 0 in optimized_baskets and ensure numeric dtype
    optimized_baskets = optimized_baskets.replace('', 0)
    optimized_baskets = optimized_baskets.apply(pd.to_numeric, errors='coerce').fillna(0)
    # Extract data
    food_groups = current_df.index
    fifth_percentile = current_df['5th percentile (grams/day)']
    ninety_fifth_percentile = current_df['95th percentile (grams/day)']
    mean = current_df['mean (grams/day)']
    median = current_df['median (grams/day)']
    colors = colors_df['color_code']
    # If any food_group in food_groups is not in optimized_baskets, add a new row with 0s
    for food_group in food_groups:
        if food_group not in optimized_baskets.index:
            optimized_baskets.loc[food_group] = 0
    
    # Use provided axes or create new ones
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
        created_fig = True
    else:
        created_fig = False
        fig = ax.get_figure()
    
    # Create the plot
    for i, food_group in enumerate(food_groups):
        ax.hlines(y=food_group, 
                  xmin=fifth_percentile.iloc[i], 
                  xmax=ninety_fifth_percentile.iloc[i], 
                  color='#6cc9d6',
                  linewidth=10)
        
    # Plot median and mean values as markers
    ax.scatter(median, food_groups, color='black', zorder=5, label='Median consumption', s=180, marker='|')
    ax.scatter(mean, food_groups, color='red', zorder=5, label='Mean consumption', s=180, marker='|')
    # Best baskets
    for best_basket in optimized_baskets.columns:
        if best_basket in colors_baskets:
            ax.scatter(optimized_baskets[best_basket], food_groups, edgecolors='black', color=colors_baskets[best_basket], zorder=5, label=best_basket, s=size_baskets[best_basket], marker='o', linewidth=0)
    # Add vertical grid lines every 20 grams
    ax.xaxis.set_minor_locator(plt.MultipleLocator(20))
    ax.xaxis.grid(which='both', linestyle='--', linewidth=0.5)
    # Start x-axis at 0
    #ax.set_xlim(left=-10)
    ax.set_xlim(left=-10, right=700)
    # Add labels and title
    ax.set_xlabel('Grams / Day', fontsize=13)

    # label sizes
    ax.tick_params(axis='y', labelsize=13)
    ax.tick_params(axis='x', labelsize=13)

    if title:
        ax.set_title('Current consumption patterns and selected diet baskets', fontsize=13)
    # Combine legend entries for percentiles and markers
    legend_elements = [Line2D([0], [0], color='none', label=r'$\bf{Selected\ diet\ baskets:}$')]  # Bold heading]
    for name, color in colors_baskets.items():
        legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markeredgecolor='none', markersize=8, label=name))

    legend_elements += [
        Line2D([0], [0], color='none', label=r'$\bf{Current\ consumption\ metrics:}$'),  # Bold heading
        Line2D([0], [0], color='#6cc9d6', lw=5, label='5th-95th percentiles'),
        Line2D([0], [0], color='black', marker='|', markersize=10, linestyle='None', label='Median consumption'),
        Line2D([0], [0], color='red', marker='|', markersize=10, linestyle='None', label='Mean consumption')
    ]

    ax.legend(handles=legend_elements, loc='lower right', fontsize=13, frameon=True)
    
    # Only show if we created the figure and not exporting
    if created_fig and not export:
        plt.tight_layout()
        plt.show()
    
    return ax  # Return the axes for further manipulation

'''
HEAT MAP OF FOOD BASKETS COMPOSITION
'''
# Function to plot heatmap of multiple baskets composition
def plot_multiple_baskets_composition_heatmap(df, title=True, export=False):
    number_of_food_items = len(df.index)
    number_of_baskets = len(df.columns)
    size_per_row = 0.15
    size_per_column = 0.8
    #plt.figure(figsize=(1 + number_of_baskets * size_per_column,2 + number_of_food_items * size_per_row))
    plt.figure(figsize=(12, 7))
    cmap = LinearSegmentedColormap.from_list('custom', ['green', 'blue', 'red'])
    sns.heatmap(df, cmap=cmap, cbar_kws={'label': 'Amount (g)'}, xticklabels=df.columns)
    
    # AESTHETICS ADJUSTMENTS
    # Separate all rows with a grey line (note that is a heatmap and rows are +- 0.5 not in the middle of the cell)
    for i in range(len(df.index)):
        plt.axhline(i+1, color='black', lw=0.2)
    # Separate all rows with a grey line (note that is a heatmap and rows are +- 0.5 not in the middle of the cell)
    for i in range(len(df.columns)):
        plt.axvline(i+1, color='black', lw=0.2)
    # Add in all the ticks
    plt.gca().spines['top'].set_visible(True)
    plt.gca().spines['bottom'].set_visible(True)
    plt.gca().spines['right'].set_visible(True)
    plt.gca().spines['left'].set_visible(True)

    # Size of the ticks
    plt.tick_params(axis='x', labelsize=9)
    plt.tick_params(axis='y', labelsize=9)
    # TITLE AND LABELS
    if title:
        plt.title('Food Basket Composition Heatmap', fontsize=12)
    plt.xlabel('Food Baskets', fontsize=12)
    plt.ylabel('Food Items', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Show the plot
    if not export:
        plt.show()
    else:
        return plt


'''
CLUSTERMAP OF FOOD BASKETS COMPOSITION
'''
# Function to plot clustermap and dendrogram
def plot_multiple_baskets_composition_clustermap(df, title=True, export=False):
    number_of_food_items = len(df.index)
    number_of_baskets = len(df.columns)
    size_per_row = 0.25
    size_per_column = 0.5
    # Ensure the DataFrame contains only finite values
    df_cleaned = df #df.replace([np.inf, -np.inf], np.nan).fillna(0)
    # Define the colormap
    cmap = LinearSegmentedColormap.from_list('custom', ['white','green', 'blue', 'red'])
    # Create the clustermap
    clustermap = sns.clustermap(
        df_cleaned,
        cmap=cmap,
        standard_scale=1,
        metric="correlation",
        #metric="euclidean",
        #method="single",
        row_cluster=True,
        col_cluster=True,
        figsize=(number_of_baskets * size_per_column, number_of_food_items * size_per_row),
        cbar_kws={'label': 'Amount (g)'},
        cbar_pos=(1.01, 0, 0.02, 0.9), # (left, bottom, width, height)
        linewidths=0.5,
        dendrogram_ratio=(0.15, 0.15),
        xticklabels=True,
        yticklabels=True
    )
    # Adjust aesthetics
    if title:
        clustermap.ax_heatmap.set_title('Food Basket Composition Clustermap', fontsize=12, loc='center', pad=80)
    clustermap.ax_heatmap.set_xlabel('Food Baskets', fontsize=12)
    clustermap.ax_heatmap.set_ylabel('Food Items', fontsize=12)
    clustermap.ax_heatmap.tick_params(axis='x', labelsize=9, rotation=0)
    clustermap.ax_heatmap.tick_params(axis='y', labelsize=9)
    # Show the plot
    # Show the plot
    if not export:
        plt.show()
    else:
        return plt