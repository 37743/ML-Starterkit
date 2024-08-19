'''
This script contains the function to generate visualizations for the data.
The function takes in the data, visualization types,
and column subset as input and generates visualizations based on the input parameters.
The visualizations are saved in a folder with a timestamp in the selected directory.
The function returns True if the visualizations are generated successfully,
and False if the user cancels the operation.
'''

from os import path, makedirs
from datetime import datetime
from tkinter import filedialog
from itertools import combinations

import matplotlib.pyplot as plt

# TODO: Reduce delay, can't thread this due to Tkinter GUI mainthread issue
def generate_visualizations(data, visualization_types, column_subset):
    """
    Generate visualizations based on the given data, visualization types, and column subset.
    Parameters:
    - data: pandas DataFrame
        The data to be visualized.
    - visualization_types: list of str
        The types of visualizations to be generated.
    - column_subset: list of str
        The subset of columns to be used for visualization.
    Returns:
    - bool
        True if the visualizations are successfully generated and saved, False otherwise.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"visualizations_{timestamp}"
    save_path = filedialog.askdirectory(title="Select Folder to Save Visualizations")
    if save_path == '':
        return False
    folder_path = path.join(save_path, folder_name)
    makedirs(folder_path)

    if column_subset == []:
        column_subset = data.columns
        
    for visualization_type in visualization_types:
        if visualization_type in ['Scatter Plot', 'Line Plot', 'Bar Plot']:
            column_subset = data[column_subset].select_dtypes(exclude=['object']).columns
            # Cartesian product of column_subset
            column_pairs = list(combinations(column_subset, 2))
            for pair in column_pairs:
                column1, column2 = pair
                if visualization_type == 'Scatter Plot':
                    plt.scatter(data[column1], data[column2])
                    plt.title(f'Scatter Plot - {column1} vs {column2}')
                    plt.xlabel(column1)
                    plt.ylabel(column2)
                    plt.savefig(path.join(folder_path, f'scatter_plot_{column1}_{column2}.png'), bbox_inches='tight')
                    plt.close()
                elif visualization_type == 'Line Plot':
                    plt.plot(data[column1], data[column2])
                    plt.title(f'Line Plot - {column1} vs {column2}')
                    plt.xlabel(column1)
                    plt.ylabel(column2)
                    plt.savefig(path.join(folder_path, f'line_plot_{column1}_{column2}.png'), bbox_inches='tight')
                    plt.close()
                elif visualization_type == 'Bar Plot':
                    plt.bar(data[column1], data[column2])
                    plt.title(f'Bar Plot - {column1} vs {column2}')
                    plt.xlabel(column1)
                    plt.ylabel(column2)
                    plt.savefig(path.join(folder_path, f'bar_plot_{column1}_{column2}.png'), bbox_inches='tight')
                    plt.close()

        for column in column_subset:
            if visualization_type == 'Histogram':
                plt.hist(data[column])
                plt.title(f'Histogram - {column}')
                plt.xlabel('Values')
                plt.ylabel('Frequency')
                plt.savefig(path.join(folder_path, f'histogram_{column}.png'), bbox_inches='tight')
                plt.close()
            elif visualization_type == 'Boxplot':
                if data[column].dtype == 'object':
                    continue
                plt.boxplot(data[column])
                plt.title(f'Boxplot - {column}')
                plt.xlabel('Columns')
                plt.ylabel('Values')
                plt.savefig(path.join(folder_path, f'boxplot_{column}.png'), bbox_inches='tight')
                plt.close()
            elif visualization_type == 'Pie Chart':
                if data[column].dtype == 'object':
                    data[column].value_counts().plot(kind='pie',
                                                     autopct='%1.1f%%',
                                                     startangle=90,
                                                     legend=True,
                                                     colormap='tab20c')
                    plt.title(f'Pie Chart - {column}')
                    plt.savefig(path.join(folder_path, f'pie_chart_{column}.png'), bbox_inches='tight')
                    plt.close()
            elif visualization_type == 'Violin Plot':
                if data[column].dtype == 'object':
                    continue
                plt.violinplot(data[column])
                plt.title(f'Violin Plot - {column}')
                plt.xlabel('Columns')
                plt.ylabel('Values')
                plt.savefig(path.join(folder_path, f'violin_plot_{column}.png'), bbox_inches='tight')
                plt.close()

        if visualization_type == 'Correlation Heatmap':
            col_numeric = data[column_subset].select_dtypes(include=['int64', 'float64']).columns
            _, ax = plt.subplots()
            im = ax.imshow(data[col_numeric].corr(), cmap='YlGn', interpolation='nearest')
            ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
            ax.figure.colorbar(im, ax=ax)
            for i in range(len(data[col_numeric].columns)):
                for j in range(len(data[col_numeric].columns)):
                    ax.text(i, j, round(data[col_numeric].corr().iloc[i, j], 2), ha='center', va='center')
            plt.xticks(range(len(data[col_numeric].columns)), data[col_numeric].columns, rotation=90)
            plt.yticks(range(len(data[col_numeric].columns)), data[col_numeric].columns)
            plt.title(f'Correlation Heatmap')
            plt.savefig(path.join(folder_path, f'correlation_heatmap_{col_numeric}.png'), bbox_inches='tight')
            plt.close()
    return True
