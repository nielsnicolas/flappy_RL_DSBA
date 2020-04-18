from itertools import cycle
import random
import sys
import os
import argparse
import pickle

# importing pandas as pd  
import pandas as pd  

import numpy as np
from numpy import convolve
import matplotlib.pyplot as plt


import pygame
from pygame.locals import *

sys.path.append(os.getcwd())

from bot import Bot


# Initialize the bot
bot = Bot()

SCREENWIDTH = 288
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE = 100  # gap between upper and lower part of pipe
BASEY = SCREENHEIGHT * 0.79

# image width height indices for ease of use
IM_WIDTH = 0
IM_HEIGTH = 1
# image, Width, Height
PIPE = [52, 320]
PLAYER = [34, 24]
BASE = [336, 112]
BACKGROUND = [288, 512]


def main():
    global HITMASKS, ITERATIONS, VERBOSE, bot, list_scoring, success_rates, one_digits_list, two_digits_list, three_digits_list, more_than_four_digits_list

    parser = argparse.ArgumentParser("learn.py")
    parser.add_argument("--iter", type=int, default=1000, help="number of iterations to run")
    parser.add_argument(
        "--verbose", action="store_true", help="output [iteration | score] to stdout"
    )
    args = parser.parse_args()
    ITERATIONS = args.iter
    VERBOSE = args.verbose

    list_scoring = []
    success_rates = []
    one_digits_list = []
    two_digits_list = []
    three_digits_list = [] 
    more_than_four_digits_list = []

    # load dumped HITMASKS
    with open("data/hitmasks_data.pkl", "rb") as input:
        HITMASKS = pickle.load(input)

    while True:
        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        score = crashInfo["score"]
        showGameOverScreen(crashInfo)
        list_scoring.append(score)
        success_rates.append(sum(list_scoring)/(sum(list_scoring)+bot.gameCNT))
        one_digits_list.append((sum(1 for i in list_scoring if i <10)/bot.gameCNT)*100)
        two_digits_list.append((sum(1 for i in list_scoring if i >=10 and i<100)/bot.gameCNT)*100)
        three_digits_list.append((sum(1 for i in list_scoring if i >=100 and i<1000)/bot.gameCNT)*100)
        more_than_four_digits_list.append((sum(1 for i in list_scoring if i >=1000)/bot.gameCNT)*100)



def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    playerIndexGen = cycle([0, 1, 2, 1])

    playery = int((SCREENHEIGHT - PLAYER[IM_HEIGTH]) / 2)

    basex = 0

    # player shm for up-down motion on welcome screen
    playerShmVals = {"val": 0, "dir": 1}

    return {
        "playery": playery + playerShmVals["val"],
        "basex": basex,
        "playerIndexGen": playerIndexGen,
    }


def mainGame(movementInfo):

    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo["playerIndexGen"]

    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo["playery"]

    basex = movementInfo["basex"]
    baseShift = BASE[IM_WIDTH] - BACKGROUND[IM_WIDTH]

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {"x": SCREENWIDTH + 200, "y": newPipe1[0]["y"]},
        {"x": SCREENWIDTH + 200 + (SCREENWIDTH / 2), "y": newPipe2[0]["y"]},
    ]

    # list of lowerpipe
    lowerPipes = [
        {"x": SCREENWIDTH + 200, "y": newPipe1[1]["y"]},
        {"x": SCREENWIDTH + 200 + (SCREENWIDTH / 2), "y": newPipe2[1]["y"]},
    ]

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY = -9  # player's velocity along Y, default same as playerFlapped
    playerMaxVelY = 10  # max vel along Y, max descend speed
    playerMinVelY = -8  # min vel along Y, max ascend speed
    playerAccY = 1  # players downward accleration
    playerFlapAcc = -9  # players speed on flapping
    playerFlapped = False  # True when player flaps

    while True:
        if -playerx + lowerPipes[0]["x"] > -30:
            myPipe = lowerPipes[0]
        else:
            myPipe = lowerPipes[1]

        if bot.act(-playerx + myPipe["x"], -playery + myPipe["y"], playerVelY):
            if playery > -2 * PLAYER[IM_HEIGTH]:
                playerVelY = playerFlapAcc
                playerFlapped = True

        # check for crash here
        crashTest = checkCrash(
            {"x": playerx, "y": playery, "index": playerIndex}, upperPipes, lowerPipes
        )
        if crashTest[0]:
            # Update the q scores
            bot.update_scores(dump_qvalues=False)
            #bot.update_scores(dump_qvalues=False, dump_scores=False)

            return {
                "y": playery,
                "groundCrash": crashTest[1],
                "basex": basex,
                "upperPipes": upperPipes,
                "lowerPipes": lowerPipes,
                "score": score,
                "playerVelY": playerVelY,
            }

        # check for score
        playerMidPos = playerx + PLAYER[IM_WIDTH] / 2
        for pipe in upperPipes:
            pipeMidPos = pipe["x"] + PIPE[IM_WIDTH] / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
        playerHeight = PLAYER[IM_HEIGTH]
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe["x"] += pipeVelX
            lPipe["x"] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]["x"] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]["x"] < -PIPE[IM_WIDTH]:
            upperPipes.pop(0)
            lowerPipes.pop(0)


def showGameOverScreen(crashInfo):

    def movingaverage (values, window):
        weights = np.repeat(1.0, window)/window
        sma = np.convolve(values, weights, 'same')
        return sma

    if VERBOSE:
        score = crashInfo["score"]

        print(str(bot.gameCNT - 1) + " | " + str(score))


    if bot.gameCNT == (ITERATIONS):
        print('the avegare score is',sum(list_scoring)/bot.gameCNT,'during those',ITERATIONS,'games')
        print('the max score is',max(list_scoring),'during those',ITERATIONS,'games')
        #print('during these',ITERATIONS,'games, they were',sum(1 for i in list_scoring if i <10),'games scored single-digits-numbers and they represent',(sum(1 for i in list_scoring if i <10)/bot.gameCNT)*100,'%')
        #print('during these',ITERATIONS,'games, they were',sum(1 for i in list_scoring if i >=10 and i<100),'games scored 2-digits-numbers and they represent',(sum(1 for i in list_scoring if i >=10 and i<100)/bot.gameCNT)*100,'%')
        #print('during these',ITERATIONS,'games, they were',sum(1 for i in list_scoring if i >=100 and i<1000),'games scored 3-digits-numbers and they represent',(sum(1 for i in list_scoring if i >=100 and i<1000)/bot.gameCNT)*100,'%')
        #print('during these',ITERATIONS,'games, they were',sum(1 for i in list_scoring if i >=1000),'games scored more than 4-digits-numbers and they represent',(sum(1 for i in list_scoring if i >=1000)/bot.gameCNT)*100,'%')
        #print(list_scoring)
        #print(success_rates)
  
        # dictionary of lists  
        dict_for_pd = {'the scores': list_scoring, 'sucess rate': success_rates, 'one digit scores': one_digits_list, 'two digits scores': two_digits_list, 'three digits scores': three_digits_list, 'four and more digits scores': more_than_four_digits_list}  
    
        df = pd.DataFrame(dict_for_pd) 
        print(df.tail())
        df.to_csv('our_results_lr_08.csv')


        x = list(range(bot.gameCNT-1))

        y1 = list_scoring
        y2 = success_rates
        y3 = one_digits_list 
        y4 = two_digits_list 
        y5 = three_digits_list 
        y6 = more_than_four_digits_list 



        # Calculate the simple average of the data
        y_mean = [np.mean(y1)]*len(x)

        fig, (ax1, ax2, ax3) = plt.subplots(3)

        # Plot the moving average line
        yMA = movingaverage(y1,100)

        ax1.plot(x,yMA, label='Moving Avegare (window=100)', linestyle='-', color='b')
        ax1.scatter(x, y1, s=2, c='gray')
        ax1.set_title('score per game')
        ax1.axhline(y=100,color='red',linestyle='-.', lw=0.5)
        ax1.axhline(y=500,color='red',linestyle='-', lw=1)


        ax2.plot(x, y2)
        ax2.set_title('evolution of success rate')
        ax2.axhline(y=1,color='red',linestyle='-.', lw=0.5)


        ax3.plot(x, y3, label='proportion of 1-digits scores')
        ax3.plot(x, y4, label='proportion of 2-digits scores')
        ax3.plot(x, y5, label='proportion of 3-digits scores')
        ax3.plot(x, y6, label='proportion of 4-digits and beyond scores')


        # Make a legend
        ax1.legend(loc='upper left')
        ax3.legend(loc='upper left')

        plt.show()

        bot.dump_qvalues(force=True)
        sys.exit()



def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm["val"]) == 8:
        playerShm["dir"] *= -1

    if playerShm["dir"] == 1:
        playerShm["val"] += 1
    else:
        playerShm["val"] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = PIPE[IM_HEIGTH]
    pipeX = SCREENWIDTH + 10

    return [
        {"x": pipeX, "y": gapY - pipeHeight},  # upper pipe
        {"x": pipeX, "y": gapY + PIPEGAPSIZE},  # lower pipe
    ]


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player["index"]
    player["w"] = PLAYER[IM_WIDTH]
    player["h"] = PLAYER[IM_HEIGTH]

    # if player crashes into ground
    if (player["y"] + player["h"] >= BASEY - 1) or (player["y"] + player["h"] <= 0):
        return [True, True]
    else:

        playerRect = pygame.Rect(player["x"], player["y"], player["w"], player["h"])
        pipeW = PIPE[IM_WIDTH]
        pipeH = PIPE[IM_HEIGTH]

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe["x"], uPipe["y"], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe["x"], lPipe["y"], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS["player"][pi]
            uHitmask = HITMASKS["pipe"][0]
            lHitmask = HITMASKS["pipe"][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


if __name__ == "__main__":
    main()
