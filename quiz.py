import json
import os
import sys
from random import random
import numpy as np
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QRadioButton, QPushButton, QVBoxLayout, QHBoxLayout, \
    QGroupBox, QMenu, QAction, QMainWindow, QCheckBox
from PyQt5.QtGui import QPixmap, QFont


MAX_HISTORY = 50

def logit(x):
    if x <= 0:
        return -10000
    if x >= 1:
        return 10000
    return np.log(x / (1 - x))


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def get_random_question_id(weights):
    random_values = [random()*weight for weight in weights]
    return np.argmax(random_values)


def get_updated_weight(current_weight, correction):
    return sigmoid(logit(current_weight) + correction)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.entro_questions = None
        self.vela_questions = None
        self.entro_weights = None
        self.vela_weights = None
        self.entro_favorites = None
        self.vela_favorites = None
        self.current_question_id = 0
        self.current_question_set = None
        self.current_weight_set = None
        self.current_image_path = 'images_entro'
        self.answer_being_shown = False
        self.result_history = []
        self.load_questions()

    def load_questions(self):
        with open('questions_entro.json') as f:
            self.entro_questions = json.load(f)

        with open('questions_vela.json') as f:
            self.vela_questions = json.load(f)

        if os.path.isfile('entro_weights.json'):
            with open('entro_weights.json') as f:
                self.entro_weights = json.load(f)
        else:
            self.entro_weights = [0.5] * len(self.entro_questions)

        if os.path.isfile('vela_weights.json'):
            with open('vela_weights.json') as f:
                self.vela_weights = json.load(f)
        else:
            self.vela_weights = [0.5] * len(self.vela_questions)

        if os.path.isfile('entro_favorites.json'):
            with open('entro_favorites.json') as f:
                self.entro_favorites = set(json.load(f))
        else:
            self.entro_favorites = set()

        if os.path.isfile('vela_favorites.json'):
            with open('vela_favorites.json') as f:
                self.vela_favorites = set(json.load(f))
        else:
            self.vela_favorites = set()

        self.current_question_set = self.entro_questions
        self.current_weight_set = self.entro_weights
        self.current_favorite_set = self.entro_favorites
        self.current_image_path = 'images_entro'

        if os.path.isfile('result_history.json'):
            with open('result_history.json') as f:
                self.result_history = json.load(f)

        self.update_results()
        self.get_new_question()

    def update_results(self):
        if not self.result_history:
            self.result_label.setText('0/0')
        else:
            self.result_label.setText(f'{sum(self.result_history)}/{len(self.result_history)}')
        with open('result_history.json', 'w') as f:
            json.dump(self.result_history, f)

    def save_weights(self):
        with open('entro_weights.json', 'w') as f:
            json.dump(self.entro_weights, f)

        with open('vela_weights.json', 'w') as f:
            json.dump(self.vela_weights, f)

    def save_favorites(self):
        entro_favorite_list = [int(id) for id in self.entro_favorites]
        vela_favorite_list = [int(id) for id in self.vela_favorites]

        if self.entro_favorites:
            with open('entro_favorites.json', 'w') as f:
                json.dump(entro_favorite_list, f)

        if self.vela_favorites:
            with open('vela_favorites.json', 'w') as f:
                json.dump(vela_favorite_list, f)

    def get_new_question(self):
        self.answer_being_shown = False
        for button in self.radio_button_list:
            button.setStyleSheet("")
        self.radio_button1.setChecked(True)
        self.ok_button.setText("Ok")
        if self.favorite_action.isChecked():
            favorite_list = list(self.current_favorite_set)
            current_weight_set = [self.current_weight_set[i] for i in favorite_list]
            favorite_question_id = get_random_question_id(current_weight_set)
            question_id = favorite_list[favorite_question_id]
        else:
            question_id = get_random_question_id(self.current_weight_set)
        question = self.current_question_set[question_id]
        self.current_question_id = question_id
        if question_id in self.current_favorite_set:
            self.favorite_checkbox.setChecked(True)
        else:
            self.favorite_checkbox.setChecked(False)
        if not question['image']:
            self.image_panel.hide()
        else:
            self.image_panel.setPixmap(QPixmap(os.path.join(self.current_image_path, question['image'])))
            self.image_panel.show()
        self.text_panel.setText(question['question'].replace('\n', ' '))
        self.radio_button1.setText(question['answers'][0].replace('\n', ' '))
        self.radio_button2.setText(question['answers'][1].replace('\n', ' '))
        if len(question['answers']) == 2:
            self.radio_button3.hide()
        else:
            self.radio_button3.setText(question['answers'][2].replace('\n', ' '))
            self.radio_button3.show()

    def initUI(self):
        # Set window properties
        self.setWindowTitle("Quiz patente nautica")
        self.setGeometry(100, 100, 600, 400)

        # Create top-level widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create layout for top-level widget
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        top_widget = QWidget()
        top_layout = QHBoxLayout()
        top_widget.setLayout(top_layout)
        main_layout.addWidget(top_widget)


        # Create panel for image display
        self.image_panel = QLabel()
        self.image_panel.setFixedSize(200, 200)
        self.image_panel.setPixmap(QPixmap('image.jpg'))
        top_layout.addWidget(self.image_panel)

        # Create panel for text label
        self.text_panel = QLabel("Text Label")
        self.text_panel.setWordWrap(True)
        font = QFont()
        font.setPointSize(14)
        self.text_panel.setFont(font)
        top_layout.addWidget(self.text_panel)

        # Create group box for radio buttons
        self.radio_group = QGroupBox("Risposte")
        radio_layout = QVBoxLayout()
        self.radio_group.setLayout(radio_layout)
        self.radio_button1 = QRadioButton("Option 1")
        self.radio_button2 = QRadioButton("Option 2")
        self.radio_button3 = QRadioButton("Option 3")
        self.radio_button_list = [self.radio_button1, self.radio_button2, self.radio_button3]
        self.radio_button1.setChecked(True)
        radio_layout.addWidget(self.radio_button1)
        radio_layout.addWidget(self.radio_button2)
        radio_layout.addWidget(self.radio_button3)
        main_layout.addWidget(self.radio_group)

        # Create favorite checkbox
        self.favorite_checkbox = QCheckBox("Preferita")
        self.favorite_checkbox.toggled.connect(self.toggle_favorite)
        main_layout.addWidget(self.favorite_checkbox)

        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_widget.setLayout(bottom_layout)
        main_layout.addWidget(bottom_widget)

        # Create Ok button
        self.ok_button = QPushButton("Ok")
        bottom_layout.addWidget(self.ok_button,2)
        self.ok_button.clicked.connect(self.validate_answer)

        self.result_label = QLabel("")
        bottom_layout.addWidget(self.result_label,0)

        # Create menu bar
        menu_bar = self.menuBar()
        domande_menu = menu_bar.addMenu("Domande")
        self.entro_action = QAction("Entro", self)
        self.entro_action.setCheckable(True)
        self.entro_action.setChecked(True)
        self.vela_action = QAction("Vela", self)
        self.vela_action.setCheckable(True)
        self.vela_action.setChecked(False)
        domande_menu.addAction(self.entro_action)
        domande_menu.addAction(self.vela_action)
        self.entro_action.triggered.connect(self.change_questions_entro)
        self.vela_action.triggered.connect(self.change_questions_vela)
        self.favorite_action = QAction("Solo preferite", self)
        self.favorite_action.setCheckable(True)
        self.favorite_action.setChecked(False)
        domande_menu.addSeparator()
        domande_menu.addAction(self.favorite_action)

    @pyqtSlot()
    def show_favorites(self):
        pass

    @pyqtSlot()
    def toggle_favorite(self):
        if self.favorite_checkbox.isChecked():
            self.current_favorite_set.add(int(self.current_question_id))
        else:
            self.current_favorite_set.discard(int(self.current_question_id))
        self.save_favorites()

    @pyqtSlot()
    def change_questions_vela(self):
        self.entro_action.setChecked(False)
        self.vela_action.setChecked(True)
        self.current_question_set = self.vela_questions
        self.current_weight_set = self.vela_weights
        self.current_favorite_set = self.vela_favorites
        self.current_image_path = 'images_vela'
        self.get_new_question()

    @pyqtSlot()
    def change_questions_entro(self):
        self.entro_action.setChecked(True)
        self.vela_action.setChecked(False)
        self.current_question_set = self.entro_questions
        self.current_weight_set = self.entro_weights
        self.current_favorite_set = self.entro_favorites
        self.current_image_path = 'images_entro'
        self.get_new_question()

    @pyqtSlot()
    def validate_answer(self):
        if self.answer_being_shown:
            # Next question
            self.get_new_question()
            return

        answer = [button.isChecked() for button in self.radio_button_list].index(True)
        if answer == self.current_question_set[self.current_question_id]['right_answer']:
            # Correct answer
            #print('old weight', self.current_weight_set[self.current_question_id])
            self.current_weight_set[self.current_question_id] = get_updated_weight(self.current_weight_set[self.current_question_id], -0.2)
            #print('new weight', self.current_weight_set[self.current_question_id])
            self.radio_button_list[answer].setStyleSheet("border: 3px solid green;")
            self.result_history.append(1)
        else:
            # Wrong answer: make it appear more often
            #print('old weight', self.current_weight_set[self.current_question_id])
            self.current_weight_set[self.current_question_id] = get_updated_weight(self.current_weight_set[self.current_question_id], 0.2)
            #print('new weight', self.current_weight_set[self.current_question_id])
            self.radio_button_list[answer].setStyleSheet("border: 3px solid red;")
            self.radio_button_list[self.current_question_set[self.current_question_id]['right_answer']].setStyleSheet("border: 3px solid green;")
            self.result_history.append(0)
        self.ok_button.setText("Next")
        self.answer_being_shown = True
        while len(self.result_history) > MAX_HISTORY:
            self.result_history.pop(0)
        self.update_results()
        self.save_weights()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())