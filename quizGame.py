from __future__ import print_function

import time
import _thread
import json
from os import path
from tkinter import Tk, StringVar, Label, Button, Frame, DISABLED, NORMAL, Canvas
from PIL import ImageTk, Image

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
    global question_type, questions

    # Import and shuffle the questions
    question_file = open(file)
    questions_json = json.load(question_file)
    question_type = questions_json['type']
    for q in questions_json['questions']:
        num_answers = len(q["answers"])
        if num_answers == 4:
            buttons = ["blue", "orange", "green", "yellow"]
        else:
            buttons = ["blue", "orange", "green"]
        new_answer = {}
        shuffle(buttons)
        new_answer['question'] = q['question']
        new_answer['answer_count'] = num_answers
        for i in range(num_answers):
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
    current_question = 0
    startButton['text'] = "Start"
    startButton['state'] = NORMAL

    questionLabel.configure(text="Press Start to Begin")
    set_image(blue_answer, "Pictures/Blue.jpg")
    set_image(orange_answer, "Pictures/Orange.jpg")
    set_image(green_answer, "Pictures/Green.jpg")
    set_image(yellow_answer, "Pictures/Yellow.jpg")
    green_frame.grid(row=6, column=1, columnspan=2, rowspan=2)
    yellow_frame.grid_forget()


def set_label(label, text, colour):
    img = Image.open("Pictures/" + colour + ".jpg")
    resized_image = img.resize((750, 250), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(resized_image)
    label.config(image=image, text=text, width=740, height=250, font=big_font)
    label.image = image


def set_image(label, file):
    img = Image.open(file)
    resized_image = img.resize((750, 250), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(resized_image)
    label.configure(text="", image=image, width=750, height=250)
    label.image = image


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

    if question_type == "music":
        questionLabel.configure(text="Listen....")
        play_sound(tracks[current_question], 30)

    # Output the question
    questionLabel.configure(text=questions[current_question]["question"])
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
        current_question += 1
    else:
        startButton['text'] = "Next Question"
        startButton['state'] = DISABLED
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


def strikeout_answer(colour):
    strike_font = ("Sans", 30, "overstrike")
    if colour.lower() == "blue":
        blue_answer.configure(font=strike_font)
    elif colour.lower() == "orange":
        orange_answer.configure(font=strike_font)
    elif colour.lower() == "green":
        green_answer.configure(font=strike_font)
    elif colour.lower() == "yellow":
        yellow_answer.configure(font=strike_font)


def show_wrong_indicator():
    wrong_label = Label(root, text="X", font=("Sans", 400, "bold"), fg="red")
    wrong_label.place(relx=0.5, rely=0.5, anchor="center")
    root.update()
    time.sleep(1)
    wrong_label.destroy()


def show_correct_indicator():
    correct_label = Label(root, text="✓", font=("Sans", 400, "bold"), fg="green")
    correct_label.place(relx=0.5, rely=0.5, anchor="center")
    root.update()
    time.sleep(1)
    correct_label.destroy()


def wait_for_buzz(question_number):
    question_answered = False
    question = questions[question_number]
    num_answers = question.get('answer_count', 3)

    if num_answers == 4:
        available_answers = ["Blue", "Orange", "Green", "Yellow"]
        green_frame.grid(row=6, column=0, columnspan=2, rowspan=2)
        yellow_frame.grid(row=6, column=2, columnspan=2, rowspan=2)
    else:
        available_answers = ["Blue", "Orange", "Green"]
        green_frame.grid(row=6, column=1, columnspan=2, rowspan=2)
        yellow_frame.grid_forget()

    available_controllers = [0, 1, 2, 3]

    # Display the answers for the current question
    for answer in available_answers:
        set_answers(answer, question[answer.lower()])

    # Call this to start so that it resets any buzzers pushed before the question is set
    buzz.get_button_pressed(0)

    while not question_answered:
        if len(available_controllers) == 0:
            startButton['state'] = NORMAL
            break

        # Start the lights blinking and wait for a button press
        _thread.start_new_thread(buzz.light_blink, (available_controllers,))
        controller = buzz.controller_get_first_pressed("red", available_controllers)
        buzz.light_blink_stop()
        buzz.light_set(controller, True)
        play_sound('Sounds/buzzer.wav', 1)
        time.sleep(0.5)

        countdown = int(timeLabel['text'])
        while True:
            button = buzz.get_button_pressed(controller)
            buzz.light_blink_stop()

            if button and button != "red":
                if button == question["correct"]:
                    play_sound('Sounds/bell.wav', 0)
                    show_correct_indicator()
                    print("Controller " + str(controller + 1) + " was correct")
                    question_answered = True
                    update_score(controller, 1)
                    startButton['state'] = NORMAL
                    break
                elif button.capitalize() in available_answers:
                    play_sound('Sounds/wrong.wav', 0)
                    show_wrong_indicator()
                    print("Sorry incorrect answer")
                    strikeout_answer(button)
                    available_controllers.remove(controller)
                    available_answers.remove(button.capitalize())
                    break
            time.sleep(0.2)
            countdown -= 0.2
            if countdown < 0:
                play_sound('Sounds/wrong.wav', 0)
                show_wrong_indicator()
                available_controllers.remove(controller)
                break
        buzz.light_set(controller, False)
    time.sleep(1)


# Main Program
questions = []
question_type = ""
tracks = []
current_round = 1
current_question = 0
score = [0, 0, 0, 0]

root = Tk()
root.title("Buzz Quiz")
root.attributes('-fullscreen', True)

root.option_add('*Dialog.msg.font', 'Sans 10')

big_font = ("Sans", 30)
medium_font = ("Sans", 20)

# ScoreFrame
scoreFrame = Frame(root)
scoreFrame.grid(row=0, column=0, columnspan=4)
scoreLabel = Label(scoreFrame, text="Scores", justify="center", font=medium_font)
scoreLabel.pack()

def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)

def create_score_box(parent, team_name, color):
    canvas = Canvas(parent, width=250, height=120, highlightthickness=0)
    round_rectangle(canvas, 5, 5, 245, 115, radius=20, fill="white", outline="gray", width=2)
    lbl_name = Label(canvas, text=team_name, font=medium_font, bg="white")
    lbl_score = Label(canvas, text="0", font=medium_font, fg=color, bg="white")
    canvas.create_window(125, 40, window=lbl_name)
    canvas.create_window(125, 85, window=lbl_score)
    return canvas, lbl_score

scoreContainer = Frame(scoreFrame)
scoreContainer.pack()

c1, team1_score = create_score_box(scoreContainer, "Team 1", team1colour)
c1.pack(side="left", padx=10)

c2, team2_score = create_score_box(scoreContainer, "Team 2", team2colour)
c2.pack(side="left", padx=10)

c3, team3_score = create_score_box(scoreContainer, "Team 3", team3colour)
c3.pack(side="left", padx=10)

c4, team4_score = create_score_box(scoreContainer, "Team 4", team4colour)
c4.pack(side="left", padx=10)


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

blue_frame = Frame(root, width=750, height=250, borderwidth=8, background="blue")
blue_frame.grid(row=4, column=0, columnspan=2, rowspan=2)
blue_frame.grid_propagate(False)
blue_answer = Label(blue_frame, width=56, height=19, anchor="center", compound="center", font=big_font, fg="orange",
                    background="blue", wraplength=700)
blue_answer.grid(row=0, column=0, columnspan=1)

orange_frame = Frame(root, width=750, height=250, borderwidth=8, background="orange")
orange_frame.grid(row=4, column=2, columnspan=2, rowspan=2)
orange_frame.grid_propagate(False)
orange_answer = Label(orange_frame, width=56, height=19, compound="center", font=big_font, fg="blue",
                      background="orange", wraplength=700)
orange_answer.grid(row=0, column=1, columnspan=1)

green_frame = Frame(root, width=750, height=250, borderwidth=8, background="green")
green_frame.grid(row=6, column=1, columnspan=2, rowspan=2)
green_frame.grid_propagate(False)
green_answer = Label(green_frame, width=56, height=19, compound="center", font=big_font, fg="white", background="green",
                     wraplength=700)
green_answer.grid(row=1, column=0, columnspan=1)

yellow_frame = Frame(root, width=750, height=250, borderwidth=8, background="yellow")
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
