import pandas as pd
import tkinter as tk
import threading
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from tkinter import filedialog
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.lang import Builder
import os

from kivy.clock import (mainthread,
                        Clock)
Config.set('input', 'mouse', 'mouse,disable_multitouch')

WINDOW_SIZE = (720, 580)
MAIN_GREEN = "45b7af"
MAIN_GRAY = "b1b1b1"
MAIN_COLOR = "2f323b"

Window.size = WINDOW_SIZE

Window.minimum_width = WINDOW_SIZE[0]-0.1*WINDOW_SIZE[0]
Window.minimum_height = WINDOW_SIZE[1]-0.1*WINDOW_SIZE[1]

def thread(function):
    ''' 
    Creates a new thread with a process using the input function
    '''
    def wrap(*args, **kwargs):
        t = threading.Thread(target=function, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t
    return wrap

class MLStarterkit(App):
    '''
    The main application class.
    This class represents the main application and contains various methods for file handling, UI updates, and operations.
    '''
    def open_file(self, file_path):
        '''
        Opens the selected file and updates the UI accordingly.
        Args:
            file_path (str): The path of the selected file.
        Returns:
            None
        '''
        self.file_path = file_path
        if file_path:
            print("Selected file:", file_path)
            self.load_button.text = "FILE LOADING"
            self.load_button.disabled = True

            # Dataframe starts processing here
            thread = self.read_file(file_path)

            self.monitor_change(thread, self.load_view)

            self.loadreq.text = "Loading data..."
            self.scroll_layout = ScrollView(size_hint=(0.9, 0.55),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.43},
                                    bar_color=MAIN_GREEN,
                                    bar_inactive_color=MAIN_GRAY,
                                    bar_width=10)
            
            self.grid_layout = GridLayout(cols=2, spacing=30, padding=10, size_hint_y=None,)
            self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
            self.scroll_layout.add_widget(self.grid_layout)
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
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() in ['.csv', '.txt']:
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
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
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        self.file_path_boxlayout.ids["ti"].text = file_path
        self.loadreq.text = "Click on \"Load File\" to load the selected file."
        self.load_button.text = "LOAD FILE"
        self.load_button.disabled = False
        try:
            for widget in [self.scroll_layout, self.file_boxlayout]:
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
    
    def load_view(self):
        self.loadreq.text = ""
        self.load_button.text = "FILE LOADED"
        self.file_boxlayout = BoxLayout(orientation='horizontal',
                                    spacing=10, padding=10,
                                    size_hint=(0.9, 0.1),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.76})
        self.file_title = Label(text="\""+self.file_path.split("/")[-1]+"\"",
                                color=MAIN_COLOR,
                                font_family="Msyhl",
                                font_size=21,
                                size_hint=(0.9, 0.1),
                                pos_hint={'center_y': 0.5},
                                halign='left')
        self.file_shape = Label(text="Shape: "+str(self.df.shape)+
                                " File Size: "+str(round(self.df.memory_usage().sum() / 1024, 2))+" KB",
                                color=MAIN_GRAY,
                                font_family="Msyhl",
                                font_size=14,
                                size_hint=(0.9, 0.1),
                                pos_hint={'center_y': 0.5},
                                halign='left')
        self.file_boxlayout.add_widget(self.file_title)
        self.file_boxlayout.add_widget(self.file_shape)
        self.layout.add_widget(self.file_boxlayout)
        
        #TODO: Add the actual data from the file to the UI
        for i in range(60):
            label = Label(text=f"Example {i+1}", color=MAIN_COLOR, font_family="Msyhl", font_size=14)
            checkbox = CheckBox(color=MAIN_GREEN, size_hint=(0.2, None), height=10)
            new_box_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=10)
            new_box_layout.add_widget(label)
            new_box_layout.add_widget(checkbox)
            self.grid_layout.add_widget(new_box_layout)

        self.layout.add_widget(self.scroll_layout)

        perform_button = Button(text="PERFORM OPERATION(S)",
                bold=True,
                size_hint=(1, 0.1),
                font_size=14,
                pos_hint={'center_x': 0.5},
                background_normal="",
                background_color=MAIN_GREEN)
        perform_button.bind(on_release=lambda x: self.perform_operation())
        self.layout.add_widget(perform_button)
        return

    def perform_operation(self):
        '''
        Performs the selected operation based on the checkboxes in the UI.
        Returns:
            None
        '''
        selected_labels = []
        for child in self.grid_layout.children:
            if isinstance(child, BoxLayout):
                # kivy inserts new children in reverse order
                checkbox = child.children[0]
                if checkbox.active:
                    label = child.children[1]
                    selected_labels.append(label.text)
        
        print("Selected labels:", selected_labels)
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
            self.layout.canvas.before.add(Rectangle(source='Assets\BG\default_bg.png',
                                                    size=self.layout.size,
                                                    pos=self.layout.pos))
        return
    
    def build(self):
        '''
        Builds the UI of the application.
        Returns:
            layout (FloatLayout): The main layout of the application.
        '''
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
                            background_color=MAIN_GREEN)
        box_layout.add_widget(self.file_chooser_button)
        
        self.load_button = Button(text="LOAD FILE",
                                bold=True,
                                font_size=14,
                                disabled_color="ffffff",
                                on_release=lambda x: self.open_file(self.file_path_boxlayout.ids["ti"].text),
                                size_hint=(0.3, 1),
                                pos_hint={'center_y': 0.5},
                                background_normal="",
                                background_color=MAIN_GREEN)
        box_layout.add_widget(self.load_button)
        self.layout.add_widget(box_layout)

        self.loadreq = Label(text="Load a file (\".csv\", \".xls\", ...etc) to start.",
                        color=MAIN_GRAY,
                        font_family="Msyhl",
                        font_size=21,
                        size_hint=(0.5, 0.1),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},)
        self.layout.add_widget(self.loadreq)
        
        footer = Label(text=f"GitHub@37743 - {self.__class__.__name__} - 2024 - v{0.1}",
                        color=MAIN_GRAY,
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
