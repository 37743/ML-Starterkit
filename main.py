from pandas import read_csv, read_excel
from tkinter import Tk
from threading import Thread
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from tkinter import filedialog
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
from Scripts.transformation import perform_transformations
from Scripts.visualization import generate_visualizations
from os import path
from datetime import datetime

from kivy.clock import (mainthread,
                        Clock)
Config.set('input', 'mouse', 'mouse,disable_multitouch')

WINDOW_SIZE = (720, 580)

MAIN_COLORS = {
    "GREEN": "45b7af",
    "RED": "f3565d",
    "BLUE": "65c3df",
    "YELLOW": "f8cb00",
    "PURPLE": "a48ad4",
    "GRAY": "b1b1b1",
    "COLOR": "2f323b"
}

Window.size = WINDOW_SIZE

Window.minimum_width = WINDOW_SIZE[0]-0.1*WINDOW_SIZE[0]
Window.minimum_height = WINDOW_SIZE[1]-0.1*WINDOW_SIZE[1]

def thread(function):
    ''' 
    Creates a new thread with a process using the input function
    '''
    def wrap(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t
    return wrap

def popup(type):
    '''
    Creates a popup window based on the type.
    Args:
        type (str): The type of popup window to create.
    Returns:
        popup (Popup): The popup window created.
    '''
    if type == 'success':
        popup = Popup(title='SUCCESS!',
                      content=Image(source='Assets\\icon.png'),
                      size_hint=(None, None), size=(350, 300),
                      separator_color=MAIN_COLORS["GREEN"],
                      title_align='center',
                      background_color=MAIN_COLORS["GREEN"])
    elif type == 'failure':
        popup = Popup(title='CRITICAL FAILURE!',
                      content=Image(source='Assets\\icon-fail.png'),
                      size_hint=(None, None), size=(350, 300),
                      separator_color=MAIN_COLORS["RED"],
                      title_align='center',
                      background_color=MAIN_COLORS["RED"])
    popup.open()
    return

def remove_duplicates(df, label, columns):
    '''
    Removes duplicate rows from a DataFrame based on the specified columns.
    Args:
        df (pandas.DataFrame): The DataFrame from which duplicates are to be removed.
        label (Label): The label widget to update with the number of duplicates.
        columns (list): The list of columns to consider for duplicate removal.
    Returns:
        df (pandas.DataFrame): The DataFrame without duplicate rows.
    '''
    if columns == []:
        columns = df.columns
    try:
        df.drop_duplicates(subset=columns, inplace=True)
        label.text = f"Number of Duplicates: {df.duplicated().sum()}"
        popup(type='success')
    except Exception as e:
        popup(type='failure')
        print(e)
    return

def handle_missing_values(df, method, label, columns):
    '''
    Handles missing values in a DataFrame based on the selected method and specified columns.
    Args:
        df (pandas.DataFrame): The DataFrame containing missing values.
        method (str): The method to use for handling missing values.
        label: The label to update with the number of missing values.
        columns (list): The list of columns to consider for missing value handling.
    Returns:
        df (pandas.DataFrame): The DataFrame with missing values handled.
    '''
    if columns == []:
        columns = df.columns
    try:
        if method == 'mean':
            numeric_columns = df[columns].select_dtypes(include=['float64', 'int64']).columns
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
        elif method == 'median':
            numeric_columns = df[columns].select_dtypes(include=['float64', 'int64']).columns
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        elif method == 'mode':
            df[columns] = df[columns].fillna(df[columns].mode().iloc[0])
        elif method == 'remove':
            df.dropna(subset=columns, inplace=True)
        label.text = f"Number of Missing Values: {df[columns].isnull().sum().sum()}"
        
        popup(type='success')
    except Exception as e:
        popup(type='failure')
        print(e)
    return

class MLStarterkit(App):
    '''
    The main application class.
    This class represents the main application and contains various methods for file handling, UI updates, and operations.
    '''
    def open_file(self, file_path="", df=None):
        '''
        Opens the selected file and updates the UI accordingly.
        Args:
            file_path (str): The path of the selected file.
        Returns:
            None
        '''
        # Dataframe starts processing here
        self.df = df
        
        self.scroll_layout = ScrollView(size_hint=(0.9, 0.55),
                                pos_hint={'center_x': 0.5, 'center_y': 0.43},
                                bar_color=MAIN_COLORS["GREEN"],
                                bar_inactive_color=MAIN_COLORS["GRAY"],
                                bar_width=10)
        
        self.grid_layout = GridLayout(cols=2, spacing=30, padding=10, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        if not self.df:
            self.file_path = file_path
            if file_path:
                print("Selected file:", file_path)
                self.load_button.text = "FILE LOADING"
                self.load_button.disabled = True
                
                thread = self.read_file(file_path)

                self.loadreq.text = "Loading data..."
                self.monitor_change(thread, self.load_view)
        else:
            self.load_view()
        return
    
    @thread
    def read_file(self, file_path):
        '''
        Reads a file and returns a pandas DataFrame
        Args:
            file_path (str): The path of the file.
        Returns:
            df (pandas.DataFrame): The DataFrame containing the data from the file.
        '''
        _, file_extension = path.splitext(file_path)
        if file_extension.lower() in ['.csv', '.txt']:
            df = read_csv(file_path)
        else:
            df = read_excel(file_path)
        self.df = df
        return

    def remove_scrollview(self, widget):
        '''
        Removes the scroll view and its children from the UI.
        Args:
            widget (ScrollView or BoxLayout or GridLayout): The widget to be removed.
        Returns:
            None
        '''
        if isinstance(widget, ScrollView):
            widget.clear_widgets()
            self.layout.remove_widget(widget)
        elif isinstance(widget, (BoxLayout, GridLayout)):
            for child in widget.children:
                self.remove_scrollview(child)
            widget.clear_widgets()
            self.layout.remove_widget(widget)

    @mainthread
    def open_file_chooser(self):
        '''
        Opens the file chooser dialog and updates the UI with the selected file path.
        Returns:
            self (App): The current instance of the App class.
        '''
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        self.file_path_boxlayout.ids["ti"].text = file_path
        self.loadreq.text = "Click on \"Load File\" to load the selected file."
        self.load_button.text = "LOAD FILE"
        self.load_button.disabled = False
        try:
            for widget in [self.scroll_layout, self.file_boxlayout, self.button_box_layout]:
                self.remove_scrollview(widget)
        except:
            pass
        del(file_path)
        del(root)
        return self

    def monitor_change(self, thread, function):
        '''
        Monitors the status of a thread and waits for it to complete.
        Args:
            thread (Thread): The thread to be monitored.
        Returns:
            None
        '''
        if thread.is_alive():
            Clock.schedule_once(lambda dt: self.monitor_change(thread, function), 1)
        else:
            thread.join()
            function()
        return
    
    def load_filebox(self):
        self.file_boxlayout = BoxLayout(orientation='horizontal',
                                    spacing=10, padding=10,
                                    size_hint=(0.9, 0.1),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.76})
        self.file_title = Label(text="\""+self.file_path.split("/")[-1]+"\"",
                                color=MAIN_COLORS["COLOR"],
                                font_family="Msyhl",
                                font_size=21,
                                size_hint=(0.9, 0.1),
                                pos_hint={'center_y': 0.5},
                                halign='left')
        self.file_shape = Label(text="Shape: "+str(self.df.shape)+
                                " - File Size: "+str(round(self.df.memory_usage().sum() / 1024, 2))+" KB",
                                color=MAIN_COLORS["GRAY"],
                                font_family="Msyhl",
                                font_size=14,
                                size_hint=(0.9, 0.1),
                                pos_hint={'center_y': 0.5},
                                halign='left')
        self.file_boxlayout.add_widget(self.file_title)
        self.file_boxlayout.add_widget(self.file_shape)
        self.layout.add_widget(self.file_boxlayout)
        return
    
    def load_datagrid(self):
        data_grid_layout = GridLayout(cols=len(self.df.columns) if len(self.df.columns) < 7 else 8,
                                    spacing=5,
                                    padding=(25,0),
                                    size_hint_y=None)
        data_grid_layout.bind(minimum_height=data_grid_layout.setter('height'))

        # df.head() equivalent
        for num, column in enumerate(self.df.columns):
            if num == 6:
                button = Button(text="...",
                                color=MAIN_COLORS["COLOR"],
                                height=30,
                                font_family="Msyhl",
                                font_size=14,
                                background_normal="",
                                background_down="",
                                background_color=list(MAIN_COLORS.values())[num%(len(MAIN_COLORS)-2)],
                                size_hint_y=None)
                data_grid_layout.add_widget(button)
            elif (num < 6) or (num == len(self.df.columns) - 1):
                button = Button(text=column if len(column) < 7 else column[:7]+"...",
                                color=MAIN_COLORS["COLOR"],
                                height=30,
                                font_family="Msyhl",
                                font_size=14,
                                background_normal="",
                                background_down="",
                                background_color=list(MAIN_COLORS.values())[num%(len(MAIN_COLORS)-2)],
                                size_hint_y=None)
                data_grid_layout.add_widget(button)

        for i in range(5): # 5 rows only
            for num, column in enumerate(self.df.columns):
                if num == 6:
                    button = Button(text="...",
                                    color=MAIN_COLORS["COLOR"],
                                    height=30,
                                    font_family="Msyhl",
                                    font_size=14,
                                    background_normal="",
                                    background_color=MAIN_COLORS["GRAY"],
                                    size_hint_y=None)
                    data_grid_layout.add_widget(button)
                elif (num < 6) or num == (len(self.df.columns) - 1):
                    value = str(self.df[column][i])
                    button = Button(text=value if len(value) < 7 else str(value)[:7]+"...",
                                color=MAIN_COLORS["COLOR"],
                                height=30,
                                font_family="Msyhl",
                                font_size=14,
                                background_normal="",
                                background_color=MAIN_COLORS["GRAY"],
                                size_hint_y=None)
                    data_grid_layout.add_widget(button)
        return data_grid_layout
    
    def load_datainfo(self):
        self.data_info_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.data_info_layout.bind(minimum_height=self.data_info_layout.setter('height'))

        for index, column in enumerate(self.df.columns):
            entry_layout = GridLayout(cols=4, spacing=10, padding=(25,0), size_hint_y=None)
            entry_layout.bind(minimum_height=entry_layout.setter('height'))

            index_column_label = Button(text=f"{index}. {column}",
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        background_normal="",
                        background_down="",
                        background_color=list(MAIN_COLORS.values())[index%(len(MAIN_COLORS)-2)],
                        size_hint_y=None)
            entry_layout.add_widget(index_column_label)

            non_null_count_label = Label(text=str(self.df[column].count()),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            entry_layout.add_widget(non_null_count_label)

            data_type_label = Label(text=str(self.df[column].dtype),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            entry_layout.add_widget(data_type_label)

            column_checkbox = CheckBox(color=MAIN_COLORS["GREEN"],
                                size_hint=(0.2, None),
                                height=30)
            entry_layout.add_widget(column_checkbox)

            self.data_info_layout.add_widget(entry_layout)
        return

    def load_datadescription(self):
        data_description_grid_layout = GridLayout(cols=9,
                                                spacing=5,
                                                padding=(25,0),
                                                size_hint_y=None)
        data_description_grid_layout.bind(minimum_height=data_description_grid_layout.setter('height'))

        for i in ['Name', 'Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']:
            label = Label(text=i,
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(label)    

        for index, column in enumerate(self.df.columns):
            if self.df[column].dtype == 'object':
                continue
            button = Button(text=column if len(column) < 7 else column[:7]+"...",
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_x=1.5,
                        size_hint_y=None,
                        background_normal="",
                        background_down="",
                        background_color=list(MAIN_COLORS.values())[index%(len(MAIN_COLORS)-2)])
            data_description_grid_layout.add_widget(button)

            count = Label(text=str(self.df[column].count()),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(count)

            mean = Label(text=str(round(self.df[column].mean(), 2)),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(mean)

            std = Label(text=str(round(self.df[column].std(), 2)),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(std)

            min_val = Label(text=str(self.df[column].min()),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(min_val)

            quantile_25 = Label(text=str(self.df[column].quantile(0.25)),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(quantile_25)

            quantile_50 = Label(text=str(self.df[column].quantile(0.5)),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(quantile_50)

            quantile_75 = Label(text=str(self.df[column].quantile(0.75)),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(quantile_75)

            max_val = Label(text=str(self.df[column].max()),
                        color=MAIN_COLORS["COLOR"],
                        height=30,
                        font_family="Msyhl",
                        font_size=14,
                        size_hint_y=None)
            data_description_grid_layout.add_widget(max_val)
        return data_description_grid_layout

    def load_dupna(self):
        duplicates_label = Label(text=f"Number of Duplicates: {self.df.duplicated().sum()}",
                                color=MAIN_COLORS["COLOR"],
                                font_family="Msyhl",
                                font_size=14,
                                size_hint=(0.9, 0.1),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5})

        remove_duplicates_button = Button(text="REMOVE DUPLICATES",
                                bold=True,
                                font_size=14,
                                height=30,
                                size_hint=(0.5, None),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                background_normal="",
                                background_color=MAIN_COLORS["GREEN"])
        remove_duplicates_button.bind(on_release=lambda x: remove_duplicates(self.df, duplicates_label, self.get_labels()))

        self.missing_values_label = Label(text=f"Number of Missing Values: {self.df.isnull().sum().sum()}",
                                color=MAIN_COLORS["COLOR"],
                                font_family="Msyhl",
                                font_size=14,
                                size_hint=(0.9, 0.1),
                                pos_hint={'center_x': 0.5, 'center_y': 0.35})

        self.button_box_layout = BoxLayout(orientation='horizontal', spacing=10, padding=(25,0), size_hint_y=None)
        self.button_box_layout.bind(minimum_height=self.button_box_layout.setter('height'))

        mean_button = Button(text="Fill with Mean",
                     bold=True,
                     height=30,
                     size_hint=(0.5, None),
                     font_size=14,
                     pos_hint={'center_x': 0.5, 'center_y': 0.5},
                     background_normal="",
                     background_color=MAIN_COLORS["GREEN"])
        
        mean_button.bind(on_release=lambda x: handle_missing_values(self.df ,'mean', self.missing_values_label, self.get_labels()))

        median_button = Button(text="Fill with Median",
                       bold=True,
                       height=30,
                       size_hint=(0.5, None),
                       font_size=14,
                       pos_hint={'center_x': 0.5, 'center_y': 0.5},
                       background_normal="",
                       background_color=MAIN_COLORS["GREEN"])
        median_button.bind(on_release=lambda x: handle_missing_values(self.df, 'median', self.missing_values_label, self.get_labels()))

        mode_button = Button(text="Fill with Mode",
                     bold=True,
                     height=30,
                     size_hint=(0.5, None),
                     font_size=14,
                     pos_hint={'center_x': 0.5, 'center_y': 0.5},
                     background_normal="",
                     background_color=MAIN_COLORS["GREEN"])
        mode_button.bind(on_release=lambda x: handle_missing_values(self.df, 'mode', self.missing_values_label, self.get_labels()))

        remove_button = Button(text="Drop N/A",
                       bold=True,
                       height=30,
                       size_hint=(0.5, None),
                       font_size=14,
                       pos_hint={'center_x': 0.5, 'center_y': 0.5},
                       background_normal="",
                       background_color=MAIN_COLORS["GREEN"])
        remove_button.bind(on_release=lambda x: handle_missing_values(self.df, 'remove', self.missing_values_label, self.get_labels()))
        return duplicates_label, remove_duplicates_button, mean_button,\
            median_button, mode_button, remove_button
    
    def load_transformations(self):
        transformation_labels = ['Standardization1', 'Normalization1', 'One-Hot Encoding2',
                                 'Label Encoding2','Log Transformation3',  'Polynomial Transformation3']

        self.transformation_vertical_grid_layout = GridLayout(cols=2,
                                                        spacing=10,
                                                        size_hint=(1, None))
        self.transformation_vertical_grid_layout.bind(minimum_height=self.transformation_vertical_grid_layout.setter('height'))

        for label in transformation_labels:
            data_transformation_box_layout = BoxLayout(orientation='horizontal',
                                                       spacing=10,
                                                       size_hint=(1, None),
                                                       height=30)
            data_transformation_box_layout.add_widget(Label(text=label[:-1],
                                                               color=MAIN_COLORS["COLOR"],
                                                               font_family="Msyhl",
                                                               font_size=14,
                                                               size_hint=(0.8, None),
                                                               height=30))
            data_transformation_box_layout.add_widget(CheckBox(color=MAIN_COLORS["GREEN"],
                                                            size_hint=(0.2, None),
                                                            height=30,
                                                            group=label[-1]))
            self.transformation_vertical_grid_layout.add_widget(data_transformation_box_layout)
        return
    
    def load_visualizations(self):
        visualization_labels = ['Histogram', 'Boxplot', 'Scatter Plot', 'Line Plot',
                                'Bar Plot', 'Pie Chart', 'Correlation Heatmap', 'Violin Plot']

        self.visualization_vertical_grid_layout = GridLayout(cols=2,
                                                       spacing=10,
                                                       size_hint=(1, None))
        self.visualization_vertical_grid_layout.bind(minimum_height=self.visualization_vertical_grid_layout.setter('height'))
        
        for label in visualization_labels:
            data_visualization_box_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=30)
            data_visualization_box_layout.add_widget(Label(text=label,
                                                               color=MAIN_COLORS["COLOR"],
                                                               font_family="Msyhl",
                                                               font_size=14,
                                                               size_hint=(0.8, None),
                                                               height=30))
            data_visualization_box_layout.add_widget(CheckBox(color=MAIN_COLORS["GREEN"],
                                                            size_hint=(0.2, None),
                                                            height=30))
            self.visualization_vertical_grid_layout.add_widget(data_visualization_box_layout)
        return

    def load_view(self):
        self.loadreq.text = ""
        self.load_button.text = "FILE LOADED"
        self.load_filebox()
        
        vertical_box_layout = BoxLayout(orientation='vertical', spacing=30, padding=(0,10), size_hint_y=None)
        vertical_box_layout.bind(minimum_height=vertical_box_layout.setter('height'))

        vertical_box_layout.add_widget(self.load_datagrid())
            
        data_exploration_label = Label(text="Data Exploration",
                                    color=MAIN_COLORS["COLOR"],
                                    font_family="Msyhl",
                                    font_size=21,
                                    size_hint=(0.9, 0.1),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.35})
        vertical_box_layout.add_widget(data_exploration_label)

        select_columns_label = Label(text="Select columns to perform operations on (or none for all columns).",
                        color=MAIN_COLORS["COLOR"],
                        font_family="Msyhl",
                        font_size=14,
                        size_hint=(0.9, 0.1),
                        pos_hint={'center_x': 0.5, 'center_y': 0.35})
        vertical_box_layout.add_widget(select_columns_label)

        self.load_datainfo()

        vertical_box_layout.add_widget(self.data_info_layout)

        data_description_label = Label(text="Data Description",
                        color=MAIN_COLORS["COLOR"],
                        font_family="Msyhl",
                        font_size=21,
                        size_hint=(0.9, 0.1),
                        pos_hint={'center_x': 0.5, 'center_y': 0.35})
        vertical_box_layout.add_widget(data_description_label)
        
        vertical_box_layout.add_widget(self.load_datadescription())
        
        data_preprocessing_label = Label(text="Data Preprocessing",
                        color=MAIN_COLORS["COLOR"],
                        font_family="Msyhl",
                        font_size=21,
                        size_hint=(0.9, 0.5),
                        pos_hint={'center_x': 0.5, 'center_y': 0.35})
        vertical_box_layout.add_widget(data_preprocessing_label)
        duplicates_label, remove_duplicates_button, mean_button, \
            median_button, mode_button, remove_button = self.load_dupna()
        vertical_box_layout.add_widget(duplicates_label)
        vertical_box_layout.add_widget(remove_duplicates_button)
        vertical_box_layout.add_widget(self.missing_values_label)
        self.button_box_layout.add_widget(mean_button)
        self.button_box_layout.add_widget(median_button)
        self.button_box_layout.add_widget(mode_button)
        self.button_box_layout.add_widget(remove_button)
        vertical_box_layout.add_widget(self.button_box_layout)
        
        # Data Transformation
        data_transformation_label = Label(text="Data Transformation",
                                        color=MAIN_COLORS["COLOR"],
                                        font_family="Msyhl",
                                        font_size=21,
                                        size_hint=(0.9, 0.5),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.35})
        vertical_box_layout.add_widget(data_transformation_label)

        self.load_transformations()
        vertical_box_layout.add_widget(self.transformation_vertical_grid_layout)

        # Data Visualization
        data_visualization_label = Label(text="Data Visualization",
                        color=MAIN_COLORS["COLOR"],
                        font_family="Msyhl",
                        font_size=21,
                        size_hint=(0.9, 0.5),
                        pos_hint={'center_x': 0.5, 'center_y': 0.35})
        vertical_box_layout.add_widget(data_visualization_label)

        self.load_visualizations()
        vertical_box_layout.add_widget(self.visualization_vertical_grid_layout)

        self.scroll_layout.add_widget(vertical_box_layout)
        self.layout.add_widget(self.scroll_layout)

        self.button_box_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))
        
        perform_button = Button(text="PERFORM OPERATION(S)",
            bold=True,
            size_hint=(0.7, 1),
            font_size=14,
            pos_hint={'center_x': 0.5},
            background_normal="",
            background_color=MAIN_COLORS["GREEN"])
        perform_button.bind(on_release=lambda x: self.perform_operations())
        self.button_box_layout.add_widget(perform_button)

        save_button = Button(text="SAVE CSV FILE",
            bold=True,
            size_hint=(0.3, 1),
            font_size=14,
            pos_hint={'center_x': 0.5},
            background_normal="",
            background_color=MAIN_COLORS["GREEN"])
        save_button.bind(on_release=lambda x: self.save_csv_file())
        self.button_box_layout.add_widget(save_button)

        self.layout.add_widget(self.button_box_layout)
        return

    def save_csv_file(self):
        '''
        Saves the DataFrame to a CSV file.
        Returns:
            None
        '''
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{self.file_path.split('/')[-1].split('.')[0]}_{timestamp}.csv"
            # Open file dialog to choose save location
            save_location = filedialog.asksaveasfilename(defaultextension='.csv',
                                                        filetypes=[("CSV files", "*.csv"),
                                                                    ("All files", "*.*")],
                                                        initialfile=filename)
            if save_location:
                self.df.to_csv(save_location, index=False)
                print(f"File saved successfully as {save_location}.")
            else:
                print("Save operation cancelled.")
        except Exception as e:
            print(e)
        return
    
    def get_labels(self):
        '''
        Performs the selected operation based on the checkboxes in the UI.
        Returns:
            None
        '''
        selected_labels = []
        for child in self.data_info_layout.children:
            checkbox = child.children[0]
            if checkbox.active:
                label = child.children[-1]
                selected_labels.append(label.text.split(".")[1].strip())
        
        print("Selected labels:", selected_labels)
        return selected_labels
    
    def perform_operations(self):
        '''
        Performs the selected operations on the selected labels.
        Returns:
            None
        '''
        labels = self.get_labels()
        print(labels)
        try:
            # Data Transformation
            transformations = []
            for child in self.transformation_vertical_grid_layout.children:
                checkbox = child.children[0]
                if checkbox.active:
                    label = child.children[-1]
                    transformations.append(label.text)
            print(transformations)
            
            # Data Visualization
            visualizations = []
            for child in self.visualization_vertical_grid_layout.children:
                checkbox = child.children[0]
                if checkbox.active:
                    label = child.children[-1]
                    visualizations.append(label.text)
            print(visualizations)

            if transformations:
                self.df = perform_transformations(self.df, transformations, labels)
            if visualizations:
                generate_visualizations(self.df, visualizations, labels)
                
            popup(type='success')
            try:
                for widget in [self.scroll_layout, self.file_boxlayout, self.button_box_layout]:
                    self.remove_scrollview(widget)
            except:
                pass
            self.open_file(df=self.df)
        except:
            popup(type='failure')
        return
    
    def update_background(self, instance, value):
        '''
        Updates the background of the layout.
        Args:
            instance: The instance triggering the update.
            value: The new value triggering the update.
        Returns:
            None
        '''
        with self.layout.canvas.before:
            self.layout.canvas.before.clear()
            self.layout.canvas.before.add(Rectangle(source='Assets\\BG\\default_bg.png',
                                                    size=self.layout.size,
                                                    pos=self.layout.pos))
        return
    
    def build(self):
        '''
        Builds the UI of the application.
        Returns:
            layout (FloatLayout): The main layout of the application.
        '''
        self.icon = 'Assets\\icon.png'
        self.title = 'Machine Learning Starter kit - @37743'
        self.layout = FloatLayout()
        
        self.layout.bind(size=self.update_background, pos=self.update_background)

        box_layout = BoxLayout(orientation='horizontal',
                        spacing=10, padding=10,
                        size_hint=(0.9, None), height=60,
                        pos_hint={'center_x': 0.5, 'center_y': 0.9})

        outlined_build = ('''
BoxLayout:
    id: box
    TextInput:
        id: ti
        pos_hint: {'center_y': 0.5}
        size_hint: 0.75, 0.75
        line_width: 2
        canvas.after:
            Color:
                rgba: 69.0/255, 183.0/255, 175.0/255, 1
            Line:
                width: self.line_width
                rectangle: self.x, self.y, self.width, self.height
''')
        
        self.file_path_boxlayout = Builder.load_string(outlined_build)
        box_layout.add_widget(self.file_path_boxlayout)

        self.file_chooser_button = Button(text="BROWSE FILES",
                            bold=True,
                            font_size=14,
                            on_release=lambda x: self.open_file_chooser(),
                            size_hint=(0.3, 1),
                            pos_hint={'center_y': 0.5},
                            background_normal="",
                            background_color=MAIN_COLORS["GREEN"])
        box_layout.add_widget(self.file_chooser_button)
        
        self.load_button = Button(text="LOAD FILE",
                                bold=True,
                                font_size=14,
                                disabled_color="ffffff",
                                on_release=lambda x: self.open_file(self.file_path_boxlayout.ids["ti"].text),
                                size_hint=(0.3, 1),
                                pos_hint={'center_y': 0.5},
                                background_normal="",
                                background_color=MAIN_COLORS["GREEN"])
        box_layout.add_widget(self.load_button)
        self.layout.add_widget(box_layout)

        self.loadreq = Label(text="Load a file (\".csv\", \".xls\", ...etc) to start.",
                        color=MAIN_COLORS["GRAY"],
                        font_family="Msyhl",
                        font_size=21,
                        size_hint=(0.5, 0.1),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},)
        self.layout.add_widget(self.loadreq)
        
        footer = Label(text=f"GitHub@37743 - {self.__class__.__name__} - 2024 - v{1.0}",
                        color=MAIN_COLORS["GRAY"],
                        font_family="Msyhl",
                        font_size=12,
                        size_hint=(1, 0.1),
                        pos_hint={'center_x': 0.5, 'center_y': 0.07})
        self.layout.add_widget(footer)
        
        return self.layout
    
    def open_settings(self, *largs):
        '''
        Removes the bloated Kivy options for packaging.
        Args:
            *largs: Variable length argument list.
        Returns:
            None
        '''
        pass


if __name__ == '__main__':
    MLStarterkit().run()
