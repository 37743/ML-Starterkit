import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
import tkinter as tk
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

Config.set('input', 'mouse', 'mouse,disable_multitouch')

WINDOW_SIZE = (720, 580)

Window.size = WINDOW_SIZE

Window.minimum_width = WINDOW_SIZE[0]-0.2*WINDOW_SIZE[0]
Window.minimum_height = WINDOW_SIZE[1]-0.2*WINDOW_SIZE[1]

class App(App):
    def open_csv_file(self, file_path):
        if file_path:
            print("Selected CSV file:", file_path)

    def open_file_chooser(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        self.file_path_textbox.text = file_path
        return file_path

    def perform_operation(self):
        selected_labels = []
        for child in self.grid_layout.children:
            if isinstance(child, BoxLayout):
                # kivy inserts new children in reverse order
                checkbox = child.children[0]
                print(checkbox)
                if checkbox.active:
                    label = child.children[1]
                    selected_labels.append(label.text)
        
        print("Selected labels:", selected_labels)
        return
    
    def build(self):
        layout = FloatLayout()

        def update_background(instance, value):
            layout.canvas.before.clear()
            layout.canvas.before.add(Color(1, 1, 1, 1))
            layout.canvas.before.add(Rectangle(size=layout.size, pos=layout.pos))
        
        layout.bind(size=update_background, pos=update_background)

        box_layout = BoxLayout(orientation='horizontal',
                       spacing=10, padding=10,
                       size_hint=(0.9, None), height=50,
                       pos_hint={'center_x': 0.5, 'center_y': 0.9})

        self.file_path_textbox = TextInput(multiline=False,
                            size_hint=(0.7, 1),
                            pos_hint={'center_y': 0.5})
        box_layout.add_widget(self.file_path_textbox)

        file_chooser_button = Button(text="Choose File",
                         on_release=lambda x: self.open_csv_file(self.open_file_chooser()),
                         size_hint=(0.3, 1),
                         pos_hint={'center_y': 0.5},
                         background_normal="",
                         background_color="3284e9")
        box_layout.add_widget(file_chooser_button)

        load_button = Button(text="Load File",
                             on_release=lambda x: self.open_csv_file(self.file_path_textbox.text),
                             size_hint=(0.3, 1),
                             pos_hint={'center_y': 0.5},
                             background_normal="",
                             background_color="3284e9")
        box_layout.add_widget(load_button)

        scroll_layout = ScrollView(size_hint=(0.95, 0.6),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                   bar_color="3284e9",
                                   bar_width=10)
        
        self.grid_layout = GridLayout(cols=2, spacing=30, padding=10, size_hint_y=None,)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        scroll_layout.add_widget(self.grid_layout)

        for i in range(60):
            label = Label(text=f"Example {i+1}", color=(0, 0, 0, 1), font_family="Msyhl", font_size=15)
            checkbox = CheckBox(color="3284e9", size_hint=(0.2, None), height=10)
            new_box_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=10)
            new_box_layout.add_widget(label)
            new_box_layout.add_widget(checkbox)
            self.grid_layout.add_widget(new_box_layout)

        layout.add_widget(scroll_layout)

        perform_button = Button(text="Perform Operation",
                 size_hint=(1, 0.1),
                 pos_hint={'center_x': 0.5},
                 background_normal="",
                 background_color="3284e9")
        perform_button.bind(on_release=lambda x: self.perform_operation())
        layout.add_widget(perform_button)

        layout.add_widget(box_layout)

        return layout
    
    def open_settings(self, *largs):
        pass
    
if __name__ == '__main__':
    App().run()
