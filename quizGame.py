from __future__ import print_function

import time
import _thread
import json
from os import path
from tkinter import Tk, StringVar, Label, Button, Frame, DISABLED, NORMAL

from BuzzController import BuzzController
from random import shuffle
from playsound import playsound

team1colour = "red"
team2colour = "green"
team3colour = "blue"
team4colour = "orange"


def play_sound(sound_file, wait=0):
    _thread.start_new_thread(playsound, (path.abspath(sound_file),))
    time.sleep(wait)


def load_questions(file):
    # Import and shuffle the questions
    question_file = open(file)
    for q in json.load(question_file):
        buttons = ["blue", "orange", "green", "yellow"]
        new_answer = {}
        shuffle(buttons)
        new_answer['question'] = q['question']
        for i in range(4):
            if i == 0:
                new_answer["correct"] = buttons[i]
            new_answer[buttons[i]] = q["answers"][i]
        questions.append(new_answer)


def reset():
    global score, current_round, current_question

    # Turn off the lights
    buzz.light_blinking = False
    buzz.all_off()

    # Reset the team score
    for i in range(len(score)):
        score[i] = 0

    set_label(team1_score, "0")
    set_label(team2_score, "0")
    set_label(team3_score, "0")
    set_label(team4_score, "0")

    # Reset the counters
    current_round = 1
    current_question = 0
    startButton['text'] = "Start"
    startButton['state'] = NORMAL
    resetButton['state'] = DISABLED

    set_label(questionLabel, "Press Start to Begin")
    set_label(answer_blue, "")
    set_label(answer_orange, "")
    set_label(answer_green, "")
    set_label(answer_yellow, "")


def set_label(label, text):
    string = StringVar()
    string.set(text)
    label.config(textvariable=string)


def start():
    global startButton, questionLabel, current_round, current_question

    # If this is the first question clear and load the questions for this round
    if current_question == 0 and current_round <= rounds:
        questions.clear()
        question_file = 'Questions/Round' + str(current_round) + '.json'
        load_questions(question_file)

    # If we have stopped then don't do anything for now
    if startButton['text'] == "Finish":
        reset()
        return

    # Output the question
    set_label(questionLabel, questions[current_question]["question"])
    print(questions[0]["question"])
    _thread.start_new_thread(wait_for_buzz, (current_question,))

    # Set the start button to the next function
    if current_question + 1 == len(questions) and current_round < rounds:
        startButton['text'] = "Next Round"
        startButton['state'] = DISABLED
        current_question = 0
        current_round += 1
    elif current_question + 1 == len(questions) and current_round == rounds:
        startButton['text'] = "Finish"
        startButton['state'] = DISABLED
        resetButton['state'] = NORMAL
        current_question += 1
    else:
        startButton['text'] = "Next Question"
        startButton['state'] = DISABLED
        current_question += 1


def update_score(controller, points):
    score[controller] += points
    set_label(team1_score, score[0])
    set_label(team2_score, score[1])
    set_label(team3_score, score[2])
    set_label(team4_score, score[3])


def wait_for_buzz(question_number):
    question_answered = False
    available_answers = ["Blue", "Orange", "Green", "Yellow"]
    available_controllers = [0, 1, 2, 3]

    question = questions[question_number]
    while not question_answered:

        for answer in available_answers:
            set_label(answer_blue, question[answer.lower()])
            if answer == "Blue":
                set_label(answer_blue, question[answer.lower()])
            if answer == "Orange":
                set_label(answer_orange, question[answer.lower()])
            if answer == "Green":
                set_label(answer_green, question[answer.lower()])
            if answer == "Yellow":
                set_label(answer_yellow, question[answer.lower()])
            print(answer + " " + question[answer.lower()])

        _thread.start_new_thread(buzz.light_blink, (available_controllers,))
        controller = buzz.controller_get_first_pressed("red", available_controllers)
        buzz.light_blink_stop()
        buzz.light_set(controller, True)
        play_sound('Sounds/buzzer.wav', 1)
        time.sleep(0.5)

        while True:
            # TODO: Start a timer once they buzz in which they have to press the option (3 secs)
            button = buzz.get_button_pressed(controller)
            if button and button != "red":
                if button == question["correct"]:
                    play_sound('Sounds/bell.wav', 1)
                    print("Controller " + str(controller + 1) + " was correct")
                    question_answered = True
                    update_score(controller, 1)
                    startButton['state'] = NORMAL
                    break
                elif button.capitalize() in available_answers:
                    play_sound('Sounds/wrong.wav', 1)
                    print("Sorry incorrect answer")
                    available_controllers.remove(controller)
                    available_answers.remove(button.capitalize())
                    break
        buzz.light_set(controller, False)
    time.sleep(1)


# Main Program
questions = []
score = [0, 0, 0, 0]

top = Tk()
top.title("Buzz Quiz")

top.option_add('*Dialog.msg.font', 'Sans 10')

big_font = ("Sans", 24)
medium_font = ("Sans", 20)

# ScoreFrame
scoreFrame = Frame(top)
scoreFrame.grid(row=0, column=0, columnspan=8)
scoreLabel = Label(scoreFrame, text="Scores", justify="center", font=medium_font)
scoreLabel.grid(row=0, column=0, columnspan=8)
score1Frame = Frame(scoreFrame, borderwidth=2, relief="raised")
score1Frame.grid(row=1, column=0)
score2Frame = Frame(scoreFrame, borderwidth=2, relief="raised")
score2Frame.grid(row=1, column=1)
score3Frame = Frame(scoreFrame, borderwidth=2, relief="raised")
score3Frame.grid(row=1, column=2)
score4Frame = Frame(scoreFrame, borderwidth=2, relief="raised")
score4Frame.grid(row=1, column=3)

team1_label = Label(score1Frame, text="Team 1", justify="right", font=medium_font)
team1_score = Label(score1Frame, justify="right", width=20, font=medium_font, fg=team1colour)
team1_label.grid(row=0, column=0)
team1_score.grid(row=1, column=0)

team2_label = Label(score2Frame, text="Team 2", justify="right", font=medium_font)
team2_score = Label(score2Frame, justify="right", width=20, font=medium_font, fg=team2colour)
team2_label.grid(row=0, column=0)
team2_score.grid(row=1, column=0)

team3_label = Label(score3Frame, text="Team 3", justify="right", font=medium_font)
team3_score = Label(score3Frame, justify="right", width=20, font=medium_font, fg=team3colour)
team3_score.config()
team3_label.grid(row=0, column=0)
team3_score.grid(row=1, column=0)

team4_label = Label(score4Frame, text="Team 4", justify="right", font=medium_font)
team4_score = Label(score4Frame, justify="right", width=20, font=medium_font, fg=team4colour)
team4_label.grid(row=0, column=0)
team4_score.grid(row=1, column=0)


def time_minus():
    return


def time_plus():
    return


def time_reset():
    return


def set_time_string(string):
    global timeString, timeLabel

    try:
        timeString.set(string)  # TODO Why does this throw an error?
    # print "successfully set to: "+str(string))
    except AttributeError:
        print("Failed to set to: " + string)
        timeString = StringVar(timeLabel)
        timeLabel.config(textvariable=timeString)
        set_time_string(string)


timeString = StringVar()
# # setTimeString("Ready to Start Countdown!")
timeFrame = Frame(top, borderwidth=5)
timeFrame.grid(row=1, column=0, columnspan=4)
Label(timeFrame, text="Time:", justify="right", font=medium_font).grid(row=0, column=0, sticky='e')
minusButton = Button(timeFrame, text="-", width=1, command=time_minus)
minusButton.grid(row=0, column=1, padx=10)
timeLabel = Label(timeFrame, textvariable=timeString, width=2, justify="center", font=medium_font)
timeLabel.grid(row=0, column=2)
plusButton = Button(timeFrame, text="+", width=1, command=time_plus)
plusButton.grid(row=0, column=3, padx=10)
falseStartButton = Button(timeFrame, text="Reset", width=2, command=time_reset)
falseStartButton.grid(row=0, column=4)
set_time_string("10")

# Label displaying question # and associated buttons
questionFrame = Frame(top, borderwidth=5)
questionFrame.grid(row=2, column=0, columnspan=4)
Label(questionFrame, justify="center").grid(row=0, column=0)
questionLabel = Label(questionFrame, justify="center", font=big_font)
questionLabel.grid(row=0, column=2)

blue_frame = Frame(top, borderwidth=8, background="blue")
blue_frame.grid(row=3, column=0, columnspan=2, rowspan=2)
answer_blue = Label(blue_frame, width=50, height=15, font=medium_font)
answer_blue.grid(row=0, column=0, columnspan=1)

orange_frame = Frame(top, borderwidth=8, background="orange")
orange_frame.grid(row=3, column=2, columnspan=2, rowspan=2)
answer_orange = Label(orange_frame, width=50, height=15, font=medium_font)
answer_orange.grid(row=0, column=1, columnspan=1)

green_frame = Frame(top, borderwidth=8, background="green")
green_frame.grid(row=5, column=0, columnspan=2, rowspan=2)
answer_green = Label(green_frame, width=50, height=15, font=medium_font)
answer_green.grid(row=1, column=0, columnspan=1)

yellow_frame = Frame(top, borderwidth=8, background="yellow")
yellow_frame.grid(row=5, column=2, columnspan=2, rowspan=2)
answer_yellow = Label(yellow_frame, width=50, height=15, font=medium_font)
answer_yellow.grid(row=1, column=1, columnspan=1)

resetButton = Button(top, text="Reset", justify="center", width=20, height=2, command=reset, font=medium_font)
resetButton.grid(row=7, column=0)

startButton = Button(top, text="Start", justify="center", width=20, height=2, command=start, font=medium_font)
startButton.grid(row=7, column=3)

rounds = 2

# Initialise the buzzer and turn the lights off
buzz = BuzzController()
reset()

# Gets the requested values of the height and width.
windowWidth = top.winfo_reqwidth()
windowHeight = top.winfo_reqheight()
print("Width", windowWidth, "Height", windowHeight)

# Gets both half the screen width/height and window width/height
positionRight = int(top.winfo_screenwidth() / 2 - windowWidth / 2)
positionDown = int(top.winfo_screenheight() / 3 - windowHeight / 2)

# Positions the window in the center of the page.
top.geometry("+{}+{}".format(positionRight, positionDown))

print("Starting loop...")
top.mainloop()
