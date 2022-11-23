from __future__ import print_function
from BuzzController import BuzzController
import time
import _thread
from random import shuffle
from playsound import playsound

# Define the questions here. Correct answer first.
import_questions = [
    {"question": "What is the capital of Australia", "answers": ["Canberra", "Sydney", "Hobart", "Melbourne"]},
    {"question": "What is the capital of Japan", "answers": ["Tokyo", "Horoshima", "Osaka", "Kyoto"]},
]
questions = []
score = [0, 0, 0, 0]

# Import and shuffle the questions
for question in import_questions:
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
        playsound('Sounds/buzzer.wav')
        time.sleep(0.5)

        while True:
            button = buzz.get_button_pressed(controller)
            if button and button != "red":
                if button == question["correct"]:
                    playsound('Sounds/bell.wav')
                    print("Controller " + str(controller + 1) + " was correct")
                    question_answered = True
                    score[controller] += 1
                    break
                elif button.capitalize() in available_answers:
                    playsound('Sounds/wrong.wav')
                    print("Sorry incorrect answer")
                    available_controllers.remove(controller)
                    available_answers.remove(button.capitalize())
                    break
        buzz.light_set(controller, False)
    time.sleep(1)

print("Final score")
print(score)
