"""
Main window of Ideated GUI. Currenlty relativley low on iteration priority, but
works as is
Author: Nathan Gollay
"""

# External Libraries
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSlider, QLabel, QPushButton, QListWidget, QListWidgetItem, 
                             QLineEdit)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
import multiprocessing
import time


class SliderDemo(QWidget):
    # Core Functionality for basic GUI
    def __init__(self, record_button_pushed, save_button_pushed, load_button_pushed, pose_name_parent_conn,
        identifier_name_parent_conn, sensitivity_slider, recording_name_conn):
        super().__init__()
        self.initialize_ui()
        self.record_button_pushed = record_button_pushed
        self.save_button_pushed = save_button_pushed
        self.mode_button_pushed = load_button_pushed
        self.lock = multiprocessing.Lock()

        self.identifier_conn = identifier_name_parent_conn
        self.pose_name_conn = pose_name_parent_conn
        self.sensitivity_slider_value = sensitivity_slider
        
        self.recording_name_conn = recording_name_conn


    def initialize_ui(self):
        layout = QVBoxLayout()

        # Title
        """
        title = QLabel('Gesture Recording and Shit')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the title
        layout.addWidget(title)
        """

        # Three buttons side by side
        button_layout = QHBoxLayout()

        self.button1 = QPushButton('Record')
        self.button1.clicked.connect(self.on_button1_clicked)
        button_layout.addWidget(self.button1)

        button2_layout = QVBoxLayout()
        self.button2 = QPushButton('Save')
        self.button2.clicked.connect(self.on_button2_clicked)
        button2_layout.addWidget(self.button2)
        
        self.text_box_under_button2 = QLineEdit()
        self.text_box_under_button2.setPlaceholderText("        Pose Name")
        button2_layout.addWidget(self.text_box_under_button2)
        
        self.text_box_under_button2_b = QLineEdit()
        self.text_box_under_button2_b.setPlaceholderText("    Unique Identifier")
        button2_layout.addWidget(self.text_box_under_button2_b)
        
        button_layout.addLayout(button2_layout)
        
        button3_layout = QVBoxLayout()
        self.button3 = QPushButton('Mode')
        self.button3.clicked.connect(self.on_button3_clicked)
        button3_layout.addWidget(self.button3)

        self.text_box_under_button3 = QLineEdit()
        self.text_box_under_button3.setPlaceholderText("        Pose Name")
        button3_layout.addWidget(self.text_box_under_button3)

        self.text_box_under_button3_b = QLineEdit()
        self.text_box_under_button3_b.setPlaceholderText("    Unique Identifier")
        button3_layout.addWidget(self.text_box_under_button3_b)

        button_layout.addLayout(button3_layout)

        layout.addLayout(button_layout)

        # Sensitivity Slider
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.update_label)

        self.label = QLabel('Sensitiivity: 50')
        
        
        # Reset button
        self.reset_button = QPushButton('Stop')
        self.reset_button.clicked.connect(self.reset_slider)

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        layout.addWidget(self.reset_button)

         # List of text options
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Controls to add to the list and toggle color
        control_layout = QHBoxLayout()

        self.text_input = QLineEdit()
        control_layout.addWidget(self.text_input)

        add_button = QPushButton('Add Item')
        add_button.clicked.connect(self.add_item)
        control_layout.addWidget(add_button)

        toggle_color_button = QPushButton('Toggle Color')
        toggle_color_button.clicked.connect(self.toggle_item_color)
        control_layout.addWidget(toggle_color_button)

        layout.addLayout(control_layout)

        self.setLayout(layout)
        self.setWindowTitle('Author: Nathan Gollay')
        self.show()

    def add_item(self):
        text = self.text_input.text()
        if text:
            item = QListWidgetItem(text)
            self.list_widget.addItem(item)
            # Reset the input field
            self.text_input.setText('')

    def toggle_item_color(self):
        item = self.list_widget.currentItem()
        if item:
            current_color = item.background().color().name()
            if current_color == '#00ff00':  # Green
                item.setBackground(QColor(255, 0, 0))  # Set to red
            elif current_color == '#ff0000':  # Red
                item.setBackground(QColor(192, 192, 192))  # Set to grey
            else:
                item.setBackground(QColor(0, 255, 0))  # Set to green

    def update_label(self, value):
        self.sensitivity_slider_value.value = value
        self.label.setText(f'Sensitivity: {value}')

    def reset_slider(self):
        self.slider.setValue(50)

    def on_button1_clicked(self):
        # Placeholder for button 1 functionality
        print("Button 1 was clicked!")
        
        with self.lock:
            self.record_button_pushed.value = 1 
        time.sleep(1)
        name_text = self.text_box_under_button2.text()
        unique_identifier_text = self.text_box_under_button2_b.text()
        file_name = str(unique_identifier_text) + '_' + str(name_text)
        print(file_name)
        self.recording_name_conn.send(file_name)

    def on_button2_clicked(self):
        # Placeholder for button 2 functionality
        print("Button 2 was clicked!")
        name_text = self.text_box_under_button2.text()
        unique_identifier_text = self.text_box_under_button2_b.text()
        
        self.identifier_conn.send(unique_identifier_text)
        self.pose_name_conn.send(name_text)

        with self.lock:
            self.save_button_pushed.value = 1

    def on_button3_clicked(self):
        # Placeholder for button 2 functionality
        print("Button 3 was clicked!")
        with self.lock:
            self.mode_button_pushed.value = 1







