from __future__ import print_function

import time
import _thread
import json
import tkinter
from os import path
from tkinter import Tk, Label, Button, Frame, NORMAL
from PIL import ImageTk, Image

from BuzzController import BuzzController
from random import shuffle
from playsound import playsound
from pygame import mixer

import multiprocessing

team1colour = "red"
team2colour = "green"
team3colour = "blue"
team4colour = "orange"

mixer.init()


def play_music(sound_file, wait=0):
    mixer.music.load(path.abspath(sound_file))
    mixer.music.play()
    time.sleep(wait)
    # mixer.music.stop()


def play_sound(sound_file, wait=0):
    _thread.start_new_thread(playsound, (path.abspath(sound_file),))
    time.sleep(wait)


def load_questions(file):
    global question_type, questions, round_name

    # Import and shuffle the questions
    question_file = open(file)
    questions_json = json.load(question_file)
    round_name = questions_json['name']
    question_type = questions_json['type']
    for q in questions_json['questions']:
        buttons = ["blue", "orange", "green", "yellow"]
        new_answer = {}
        shuffle(buttons)
        new_answer['question'] = q['question']
        for i in range(4):
            if i == 0:
                new_answer["correct"] = buttons[i]
            new_answer[buttons[i]] = q["answers"][i]
        questions.append(new_answer)
        if question_type == "music":
            tracks.append(q["track"])


def reset():
    global score, current_round, current_question

    # Turn off the lights
    buzz.light_blinking = False
    buzz.all_off()

    # Reset the team score
    for i in range(len(score)):
        score[i] = 0

    team1_score['text'] = "0"
    team2_score['text'] = "0"
    team3_score['text'] = "0"
    team4_score['text'] = "0"

    # Reset the counters
    current_round = 1
    current_question = -1
    startButton['text'] = "Start"
    startButton['state'] = NORMAL

    questionLabel.configure(text="Press Start to Begin")
    clear_images()
    clear_labels()


def clear_images():
    set_image(blue_answer, "Pictures/Blue.jpg")
    set_image(orange_answer, "Pictures/Orange.jpg")
    set_image(green_answer, "Pictures/Green.jpg")
    set_image(yellow_answer, "Pictures/Yellow.jpg")


def clear_labels():
    set_label(blue_answer, "", "Blue")
    set_label(orange_answer, "", "Orange")
    set_label(green_answer, "", "Green")
    set_label(yellow_answer, "", "Yellow")


def set_label(label, text, colour):
    img = Image.open("Pictures/" + colour + ".jpg")
    resized_image = img.resize((750, 420), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(resized_image)
    label.config(image=image, text=text, width=740, height=450)
    label.image = image


def set_image(label, file):
    img = Image.open(file)
    width = int(img.size[0])
    height = int(img.size[1])
    resized_image = img.resize((width, height), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(resized_image)
    label.configure(text="", image=image, width=width, height=height)
    label.image = image


def start():
    global startButton, questionLabel, current_round, current_question

    # Immediately disable the start button so that you can't press it twice
    startButton['state'] = tkinter.DISABLED

    clear_images()
    clear_labels()
    questionLabel.configure(text="")
    root.update()

    # If this is the first question clear and load the questions for this round
    if current_question == -1 and current_round <= rounds:
        questions.clear()
        question_file = 'Questions/Round' + str(current_round) + '.json'
        load_questions(question_file)
        questionLabel.configure(text=round_name + " Round")
        root.update()
        current_question = 0
        startButton['text'] = 'Start'
        startButton['state'] = tkinter.NORMAL
        return

    # If we have stopped then don't do anything for now
    if startButton['text'] == "Finish":
        reset()
        return

    if question_type == "music":
        questionLabel.configure(text="Listen....")
        root.update()
        time.sleep(2)
        play_music(tracks[current_question], 5)

    # Output the question
    questionLabel.configure(text=questions[current_question]["question"])
    print(questions[0]["question"])
    _thread.start_new_thread(wait_for_buzz, (current_question,))

    # Set the start button to the next function
    if current_question + 1 == len(questions) and current_round < rounds:
        startButton['text'] = "Next Round"
        current_question = -1
        current_round += 1
    elif current_question + 1 == len(questions) and current_round == rounds:
        startButton['text'] = "Finish"
        current_question += 1
    else:
        startButton['text'] = "Next Question"
        current_question += 1


def update_score(controller, points):
    score[controller] += points
    team1_score['text'] = score[0]
    team2_score['text'] = score[1]
    team3_score['text'] = score[2]
    team4_score['text'] = score[3]


def set_answers(answer_colour, answer):
    if question_type == "image":
        if answer_colour == "Blue":
            set_image(blue_answer, answer)
        if answer_colour == "Orange":
            set_image(orange_answer, answer)
        if answer_colour == "Green":
            set_image(green_answer, answer)
        if answer_colour == "Yellow":
            set_image(yellow_answer, answer)
        print(answer_colour + " " + answer)
    else:
        if answer_colour == "Blue":
            set_label(blue_answer, answer, answer_colour)
        if answer_colour == "Orange":
            set_label(orange_answer, answer, answer_colour)
        if answer_colour == "Green":
            set_label(green_answer, answer, answer_colour)
        if answer_colour == "Yellow":
            set_label(yellow_answer, answer, answer_colour)
        print(answer_colour + " " + answer)


def wait_for_buzz(question_number):
    question_answered = False
    available_answers = ["Blue", "Orange", "Green", "Yellow"]
    available_controllers = [0, 1, 2, 3]

    buzz.clear_status()
    buzz.hid.read(5)
    buzz.get_button_pressed(0)

    # Display the answers for the current question
    question = questions[question_number]
    for answer in available_answers:
        set_answers(answer, question[answer.lower()])

    while not question_answered:

        for x in range(0, 20):
            buzz.clear_status()
            buzz.hid.read(5)

        # Start the lights blinking and wait for a button press
        _thread.start_new_thread(buzz.light_blink, (available_controllers,))
        controller = buzz.controller_get_first_pressed("red", available_controllers)
        buzz.light_blink_stop()
        buzz.light_set(controller, True)
        mixer.music.stop()
        play_sound('Sounds/buzzer.wav', 1)
        time.sleep(0.5)

        countdown = int(timeLabel['text'])
        while True:

            button = buzz.get_button_pressed(controller)
            buzz.light_blink_stop()

            if button and button != "red":
                if button == question["correct"]:
                    play_sound('Sounds/bell.wav', 1)
                    print("Team " + str(controller + 1) + " were correct")
                    question_answered = True
                    update_score(controller, 1)
                    startButton['state'] = tkinter.NORMAL
                    break
                elif button.capitalize() in available_answers:
                    play_sound('Sounds/wrong.wav', 1)
                    print("Sorry incorrect answer")
                    available_controllers.remove(controller)
                    # available_answers.remove(button.capitalize())

                    # If there are no more controllers, re-enable the button to continue
                    if len(available_controllers) == 0:
                        startButton['text'] = "Skip"
                        startButton['state'] = tkinter.NORMAL
                        question_answered = True
                    break

            time.sleep(0.2)
            countdown -= 0.2
            if countdown < 0:
                play_sound('Sounds/wrong.wav', 1)
                available_controllers.remove(controller)
                break

        buzz.light_set(controller, False)
    time.sleep(1)


# Main Program
questions = []
question_type = ""
round_name = ""
tracks = []
current_round = 1
current_question = -1
score = [0, 0, 0, 0]

root = Tk()
root.title("Buzz Quiz")
root.attributes('-fullscreen', True)

root.option_add('*Dialog.msg.font', 'Sans 10')

big_font = ("Sans", 30)
medium_font = ("Sans", 20)

# ScoreFrame
scoreFrame = Frame(root)
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
team1_score = Label(score1Frame, text=0, justify="right", width=20, font=medium_font, fg=team1colour)
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
    current_time = int(timeLabel['text'])
    new_time = current_time - 1
    timeLabel.configure(text=new_time)


def time_plus():
    current_time = int(timeLabel['text'])
    new_time = current_time + 1
    timeLabel.configure(text=new_time)


def time_reset():
    timeLabel.configure(text=3)


timeFrame = Frame(root, borderwidth=5)
timeFrame.grid(row=1, column=0, columnspan=4)
Label(timeFrame, text="Time:", justify="right", font=medium_font).grid(row=0, column=0, sticky='e')
minusButton = Button(timeFrame, text="-", width=1, command=time_minus)
minusButton.grid(row=0, column=1, padx=10)
timeLabel = Label(timeFrame, text=3, width=2, justify="center", font=medium_font)
timeLabel.grid(row=0, column=2)
plusButton = Button(timeFrame, text="+", width=1, command=time_plus)
plusButton.grid(row=0, column=3, padx=10)
falseStartButton = Button(timeFrame, text="Reset", width=2, command=time_reset)
falseStartButton.grid(row=0, column=4)

# Label displaying question # and associated buttons
questionFrame = Frame(root, borderwidth=5)
questionFrame.grid(row=2, column=0, columnspan=4, rowspan=2)
Label(questionFrame, justify="center").grid(row=0, column=0)
questionLabel = Label(questionFrame, justify="center", font=big_font, wraplength=1500)
questionLabel.grid(row=0, column=2)

blue_frame = Frame(root, width=750, height=400, borderwidth=8, background="blue")
blue_frame.grid(row=4, column=0, columnspan=2, rowspan=2)
blue_frame.grid_propagate(False)
blue_answer = Label(blue_frame, width=56, height=19, anchor="center", compound="center", font=big_font, fg="orange",
                    background="blue", wraplength=700)
blue_answer.grid(row=0, column=0, columnspan=1)

orange_frame = Frame(root, width=750, height=400, borderwidth=8, background="orange")
orange_frame.grid(row=4, column=2, columnspan=2, rowspan=2)
orange_frame.grid_propagate(False)
orange_answer = Label(orange_frame, width=56, height=19, compound="center", font=big_font, fg="blue",
                      background="orange", wraplength=700)
orange_answer.grid(row=0, column=1, columnspan=1)

green_frame = Frame(root, width=750, height=400, borderwidth=8, background="green")
green_frame.grid(row=6, column=0, columnspan=2, rowspan=2)
green_frame.grid_propagate(False)
green_answer = Label(green_frame, width=56, height=19, compound="center", font=big_font, fg="white", background="green",
                     wraplength=700)
green_answer.grid(row=1, column=0, columnspan=1)

yellow_frame = Frame(root, width=750, height=400, borderwidth=8, background="yellow")
yellow_frame.grid(row=6, column=2, columnspan=2, rowspan=2)
yellow_frame.grid_propagate(False)
yellow_answer = Label(yellow_frame, width=56, height=19, compound="center", font=big_font, fg="purple",
                      background="yellow", wraplength=700)
yellow_answer.grid(row=1, column=1, columnspan=1)

resetButton = Button(root, text="Reset", justify="center", width=20, height=2, command=reset, font=medium_font)
resetButton.grid(row=8, column=0)

startButton = Button(root, text="Start", justify="center", width=20, height=2, command=start, font=medium_font)
startButton.grid(row=8, column=3)

rounds = 5

# Initialise the buzzer and turn the lights off
buzz = BuzzController()
reset()

# Gets the requested values of the height and width.
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
print("Width", windowWidth, "Height", windowHeight)

# Gets both half the screen width/height and window width/height
positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
positionDown = int(root.winfo_screenheight() / 3 - windowHeight / 2)

# Positions the window in the center of the page.
root.geometry("+{}+{}".format(positionRight, positionDown))

print("Starting loop...")
root.mainloop()
