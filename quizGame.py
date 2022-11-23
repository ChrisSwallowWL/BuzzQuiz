from __future__ import print_function

import time
import _thread
import json
from os import path
from BuzzController import BuzzController
from random import shuffle
from playsound import playsound


def play_sound(sound_file, wait=0):
    _thread.start_new_thread(playsound, (path.abspath(sound_file),))
    time.sleep(wait)


def load_questions(file):
    return json.load(file)


questions = []
score = [0, 0, 0, 0]

# Import and shuffle the questions
question_file = open('Questions/Round1.json')
for question in load_questions(question_file):
    buttons = ["blue", "orange", "green", "yellow"]
    new_answer = {}
    shuffle(buttons)
    new_answer['question'] = question['question']
    for i in range(4):
        if i == 0:
            new_answer["correct"] = buttons[i]
        new_answer[buttons[i]] = question["answers"][i]
    questions.append(new_answer)

# Create a new instance of the controller
buzz = BuzzController()

for question in questions:
    question_answered = False
    available_answers = ["Blue", "Orange", "Green", "Yellow"]
    available_controllers = [0, 1, 2, 3]

    while not question_answered:
        print(question["question"])

        for i in available_answers:
            print(i + " " + question[i.lower()])

        _thread.start_new_thread(buzz.light_blink, (available_controllers,))
        controller = buzz.controller_get_first_pressed("red", available_controllers)
        buzz.light_blinking = False
        buzz.light_set(controller, True)
        play_sound('Sounds/buzzer.wav', 1)
        time.sleep(0.5)

        while True:
            button = buzz.get_button_pressed(controller)
            if button and button != "red":
                if button == question["correct"]:
                    play_sound('Sounds/bell.wav', 1)
                    print("Controller " + str(controller + 1) + " was correct")
                    question_answered = True
                    score[controller] += 1
                    break
                elif button.capitalize() in available_answers:
                    play_sound('Sounds/wrong.wav', 1)
                    print("Sorry incorrect answer")
                    available_controllers.remove(controller)
                    available_answers.remove(button.capitalize())
                    break
        buzz.light_set(controller, False)
    time.sleep(1)

print("Final score")
print(score)
