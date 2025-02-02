# Math Quizzer
# Made by squareroot12621 from 1/4/2024 to 2/1/2024.
# Designed to be run in IDLE.
#
# CHANGELOG:
# v1.3: 2/1/2024
#   - Added the version number to the main menu, instead of being
#     exclusively in the code.
#   - Added a 0.5-second buffer after the "Oops!" or "You ran out of
#     time!" screens, so that players, especially in timed difficulties,
#     wouldn't skip the correct answer or final score.
#   - Gave Easy, Normal, and Hard difficulties 10 seconds per problem
#     instead of 8.
#   - Revamped streaks to give a fair number of points.
#
# v1.2.1: 1/27/2024
#   - Changed the location of the page-turning button in the statistics
#     menu.
#
# v1.2: 1/23/2024
#   - Added timed difficulties, where you have to solve as many problems
#     as you can within 30 seconds, 1 minute, or 2 minutes. Note that
#     the "Correct!" screen will not appear.
#   - Added streaks--if you answer problems within 5 seconds, you grow
#     your streak and get more points.
#   - If you pressed the "Correct!" screen before the +1 animation
#     ended, it would be cut off. This is fixed.
#
# v1.1.1: 1/16/2024
#   - Tweaked the code to be more compliant with PEP 8 and PEP 257.
#   - Changed the minus sign during play from - to −. (Yes, there is a
#     difference.)
#   - The statistics menu now shows "You haven't attempted this
#     difficulty yet." when viewing a difficulty with no attempts.
#   - In a similar vein, durations in the statistics menu are shown
#     slightly differently.
#
# v1.1: 1/15/2024
#   - The program now automatically makes two new files, called
#     MATHQUIZZER-highscores.txt and MATHQUIZZER-other.txt, to store the
#     user's attempts and settings. Please make sure you don't have any
#     files with the same names before running the program for the first
#     time.
#   - This also gives the ability to show statistics, found in the play
#     screen. You can look at previous attempts for different
#     difficulties and try to improve on your high score.
#
# Earlier changes are located at aops.com/community/h3235279.

import math
import random
import time
import turtle

VERSION = 'v1.3'
BACKGROUND_COLOR = '#8070BF'
TEXT_COLOR = '#FFFFFF'

turtle.setup(420, 420)
window = turtle.Screen()
window.title('Math Quizzer')
window.bgcolor(BACKGROUND_COLOR)

turtle.tracer(0)

t = turtle.Turtle()

mode = 'menu'
data = None

points = 0
question = None
questionAnswer = ''
questionMakeTime = 0
questionCorrect = 0 # 0 = unanswered, 1 = correct, -1 = incorrect,
                    # -2 = out of time
AAAAAAAUnlocked = False
difficulty = 0 # 0 = not playing, 1+ = difficulty of round
answerTime = 0
pointsGained = 0
streak = 0
totalTime = 0
timedDifficulty = False
timeGameEnded = 0

answerInProgress = '' # Only used in difficulty 6
typingMessage = '' # Only used in difficulty 6

timeStarted = 0 # Only used in timed difficulties

tabDifficulty = 0 # Only used in the play menu

difficultyStatistics = 0 # Only used in statistics
tabStatistics = 0 # Only used in statistics
sortBy = 0 # Only used in statistics
pageStatistics = 0 # Only used in statistics
allAttempts = [] # Only used in statistics

# DATA:
#
# 3;3-7;3-10;r
# 3;            Weight (how often this operator is picked)
#   3-7;        First number range
#       3-10;   Second number range
#            r  Random order
#
# 2;6-15;3-10;g1
# 2;              Weight
#   6-15;         First number range
#        3-10;    Second number range
#             g1  First number is always greater than second number
#
# 2;10-25;3-6;w1
# 2;              Weight
#   10-25;        First number range
#         3-6;    Second number range
#             w1  Change w1 to nearest integer to make sure result is an
#                   integer

difficultyData = (None,
                  ['3;3-7;3-10;r', '2;6-15;3-10;g1', # Easy
                   '0;0-0;0-0;', '0;0-0;0-0;'],
                  ['2;5-11;5-13;r', '3;10-20;5-15;g1', # Medium
                   '3;2-8;4-10;r', '0;0-0;0-0;'],
                  ['3;7-18;10-25;r', '3;20-35;8-28;g1', # Hard
                   '6;3-10;7-12;r', '2;10-25;3-6;w1'],
                  ['2;10-25;15-40;r', '2;25-55;12-40;g1', # Harder
                   '5;4-12;8-16;r', '2;18-50;5-9;w1'],
                  ['2;17-40;25-75;r', '2;30-85;15-60;g1', # Insane
                   '7;5-15;10-20;r', '3;30-90;7-12;w1'],
                  ['2;30-100;50-150;r', '2;100-200;50-125;g1', # AAAAAAA
                   '7;8-20;15-25;r', '4;60-175;9-16;w1'],
                  ['4;7-18;10-25;r', '4;20-35;8-28;g1', # Timed
                   '7;3-10;7-12;r', '3;15-45;3-9;w1'])

def in_circle(x, y, targetX, targetY, radius):
    '''in_circle(x, y, targetX, targetY, radius) -> bool
    Returns a bool corresponding to whether (x, y) is inside a circle
    around (targetX, targetY) of radius radius.
    '''
    return (x - targetX) ** 2 + (y - targetY) ** 2 <= radius ** 2


def in_rectangle(x, y, leftX, topY, rightX, bottomY):
    '''in_rectangle(x, y, leftX, topY, rightX, bottomY) -> bool
    Returns a bool corresponding to whether (x, y) is in the rectangle
    constructed from the top-left corner (leftX, topY) and the
    bottom-right corner (rightX, bottomY).
    '''
    return leftX <= x <= rightX and bottomY <= y <= topY


def calculate(first, operation, second):
    '''calculate(first, operation, second) -> float OR int
    Calculates first operation second, according to the following table:
    0: +      1: -      2: *      3: /'''
    return [first + second, first - second,
            first * second, first / second][operation]


def make_question(data):
    '''make_question(data) -> (str, int, int, int, int, str, int)
    Makes a Math Quizzer question based off of data. The tuple is in the
    format (PROMPT, POSSIBLE ANSWERS, CORRECT LETTER, CORRECT NUMBER),
    where POSSIBLE ANSWERS takes up four elements.
    '''
    # Get the operation
    data = [i.split(';') for i in data]
    weights = [int(i[0]) for i in data]
    pickedNumber = random.randrange(0, sum(weights))
    pickedOperation = None
    for operation in range(4):
        if pickedNumber < sum(weights[0:operation + 1]):
            pickedOperation = operation
            break
    pickedOperationStr = '+−×÷'[operation]

    # Generate the numbers
    pickedData = data[operation][1:]
    firstNumberRange = pickedData[0].split('-')
    firstNumber = random.randrange(int(firstNumberRange[0]),
                                   int(firstNumberRange[1]) + 1)
    secondNumberRange = pickedData[1].split('-')
    secondNumber = random.randrange(int(secondNumberRange[0]),
                                    int(secondNumberRange[1]) + 1)

    # Edit the numbers according to the parameters
    parameter = pickedData[2]
    if parameter == '':
        pass
    elif parameter == 'r':
        (firstNumber, secondNumber) = (secondNumber, firstNumber)
    elif parameter == 'g1':
        if secondNumber >= firstNumber:
            secondNumber = random.randrange(int(secondNumberRange[0]),
                                            firstNumber)
    elif parameter == 'g2':
        if firstNumber >= secondNumber:
            firstNumber = random.randrange(int(firstNumberRange[0]),
                                           secondNumber)
    elif parameter == 'w1':
        firstNumber = round(firstNumber / secondNumber) * secondNumber
    else:
        raise ValueError("I don't know the parameter " + parameter
                         + ' yet, sorry.')

    if difficulty == 6:
        prompt = ('What is ' + str(firstNumber) + ' ' + pickedOperationStr
                  + ' ' + str(secondNumber) + '?')
        trueAnswer = calculate(firstNumber, pickedOperation, secondNumber)
        potentialAnswers = [trueAnswer, None, None, None]
        answerLetter = 'A'

    else: # Generate the question and possible answers (and true answer)
        prompt = ('What is ' + str(firstNumber) + ' ' + pickedOperationStr + ' '
                  + str(secondNumber) + '?')
        trueAnswer = calculate(firstNumber, pickedOperation, secondNumber)
        wrongAnswers = ([trueAnswer + i for i in (-10, -5, -3, -2, -1,
                                                  1, 2, 3, 5, 10)
                         if abs(i) <= 1.5 * (trueAnswer + 0.5) ** (1 / 3) + 1]
                        + [round(trueAnswer * random.uniform(0.75, 1.25))])
        if operation == 0:
            wrongAnswers.extend([abs(firstNumber - secondNumber)])
        elif operation == 1:
            wrongAnswers.extend([firstNumber + secondNumber])
        elif operation == 2:
            wrongAnswers.extend([trueAnswer - firstNumber,
                                 trueAnswer + firstNumber,
                                 trueAnswer - secondNumber,
                                 trueAnswer + secondNumber])
        elif operation == 3:
            wrongAnswers.extend([int(i) for i in
                                 [firstNumber / (secondNumber + 1),
                                  firstNumber / (secondNumber - 1)]
                                 if i % 1 == 0])
        wrongAnswers = list(set([int(i) for i in wrongAnswers
                                 if i != trueAnswer]))
        random.shuffle(wrongAnswers)
        potentialAnswers = wrongAnswers[:3] + [int(trueAnswer)]
        random.shuffle(potentialAnswers)
        answerLetter = 'ABCD'[potentialAnswers.index(trueAnswer)]
    
    return (prompt, *potentialAnswers, answerLetter, int(trueAnswer))


def red_green_gradient(num):
    '''red_green_gradient(num) -> str
    Returns a hexcode. If num is close to 0, the hexcode
    will be very red; if num is close to 1, the hexcode
    will be very green.
    '''
    if num > 0.5:
        return '#' + hex(int(510 * (1 - num)) + 256)[-2:].upper() + 'FF00'
    else:
        return '#FF' + hex(int(510 * num) + 256)[-2:].upper() + '00'

    
def draw_menu():
    '''Draws the Math Quizzer main menu.'''
    t.reset()
    t.penup()
    
    # Title
    t.goto(0, 110)
    t.color(TEXT_COLOR)
    t.write('MATH', align = 'center', font = ('Arial', 48, 'italic'))
    t.goto(0, 75)
    t.write('QUIZZER', align = 'center', font = ('Arial', 32, 'italic'))
    t.goto(0, 55)
    t.write(VERSION, align = 'center', font = ('Arial', 16, 'normal'))
    
    # Play button
    t.goto(-115, -100)
    t.pensize(4)
    t.color('#00BF00')
    t.fillcolor('#00EF00')
    t.pendown()
    t.begin_fill()
    t.circle(50)
    t.end_fill()
    t.penup()
    t.goto(-90, -50)
    t.color('#CF9F00')
    t.fillcolor('#EFCF00')
    t.pendown()
    t.begin_fill()
    t.goto(-130, -20)
    t.goto(-130, -80)
    t.goto(-90, -50)
    t.end_fill()
    t.penup()

    # Help button
    t.goto(0, -100)
    t.pensize(4)
    t.color('#AFAFAF')
    t.fillcolor('#FFFFFF')
    t.pendown()
    t.begin_fill()
    t.circle(50)
    t.end_fill()
    t.penup()
    t.color('#606060')
    t.goto(0, -97)
    t.write('?', align = 'center', font = ('Arial', 60, 'bold'))
    t.penup()
    
    # Quit button
    t.goto(115, -100)
    t.color('#AF0000')
    t.fillcolor('#FF0000')
    t.pendown()
    t.begin_fill()
    t.circle(50)
    t.end_fill()
    t.penup()
    t.pensize(9)
    t.color('#8F0000')
    t.goto(90, -25)
    t.pendown()
    t.goto(140, -75)
    t.penup()
    t.goto(140, -25)
    t.pendown()
    t.goto(90, -75)
    t.penup()
    
    t.hideturtle()
    window.update()


def draw_help():
    '''Draws the help screen in Math Quizzer.'''
    t.reset()
    t.penup()

    # Subtitle
    t.goto(0, 140)
    t.color(TEXT_COLOR)
    t.write('How do you play?', align = 'center',
            font = ('Arial', 24, 'italic'))

    # Instructions
    startingY = 90
    for line in ('To start the game, click on the play\n'
                 + 'button and choose the desired\n'
                 + 'difficulty. Then, on each math\n'
                 + 'problem, click on the correct answer\n'
                 + 'to each math problem to get a point.\n'
                 + 'However, you only get a few seconds\n'
                 + 'to answer each math problem. If you\n'
                 + 'answer incorrectly or you run out of\n'
                 + "time, it's game over. Try to get as\n"
                 + 'many points as you can!').split('\n'):
        t.goto(0, startingY)
        t.write(line, align = 'center', font = ('Arial', 14, 'normal'))
        startingY -= 22
    
    # Back button
    t.goto(-160, -190)
    t.pensize(4)
    t.color('#AF8E00')
    t.fillcolor('#FFCF00')
    t.pendown()
    t.begin_fill()
    t.circle(30)
    t.end_fill()
    t.penup()
    t.pensize(5)
    t.color('#805B00')
    t.goto(-155, -143)
    t.pendown()
    t.goto(-172, -160)
    t.goto(-155, -177)
    t.penup()
    
    t.hideturtle()
    window.update()

    
def draw_difficulty():
    '''Draws the difficulty-selecting screen in Math Quizzer.'''
    t.reset()
    t.penup()

    # Subtitle
    t.goto(0, 155)
    t.color(TEXT_COLOR)
    t.write('Select your difficulty:', align = 'center',
            font = ('Arial', 24, 'italic'))

    # Page button
    t.goto(-65, 87)
    t.pensize(4)
    t.color('#0040BF')
    t.fillcolor('#0055FF')
    t.pendown()
    t.begin_fill()
    t.goto(65, 87)
    t.goto(65, 123)
    t.goto(-65, 123)
    t.goto(-65, 87)
    t.end_fill()
    t.penup()
    t.color('#FFFFFF')
    if tabDifficulty == 0:
        t.goto(1, 91)
        t.write('Regular', align = 'center', font = ('Arial', 18, 'normal'))
    else:
        t.goto(1, 91)
        t.write('Timed', align = 'center', font = ('Arial', 18, 'normal'))

    # Buttons
    buttons = [[(-80, 40, '#009FFF', '#000000', '1', 'Easy'),
                (80, 40, '#00BF00', '#000000', '2', 'Normal'),
                (-80, -20, '#FFCF00', '#000000', '3', 'Hard'),
                (80, -20, '#FF3000', '#FFFFFF', '4', 'Harder'),
                (-80, -80, '#FF00FF', '#000000', '5', 'Insane'),
                (80, -80, '#8020BF', '#FFFFFF', '6', 'AAAAAAA')]
               [:5 + int(AAAAAAAUnlocked)],
               [(-80, 40, '#EF8F10', '#000000', ' 30', '  seconds'),
                (80, 40, '#90DF00', '#000000', '1', 'minute'),
                (-80, -20, '#00AF8F', '#000000', '2', 'minutes')]]
    for button in buttons[tabDifficulty]:
        t.goto(button[0] - 73, button[1] + 23)
        t.pensize(5)
        t.color('#60548F')
        t.fillcolor(button[2])
        t.pendown()
        t.begin_fill()
        t.goto(button[0] + 73, button[1] + 23)
        t.goto(button[0] + 73, button[1] - 23)
        t.goto(button[0] - 73, button[1] - 23)
        t.goto(button[0] - 73, button[1] + 23)
        t.end_fill()
        t.penup()
        t.color(button[3])
        if tabDifficulty == 0:
            t.goto(button[0] - 52, button[1] - 24)
            t.write(button[4], align = 'center',
                    font = ('Arial', 30, 'italic'))
            t.goto(button[0] - 30, button[1] - 14)
            t.write(button[5], align = 'left', font = ('Arial', 18, 'normal'))
        else:
            t.goto(button[0] - 52, button[1] - 19)
            t.write(button[4], align = 'center',
                    font = ('Arial', 24, 'normal'))
            t.goto(button[0] - 36, button[1] - 14)
            t.write(button[5], align = 'left', font = ('Arial', 18, 'normal'))
        t.goto(button[0] + 73, button[1] + 23)
        t.color('#60548F')
        t.pendown()
        t.goto(button[0] + 73, button[1] - 23)
        t.penup()

    # Back button
    t.goto(-160, -190)
    t.pensize(4)
    t.color('#AF8E00')
    t.fillcolor('#FFCF00')
    t.pendown()
    t.begin_fill()
    t.circle(30)
    t.end_fill()
    t.penup()
    t.pensize(5)
    t.color('#805B00')
    t.goto(-155, -143)
    t.pendown()
    t.goto(-172, -160)
    t.goto(-155, -177)
    t.penup()

    # Statistics button
    t.goto(160, -190)
    t.pensize(4)
    t.color('#00BF00')
    t.fillcolor('#00EF00')
    t.pendown()
    t.begin_fill()
    t.circle(30)
    t.end_fill()
    t.penup()
    t.pensize(3)
    t.color('#CF9F00')
    t.fillcolor('#EFCF00')
    for bar in [(141, 16), (155, 25), (169, 34)]:
        t.goto(bar[0], -177)
        t.pendown()
        t.begin_fill()
        t.goto(bar[0] + 10, -177)
        t.goto(bar[0] + 10, bar[1] - 177)
        t.goto(bar[0], bar[1] - 177)
        t.goto(bar[0], -177)
        t.end_fill()
        t.penup()
    
    t.hideturtle()
    window.update()


def draw_play():
    '''Draws the play screen in Math Quizzer.'''
    if not timedDifficulty:
        timeOnQuestion = time.time() - questionMakeTime
        if questionMakeTime == 0:
            timeOnQuestion = 0
    else:
        timeOnQuestion = time.time() - timeStarted
        if timeStarted == 0:
            timeOnQuestion = 0
    timeLeftFloat = totalTime - timeOnQuestion
    timeLeftInt = math.ceil(timeLeftFloat)
        
    t.reset()
    t.penup()

    # Points
    if questionCorrect >= 0:
        t.goto(190, -175)
        t.color('#FFFF00')
        if points == 1:
            t.write('1 point', align = 'right', font = ('Arial', 16, 'normal'))
        else:
            t.write(str(points) + ' points', align = 'right',
                    font = ('Arial', 16, 'normal'))
        
        timeSinceAnswered = time.time() - answerTime
        if timeSinceAnswered < 0.5:
            t.goto(123 - 6 * (len(str(points)) - 1)
                   + 11 * int(points == 1), 70 * timeSinceAnswered - 170)
            t.color('#' + hex(int(511 - 254 * timeSinceAnswered))[-2:].upper()
                    + hex(int(511 - 286 * timeSinceAnswered))[-2:].upper()
                    + hex(int(256 + 382 * timeSinceAnswered))[-2:].upper())
            t.write('+' + str(pointsGained), align = 'center',
                    font = ('Arial', 16, 'normal'))

    # Streak
    if questionCorrect >= 0:
        t.goto(-188, -32 * questionCorrect - 143)
        t.color(TEXT_COLOR)
        t.write('Streak: ' + str(streak), align = 'left',
                font = ('Arial', 16, 'normal'))
    
    if question != None and questionCorrect == 0:
        # Prompt
        t.goto(0, 140)
        t.color(TEXT_COLOR)
        t.write(question[0], align = 'center', font = ('Arial', 24, 'normal'))

        # Time left
        t.goto(-188, -179)
        t.pensize(0)
        t.fillcolor(TEXT_COLOR)
        t.pendown()
        t.begin_fill()
        for twoSides in range(2):
            t.forward(250)
            t.left(90)
            t.forward(34)
            t.left(90)
        t.end_fill()
        t.penup()
        t.fillcolor(red_green_gradient(timeLeftFloat / totalTime))
        t.pendown()
        t.begin_fill()
        for twoSides in range(2):
            t.forward(timeLeftFloat * 250 / totalTime)
            t.left(90)
            t.forward(34)
            t.left(90)
        t.end_fill()
        t.penup()
        t.color('#000000')
        t.pensize(3)
        t.pendown()
        for twoSides in range(2):
            t.forward(250)
            t.left(90)
            t.forward(34)
            t.left(90)
        t.penup()
        t.goto(-179, -175)
        t.write(str(timeLeftInt), \
                align = 'left', font = ('Arial', 16, 'normal'))

        if difficulty == 6: # Type the answer
            for button in [(-193, -158, -30, '1'),
                           (-154, -119, -30, '2'),
                           (-115, -80, -30, '3'),
                           (-76, -41, -30, '4'),
                           (-37, -2, -30, '5'),
                           (2, 37, -30, '6'),
                           (41, 76, -30, '7'),
                           (80, 115, -30, '8'),
                           (119, 154, -30, '9'),
                           (158, 193, -30, '0'),
                           (-193, -41, -80, 'Delete'),
                           (-37, 115, -80, 'Clear'),
                           (119, 193, -80, 'Go')]:
                t.goto(button[0], button[2] + 23)
                t.pensize(3)
                t.color('#60548F')
                if button[3] != 'Go':
                    t.fillcolor('#CFCFCF')
                else:
                    t.fillcolor('#00FF00')
                t.pendown()
                t.begin_fill()
                t.goto(button[1], button[2] + 23)
                t.goto(button[1], button[2] - 23)
                t.goto(button[0], button[2] - 23)
                t.goto(button[0], button[2] + 23)
                t.end_fill()
                t.penup()
                t.goto((button[0] + button[1]) / 2, button[2] - 19)
                t.color('#000000')
                t.write(button[3], align = 'center',
                        font = ('Arial', 24, 'normal'))
            t.goto(-193, 43)
            t.pensize(3)
            t.color('#60548F')
            t.fillcolor('#FFFFFF')
            t.pendown()
            t.begin_fill()
            t.goto(193, 43)
            t.goto(193, -3)
            t.goto(-193, -3)
            t.goto(-193, 43)
            t.end_fill()
            t.penup()
            t.goto(0, 1)
            t.color('#000000')
            t.write(answerInProgress, align = 'center',
                    font = ('Arial', 24, 'normal'))
            t.goto(0, 45)
            t.color(TEXT_COLOR)
            t.write(typingMessage, align = 'center',
                    font = ('Arial', 13, 'bold'))
        else: # Buttons
            for button in [(-80, 20, '#FF0040', '#FFFFFF', 'A)', question[1]),
                           (80, 20, '#FFCF00', '#000000', 'B)', question[2]),
                           (-80, -40, '#00DF00', '#000000', 'C)', question[3]),
                           (80, -40, '#009FFF', '#000000', 'D)', question[4])]:
                t.goto(button[0] - 73, button[1] + 23)
                t.pensize(5)
                t.color('#60548F')
                t.fillcolor(button[2])
                t.pendown()
                t.begin_fill()
                t.goto(button[0] + 73, button[1] + 23)
                t.goto(button[0] + 73, button[1] - 23)
                t.goto(button[0] - 73, button[1] - 23)
                t.goto(button[0] - 73, button[1] + 23)
                t.end_fill()
                t.penup()
                t.goto(button[0] - 45, button[1] - 22)
                t.color(button[3])
                t.write(button[4], align = 'center',
                        font = ('Arial', 28, 'italic'))
                t.goto(button[0] - 21, button[1] - 14)
                t.write(button[5], align = 'left',
                        font = ('Arial', 18, 'normal'))
    else:
        if questionCorrect == 1:
            # 'Correct!' message
            t.color('#00FF00')
            t.goto(0, 0)
            t.write('Correct!', align = 'center',
                    font = ('Arial', 28, 'normal'))
            t.color(TEXT_COLOR)
            t.goto(0, -28)
            t.write('(Click to continue.)', align = 'center',
                    font = ('Arial', 14, 'normal'))
        elif questionCorrect == -1:
            # 'Oops!' message
            t.color('#FF9F9F')
            t.goto(0, 0)
            t.write('Oops!', align = 'center', font = ('Arial', 28, 'normal'))
            t.goto(0, -28)
            t.write('The correct answer was ' + str(question[5]) + ') '
                    + str(question[6]) + '.', align = 'center',
                    font = ('Arial', 18, 'normal'))
            t.goto(0, -55)
            t.write('You finished with ' + str(points) + ' points.',
                    align = 'center', font = ('Arial', 18, 'normal'))
            t.color(TEXT_COLOR)
            t.goto(0, -82)
            t.write('(Click to return to the main menu.)', align = 'center',
                    font = ('Arial', 14, 'normal'))
        elif questionCorrect == -2 and not timedDifficulty:
            # 'You ran out of time!' message in regular gamemodes
            t.color('#FFFF00')
            t.goto(0, 0)
            t.write('You ran out of time!', align = 'center',
                    font = ('Arial', 28, 'normal'))
            t.goto(0, -28)
            t.write('The correct answer was ' + str(question[5]) + ') '
                    + str(question[6]) + '.', align = 'center',
                    font = ('Arial', 18, 'normal'))
            t.goto(0, -55)
            t.write('You finished with ' + str(points) + ' points.',
                    align = 'center', font = ('Arial', 18, 'normal'))
            t.color(TEXT_COLOR)
            t.goto(0, -82)
            t.write('(Click to return to the main menu.)', align = 'center',
                    font = ('Arial', 14, 'normal'))
        elif questionCorrect == -2 and timedDifficulty:
            # 'You ran out of time!' message in timed gamemodes
            t.color('#FFFF00')
            t.goto(0, 0)
            t.write('You ran out of time!', align = 'center',
                    font = ('Arial', 28, 'normal'))
            t.goto(0, -28)
            t.write('You finished with ' + str(points) + ' points.',
                    align = 'center', font = ('Arial', 18, 'normal'))
            t.color(TEXT_COLOR)
            t.goto(0, -55)
            t.write('(Click to return to the main menu.)', align = 'center',
                    font = ('Arial', 14, 'normal'))
    
    t.hideturtle()
    window.update()


def draw_statistics():
    '''Draws the statistics screen.'''    
    t.reset()
    t.penup()

    # 'Stats for:' header
    t.goto(-180, 150)
    t.pensize(4)
    t.color('#0040BF')
    t.fillcolor('#0055FF')
    t.pendown()
    t.begin_fill()
    t.goto(-70, 150)
    t.goto(-70, 185)
    t.goto(-180, 185)
    t.goto(-180, 150)
    t.end_fill()
    t.penup()
    t.color('#FFFFFF')
    t.goto(-124, 153)
    if tabStatistics == 0:
        t.write('Regular', align = 'center', font = ('Arial', 18, 'normal'))
    else:
        t.write('Timed', align = 'center', font = ('Arial', 18, 'normal'))
        
    headerButtons = [[(-35, '1', '#009FFF', '#000000', 1),
                      (5, '2', '#00BF00', '#000000', 2),
                      (45, '3', '#FFCF00', '#000000', 3),
                      (85, '4', '#FF3000', '#FFFFFF', 4),
                      (125, '5', '#FF00FF', '#000000', 5),
                      (165, '6', '#8020BF', '#FFFFFF', 6)]
                     if AAAAAAAUnlocked else
                     [(-35, '1', '#009FFF', '#000000', 1),
                      (5, '2', '#00BF00', '#000000', 2),
                      (45, '3', '#FFCF00', '#000000', 3),
                      (85, '4', '#FF3000', '#FFFFFF', 4),
                      (125, '5', '#FF00FF', '#000000', 5)],
                     [(-35, '30s', '#EF8F10', '#000000', 7),
                      (5, '1m', '#90DF00', '#000000', 8),
                      (45, '2m', '#00AF8F', '#000000', 9)]]
    t.pensize(3)
    for headerButton in headerButtons[tabStatistics]:
        t.color('#60548F')
        if difficultyStatistics == headerButton[4]:
            t.fillcolor(headerButton[2])
        else:
            t.fillcolor('#FFFFFF')
        t.goto(headerButton[0], 151)
        t.pendown()
        t.begin_fill()
        t.circle(18)
        t.end_fill()
        t.penup()
        if difficultyStatistics == headerButton[4]:
            t.color(headerButton[3])
        else:
            t.color('#000000')
        if len(headerButton[1]) == 1:
            t.goto(headerButton[0] + 1, 155)
            t.write(headerButton[1], align = 'center',
                    font = ('Arial', 19, 'normal'))
        elif len(headerButton[1]) == 2:
            t.goto(headerButton[0] + 1, 158)
            t.write(headerButton[1], align = 'center',
                    font = ('Arial', 15, 'normal'))
        else:
            for pos in [(0.5, 0.5), (0.5, 1), (1, 0.5), (1, 1)]:
                t.goto(headerButton[0] + pos[0], 159 + pos[1])
                t.write(headerButton[1], align = 'center',
                        font = ('Arial', 13, 'normal'))

    # Quick statistics (left side)
    allAttempts = [i for i in highscoresList[1:] if i != ''
                   and int(i.split(' ')[1]) == difficultyStatistics]
    pointTotals = [int(i.split(' ')[2]) for i in allAttempts]
    numAttempts = len(allAttempts)
    if numAttempts == 0:
        averagePoints = 'N/A'
        maxPoints = 'N/A'
    else:
        averagePoints = sum(pointTotals) / numAttempts
        if averagePoints % 1 == 0:
            averagePoints = int(averagePoints)
        elif averagePoints < 9.9995:
            averagePoints = round(averagePoints, 3)
        elif averagePoints < 99.995:
            averagePoints = round(averagePoints, 2)
        else:
            averagePoints = round(averagePoints, 1)
        maxPoints = max(pointTotals)

    t.color(TEXT_COLOR)
    overallStatsY = 105
    for line in [('Attempts:', str(numAttempts)),
                 ('Average:', str(averagePoints)),
                 ('Max:', str(maxPoints))]:
        t.goto(-130, overallStatsY)
        t.write(line[0], align = 'center', font = ('Arial', 18, 'normal'))
        t.goto(-130, overallStatsY - 40)
        t.write(line[1], align = 'center', font = ('Arial', 28, 'normal'))
        overallStatsY -= 75
    
    # Table of attempts (right side)
    if len(allAttempts) == 0:
        t.goto(57, 40)
        t.write("You haven't attempted", align = 'center',
                font = ('Arial', 14, 'italic'))
        t.goto(57, 18)
        t.write('this difficulty yet.', align = 'center',
                font = ('Arial', 14, 'italic'))
    else:
        t.goto(15, 105)
        t.write('Time Done', align = 'center', font = ('Arial', 18, 'bold'))
        t.goto(130, 105)
        t.write('Points', align = 'center', font = ('Arial', 18, 'bold'))
        tableAttemptsY = 75
        if sortBy == 0: # Newest
            sortKey = lambda n: int(n.split(' ')[0])
        else: # High Scores
            sortKey = lambda n: int(n.split(' ')[2])
        sortedAttempts = sorted(allAttempts, key = sortKey, reverse = True)
        
        for attempt in sortedAttempts[8*pageStatistics : 8*pageStatistics + 8]:
            t.goto(15, tableAttemptsY)
            timeAgo = int(time.time() - int(attempt.split(' ')[0]))
            if timeAgo < 60:
                timeStr = str(timeAgo) + 's ago'
            elif timeAgo < 3600:
                if timeAgo % 60 == 0:
                    timeStr = str(timeAgo // 60) + 'm ago'
                else:
                    timeStr = (str(timeAgo // 60) + 'm ' + str(timeAgo % 60)
                               + 's ago')
            elif timeAgo < 86400:
                if timeAgo % 3600 < 60:
                    timeStr = str(timeAgo // 3600) + 'h ago'
                else:
                    timeStr = (str(timeAgo // 3600) + 'h '
                               + str((timeAgo // 60) % 60) + 'm ago')
            elif timeAgo < 8640000: # 100 days
                if timeAgo % 86400 < 3600:
                    timeStr = str(timeAgo // 86400) + 'd ago'
                else:
                    timeStr = (str(timeAgo // 86400) + 'd '
                               + str((timeAgo // 3600) % 24) + 'h ago')
            else:
                timeStr = str(timeAgo // 86400) + 'd ago'
            t.write(timeStr, align = 'center', font = ('Arial', 18, 'normal'))
            t.goto(130, tableAttemptsY)
            t.write(attempt.split(' ')[2], align = 'center',
                    font = ('Arial', 18, 'normal'))
            tableAttemptsY -= 28
    
    # Back button
    t.goto(-160, -190)
    t.pensize(4)
    t.color('#AF8E00')
    t.fillcolor('#FFCF00')
    t.pendown()
    t.begin_fill()
    t.circle(30)
    t.end_fill()
    t.penup()
    t.pensize(5)
    t.color('#805B00')
    t.goto(-155, -143)
    t.pendown()
    t.goto(-172, -160)
    t.goto(-155, -177)
    t.penup()

    # Sort button
    t.goto(-70, -190)
    t.pensize(4)
    t.color('#0040BF')
    t.fillcolor('#0055FF')
    t.pendown()
    t.begin_fill()
    t.goto(30, -190)
    t.goto(30, -160)
    t.goto(-70, -160)
    t.goto(-70, -190)
    t.end_fill()
    t.penup()
    t.color('#FFFFFF')
    if sortBy == 0:
        t.goto(-19, -187)
        t.write('Newest', align = 'center', font = ('Arial', 16, 'normal'))
    else:
        t.goto(-19, -184)
        t.write('High Scores', align = 'center',
                font = ('Arial', 12, 'normal'))
    t.goto(-19, -157)
    t.write('Sort by:', align = 'center', font = ('Arial', 16, 'normal'))

    # Page up/down buttons
    t.goto(90, -190)
    t.pensize(4)
    t.color('#0040BF')
    t.fillcolor('#0055FF')
    t.pendown()
    t.begin_fill()
    t.circle(30)
    t.end_fill()
    t.penup()
    t.pensize(5)
    t.color('#FFFFFF')
    t.fillcolor('#FFFFFF')
    t.goto(103, -168)
    t.pendown()
    t.begin_fill()
    t.goto(90, -148)
    t.goto(77, -168)
    t.goto(103, -168)
    t.end_fill()
    t.penup()
    
    t.goto(160, -190)
    t.pensize(4)
    t.color('#0040BF')
    t.fillcolor('#0055FF')
    t.pendown()
    t.begin_fill()
    t.circle(30)
    t.end_fill()
    t.penup()
    t.pensize(5)
    t.color('#FFFFFF')
    t.fillcolor('#FFFFFF')
    t.goto(173, -152)
    t.pendown()
    t.begin_fill()
    t.goto(160, -172)
    t.goto(147, -152)
    t.goto(173, -152)
    t.end_fill()
    t.penup()
    
    t.hideturtle()
    window.update()
    
def draw_error(message = 'Unknown error occurred.'):
    '''Draws an error screen.'''
    global mode
    if mode != 'error':
        t.reset()
        t.penup()

        # Error message
        window.bgcolor('#000000')
        t.goto(-180, 0)
        t.color('#FFFFFF')
        t.write(message + '\nClick anywhere to quit.', align = 'left',
                font = ('Courier', 14, 'normal'))
        t.hideturtle()
        mode = 'error'
    
    window.update()


def question_handler():
    '''Handles questions during play.'''
    global mode, data, question, questionAnswer, questionCorrect, \
           questionMakeTime, points, answerInProgress, answerTime, \
           pointsGained, streak, timeStarted, timeGameEnded
    timeOnQuestion = time.time() - questionMakeTime
    if questionMakeTime == 0:
        timeOnQuestion = 0
    if mode not in ['play 1', 'play 2', 'play 3']:
        return None
    if mode == 'play 3':
        question = make_question(data)
        questionMakeTime = time.time()
        questionAnswer = ''
        questionCorrect = 0
        mode = 'play 1'
        answerInProgress = ''
    elif mode == 'play 1' and questionAnswer == question[5]: # Correct answer
        answerTime = time.time()
        if timeOnQuestion <= 5:
            streak += 1
            pointsGained = [None,
                            max(streak - 2, 1) ** 0.35,
                            max(streak - 1, 1) ** 0.43,
                            streak ** 0.5,
                            streak ** 0.6,
                            streak ** 0.7,
                            streak ** 0.8,
                            streak ** 0.6,
                            streak ** 0.53,
                            streak ** 0.45][difficulty]
            pointsGained = math.ceil(pointsGained)
        else:
            streak = 0
            pointsGained = 1
        points += pointsGained
        questionCorrect = 1
        if not timedDifficulty:
            mode = 'play 2'
        else:
            mode = 'play 3'
            question_handler()
    elif mode == 'play 1' and questionAnswer in ['A', 'B', 'C', 'D']:
        # Wrong answer
        mode = 'play 2'
        questionCorrect = -1
        timeGameEnded = time.time()
        save_score(int(timeGameEnded), difficulty, points)
    elif (mode == 'play 1' and questionAnswer == ''
          and [timeOnQuestion, time.time() - timeStarted][int(timedDifficulty)]
          >= totalTime):
        # Ran out of time
        mode = 'play 2'
        questionCorrect = -2
        save_score(int(time.time()), difficulty, points)

    
def draw_screen():
    '''Draws the screen for Math Quizzer.'''
    if mode == 'menu':
        draw_menu()
    elif mode == 'help':
        draw_help()
    elif mode == 'difficulty':
        draw_difficulty()
    elif mode in ['play 1', 'play 2', 'play 3']:
        draw_play()
    elif mode == 'statistics':
        draw_statistics()
    else:
        draw_error('Unknown mode: ' + repr(mode))


def click_handler(x, y):
    '''Handles clicks from the screen.'''
    global mode, data, questionAnswer, questionCorrect, questionMakeTime, \
           AAAAAAAUnlocked, difficulty, answerInProgress, typingMessage, \
           question, points, difficultyStatistics, sortBy, pageStatistics, \
           tabDifficulty, tabStatistics, timeStarted, totalTime, \
           timedDifficulty, streak
    if mode == 'menu':
        if in_circle(x, y, -115, -50, 52): # Play button
            mode = 'difficulty'
        elif in_circle(x, y, 0, -50, 52): # Help button
            mode = 'help'
        elif in_circle(x, y, 115, -50, 52): # Quit button
            quit_game()
    elif mode == 'help':
        if in_circle(x, y, -160, -160, 32): # Back button
            mode = 'menu'
    elif mode == 'difficulty':
        if tabDifficulty == 0:
            if in_rectangle(x, y, -156, 66, -4, 14): # Easy button
                mode = 'play 3'
                data = difficultyData[1]
                difficulty = 1
                totalTime = 10
            elif in_rectangle(x, y, 4, 66, 156, 14): # Normal button
                mode = 'play 3'
                data = difficultyData[2]
                difficulty = 2
                totalTime = 10
            elif in_rectangle(x, y, -156, 6, -4, -46): # Hard button
                mode = 'play 3'
                data = difficultyData[3]
                difficulty = 3
                totalTime = 10
            elif in_rectangle(x, y, 4, 6, 156, -46): # Harder button
                mode = 'play 3'
                data = difficultyData[4]
                difficulty = 4
                totalTime = 8
            elif in_rectangle(x, y, -156, -54, -4, -106): # Insane button
                mode = 'play 3'
                data = difficultyData[5]
                difficulty = 5
                totalTime = 8
            elif in_rectangle(x, y, 4, -54, 156, -106): # AAAAAAA button
                if AAAAAAAUnlocked:
                    mode = 'play 3'
                    data = difficultyData[6]
                    difficulty = 6
                    totalTime = 8
                else:
                    AAAAAAAUnlocked = True
        elif tabDifficulty == 1:
            if in_rectangle(x, y, -156, 66, -4, 14): # 30 seconds button
                mode = 'play 3'
                data = difficultyData[7]
                difficulty = 7
                timeStarted = time.time()
                totalTime = 30
                timedDifficulty = True
            elif in_rectangle(x, y, 4, 66, 156, 14): # 1 minute button
                mode = 'play 3'
                data = difficultyData[7]
                difficulty = 8
                timeStarted = time.time()
                totalTime = 60
                timedDifficulty = True
            elif in_rectangle(x, y, -156, 6, -4, -46): # 2 minutes button
                mode = 'play 3'
                data = difficultyData[7]
                difficulty = 9
                timeStarted = time.time()
                totalTime = 120
                timedDifficulty = True
        if in_rectangle(x, y, -68, 126, 68, 84): # Gamemode type button
            tabDifficulty = 1 - tabDifficulty
        elif in_circle(x, y, -160, -160, 32): # Back button
            mode = 'menu'
            tabDifficulty = 0
        elif in_circle(x, y, 160, -160, 32): # Statistics button
            mode = 'statistics'
            tabDifficulty = 0
            difficultyStatistics = 1
    elif mode == 'play 1':
        if difficulty == 6:
            for button in [(-193, -158, -30, '1'),
                           (-154, -119, -30, '2'),
                           (-115, -80, -30, '3'),
                           (-76, -41, -30, '4'),
                           (-37, -2, -30, '5'),
                           (2, 37, -30, '6'),
                           (41, 76, -30, '7'),
                           (80, 115, -30, '8'),
                           (119, 154, -30, '9'),
                           (158, 193, -30, '0'),
                           (-193, -41, -80, 'Delete'),
                           (-37, 115, -80, 'Clear'),
                           (119, 193, -80, 'Go')]:
                if in_rectangle(x, y, button[0] - 2, button[2] + 25,
                                button[1] + 2, button[2] - 25):
                    typingMessage = ''
                    if len(button[3]) == 1: # Digit
                        if len(answerInProgress) == 20:
                            typingMessage = ("The answer's obviously"
                                             + 'smaller than that.')
                        elif answerInProgress == '0':
                            answerInProgress = button[3]
                        else:
                            answerInProgress += button[3]
                    elif button[3] == 'Delete': # Delete
                        if len(answerInProgress) > 0:
                            answerInProgress = answerInProgress[:-1]
                    elif button[3] == 'Clear': # Clear
                        answerInProgress = '0'
                    elif button[3] == 'Go': # Go
                        if answerInProgress == '':
                        # Tried to enter a blank answer
                            typingMessage = 'Please enter a number.'
                        else:
                            answerInProgress = int(answerInProgress)
                            if answerInProgress == question[6]:
                                questionAnswer = 'A'
                            else:
                                questionAnswer = 'B'
        else:
            if in_rectangle(x, y, -156, 46, -4, -6): # A) button
                questionAnswer = 'A'
            elif in_rectangle(x, y, 4, 46, 156, -6): # B) button
                questionAnswer = 'B'
            elif in_rectangle(x, y, -156, -14, -4, -66): # C) button
                questionAnswer = 'C'
            elif in_rectangle(x, y, 4, -14, 156, -66): # D) button
                questionAnswer = 'D'
    elif mode == 'play 2' and questionCorrect == 1:
    # Click after a correct answer
        mode = 'play 3'
    elif mode == 'play 2' and questionCorrect < 0:
    # Click after a wrong answer
        if time.time() - timeGameEnded >= 0.5:
            question = None
            questionCorrect = 0
            questionMakeTime = 0
            mode = 'menu'
            points = 0
            difficulty = 0
            answerInProgress = ''
            streak = 0
    elif mode == 'statistics': # Statistics screen
        if in_rectangle(x, y, -182, 187, -68, 148): # Tab button, part 1
            tabStatistics = 1 - tabStatistics
        headerButtons = [[(-35, 1), (5, 2), (45, 3), (85, 4),
                          (125, 5), (165, 6)] if AAAAAAAUnlocked else
                         [(-35, 1), (5, 2), (45, 3), (85, 4),
                          (125, 5)],
                         [(-35, 7), (5, 8), (45, 9)]][tabStatistics]
        if in_circle(x, y, -160, -160, 32): # Back button
            mode = 'difficulty'
            difficultyStatistics = 0
            tabStatistics = 0
        elif in_circle(x, y, 90, -160, 32): # Page up button
            if pageStatistics != 0:
                pageStatistics -= 1
        elif in_circle(x, y, 160, -160, 32): # Page down button
            if pageStatistics != -(len(allAttempts) // -8) - 1:
                pageStatistics += 1
        elif in_rectangle(x, y, -182, 187, -68, 148): # Tab button, part 2
            difficultyStatistics = headerButtons[0][1]
        elif in_rectangle(x, y, -72, -158, 32, -192): # 'Sort by' button
            sortBy = 1 - sortBy
        for button in headerButtons:
            if in_circle(x, y, button[0], 169, 20):
                difficultyStatistics = button[1]
                pageStatistics = 0
    elif mode == 'error': # Error screen; 'Click anywhere to quit.'
        quit_game()


def quit_game():
    '''Closes the Math Quizzer game.'''
    highscoresFile.close()
    otherFile.close()
    window.bye()


def find_scores():
    '''Turns the scores from the MATHQUIZZER-highscores.txt file into a
    nested list, then returns it.
    '''
    return [[int(i) for i in line.split(' ')] for line in highscoresList[1:]
            if line != '']


def save_score(timeFinished, difficulty, points):
    '''Saves score to MATHQUIZZER-highscores.txt, according to
    timeFinished, difficulty, and points.
    '''
    global highscoresFile, highscoresText, highscoresList, highScores
    highscoresFile.write(str(timeFinished) + ' ' + str(difficulty)
                         + ' ' + str(points) + '\n')
    highscoresFile.flush()
    highscoresText += (str(timeFinished) + ' ' + str(difficulty) + ' '
                       + str(points) + '\n')
    highscoresList = highscoresText.split('\n')
    highScores = find_scores()


# Open files MATHQUIZZER-highscores.txt and MATHQUIZZER-other.txt,
# throwing an error if they exist and the first line isn't the standard
# header
try:
    highscoresFile = open('MATHQUIZZER-highscores.txt', 'r+')
except OSError:
    highscoresFile = open('MATHQUIZZER-highscores.txt', 'w+')
    highscoresFile.write('# Belongs to the game Math Quizzer.\n')
highscoresFile.seek(0)
highscoresText = highscoresFile.read()
highscoresList = highscoresText.split('\n')
if not highscoresText.startswith('# Belongs to the game Math Quizzer.'):
    raise Exception('File MATHQUIZZER-highscores.txt is not formed properly. '
                    + 'Please rename the file, then try again.')
else:
    highScores = find_scores()

try:
    otherFile = open('MATHQUIZZER-other.txt', 'r+')
except OSError:
    otherFile = open('MATHQUIZZER-other.txt', 'w+')
    otherFile.write('# Belongs to the game Math Quizzer.\n')
otherFile.seek(0)
otherText = otherFile.read()
if not otherText.startswith('# Belongs to the game Math Quizzer.'):
    raise Exception('File MATHQUIZZER-other.txt is not formed properly. '
                    + 'Please rename the file, then try again.')
else:
    AAAAAAAUnlocked = 'AAAAAAAUnlocked\n' in otherText


while True:
    question_handler()
    draw_screen()
    window.onclick(click_handler)
    if AAAAAAAUnlocked and 'AAAAAAAUnlocked\n' not in otherText:
        otherFile.write('AAAAAAAUnlocked\n')
        otherFile.flush()
        otherText += 'AAAAAAAUnlocked\n'

window.listen()
window.mainloop()
