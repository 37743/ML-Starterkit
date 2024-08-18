from os import path, makedirs
from datetime import datetime
from tkinter import filedialog

import matplotlib.pyplot as plt

def generate_visualizations(data, visualization_types, column_subset):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"visualizations_{timestamp}"
    save_path = filedialog.askdirectory(title="Select Folder to Save Visualizations")
    folder_path = path.join(save_path, folder_name)
    makedirs(folder_path)

    if column_subset == []:
        column_subset = data.columns
        
    for visualization_type in visualization_types:
        if visualization_type in ['Scatter Plot', 'Line Plot', 'Bar Plot']:
            if len(column_subset) == 2:
                if visualization_type == 'Scatter Plot':
                    plt.scatter(data[column_subset[0]], data[column_subset[1]])
                    plt.title(f'Scatter Plot - {column_subset[0]} vs {column_subset[1]}')
                    plt.xlabel(column_subset[0])
                    plt.ylabel(column_subset[1])
                    plt.savefig(path.join(folder_path, f'scatter_plot_{column_subset[0]}_{column_subset[1]}.png'))
                    plt.close()
                elif visualization_type == 'Line Plot':
                    plt.plot(data[column_subset[0]], data[column_subset[1]])
                    plt.title(f'Line Plot - {column_subset[0]} vs {column_subset[1]}')
                    plt.xlabel(column_subset[0])
                    plt.ylabel(column_subset[1])
                    plt.savefig(path.join(folder_path, f'line_plot_{column_subset[0]}_{column_subset[1]}.png'))
                    plt.close()
                elif visualization_type == 'Bar Plot':
                    plt.bar(data[column_subset[0]], data[column_subset[1]])
                    plt.title(f'Bar Plot - {column_subset[0]} vs {column_subset[1]}')
                    plt.xlabel(column_subset[0])
                    plt.ylabel(column_subset[1])
                    plt.savefig(path.join(folder_path, f'bar_plot_{column_subset[0]}_{column_subset[1]}.png'))
                    plt.close()

        for column in column_subset:
            if visualization_type == 'Histogram':
                plt.hist(data[column])
                plt.title(f'Histogram - {column}')
                plt.xlabel('Values')
                plt.ylabel('Frequency')
                plt.savefig(path.join(folder_path, f'histogram_{column}.png'))
                plt.close()
            elif visualization_type == 'Boxplot':
                plt.boxplot(data[column])
                plt.title(f'Boxplot - {column}')
                plt.xlabel('Columns')
                plt.ylabel('Values')
                plt.savefig(path.join(folder_path, f'boxplot_{column}.png'))
                plt.close()
            elif visualization_type == 'Pie Chart':
                if data[column].dtype == 'object':
                    plt.pie(data[column])
                    plt.title(f'Pie Chart - {column}')
                    plt.savefig(path.join(folder_path, f'pie_chart_{column}.png'))
                    plt.close()
            elif visualization_type == 'Correlation Heatmap':
                plt.imshow(data[column].corr(), cmap='hot', interpolation='nearest')
                plt.title(f'Correlation Heatmap - {column}')
                plt.colorbar()
                plt.savefig(path.join(folder_path, f'correlation_heatmap_{column}.png'))
                plt.close()
            elif visualization_type == 'Violin Plot':
                plt.violinplot(data[column])
                plt.title(f'Violin Plot - {column}')
                plt.xlabel('Columns')
                plt.ylabel('Values')
                plt.savefig(path.join(folder_path, f'violin_plot_{column}.png'))
                plt.close()
    return
