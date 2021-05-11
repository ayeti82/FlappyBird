# create a logo for mystic corporations
# try to add buttons for start and statistics, changing birds
# speed increases with score
import pygame
from pygame.locals import *
import random
import os
import sys

# for p in pygame.font.get_fonts():
#     print(p)

# Frame
fps = 60

# Screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width = screen.get_width()
screen_ht = screen.get_height()

game_base = pygame.image.load("tmp_fbird/sprites/base.png").convert_alpha()
game_base = pygame.transform.scale(game_base, (screen_width, int(screen_ht * 0.2)))
ground_y = screen_ht * 0.9

player = pygame.image.load('tmp_fbird/sprites/bird.png').convert_alpha()
player = pygame.transform.scale(player, (80, 80))

background = pygame.image.load('tmp_fbird/sprites/background.png').convert_alpha()
background = pygame.transform.scale(background, (screen_width, screen_ht))

pipe = 'tmp_fbird/sprites/pipe.png'

welcome = pygame.image.load('tmp_fbird/sprites/welcome.png').convert_alpha()
welcome = pygame.transform.scale(welcome, (screen_width, screen_ht))
startButton = pygame.image.load('tmp_fbird/sprites/start_button.png').convert_alpha()

gameOver = pygame.image.load('tmp_fbird/sprites/game_over.png').convert_alpha()
gameOver = pygame.transform.scale(gameOver, (500, 500))

# Sprites and sounds
game_sprites = {}
game_sounds = {}

if not os.path.exists("HighScore.txt"):
    with open("HighScore.txt", "w") as f:
        f.write("0")
    highScore = f.read()
else:
    with open("HighScore.txt", "r") as f:
        highScore = f.read()


def text_screen(text, font, color, x, y):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, (x, y))


def printHighScore():
    text_screen(f"High Score: {highScore}", pygame.font.SysFont("goudyoldstyle", 100), (0, 0, 0), screen_width / 3.5,
                screen_ht / 1.6)


def eventSpaceFunc(playerx, playery, basex):
    screen.blit(game_sprites['background'], (0, 0))
    screen.blit(game_sprites['player'], (playerx, playery))
    screen.blit(game_sprites['base'], (basex, ground_y))
    pygame.display.update()


def welcomeScreen(Crashed, cnt, score):
    playerx = int(screen_width / 5)
    playery = int((screen_ht - game_sprites['player'].get_height()) / 2)
    basex = 0
    if Crashed or cnt == 0:
        if Crashed:
            global highScore
            screen.blit(gameOver, (((screen_width - gameOver.get_width()) / 2), (screen_ht / 13)))
            if int(highScore) < score:
                with open("HighScore.txt", "w") as fd:
                    fd.write(str(score))
        else:
            screen.blit(game_sprites['message'], (0, 0))
            screen.blit(startButton, ((screen_width - startButton.get_width()) / 2, screen_ht / 2.5))
            printHighScore()
            text_screen("Mystic Co-operation", pygame.font.SysFont("goudyoldstyle", 40), (0, 0, 0), screen_width / 1.4,
                        screen_ht / 1.1)
        pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                eventSpaceFunc(playerx, playery, basex)
                return
            elif event.type == MOUSEBUTTONDOWN and event.button == BUTTON_LEFT:
                pos = pygame.mouse.get_pos()
                if int(screen_width / 2) < pos[0] < int((screen_width / 2) + startButton.get_width()) \
                        and int(screen_ht / 2.5) < pos[1] < int((screen_ht / 2.5) + startButton.get_height()):
                    eventSpaceFunc(playerx, playery, basex)
                    return
            FPSCLOCK.tick(fps)


def mainGame(cnt):
    score = 0
    playerx = int(screen_width / 5)
    playery = int(screen_ht / 2)
    basex = 0

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    upperPipes = [{'x': screen_width + 200, 'y': newPipe1[0]['y']},
                  {'x': screen_width + 200 + (screen_width / 2), 'y': newPipe2[0]['y']}, ]
    lowerPipes = [{'x': screen_width + 200, 'y': newPipe1[1]['y']},
                  {'x': screen_width + 200 + (screen_width / 2), 'y': newPipe2[1]['y']}, ]

    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    # playerMinVelY = -8
    playerAccY = 1
    playerFlapAccv = -8

    playerFlapped = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    game_sounds['wing'].play()

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            welcomeScreen(True, cnt, score)
            cnt += 1
            return

        playerMidPos = playerx + game_sprites['player'].get_width() / 2
        for tmpPipe in upperPipes:
            pipeMidPos = tmpPipe['x'] + game_sprites['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score = score + 1
                game_sounds['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = game_sprites['player'].get_height()
        playery = playery + min(playerVelY, ground_y - playery - playerHeight)

        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        if upperPipes[0]['x'] < -game_sprites['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        screen.blit(game_sprites['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            screen.blit(game_sprites['pipe'][0], (upperPipe['x'], upperPipe['y']))
            screen.blit(game_sprites['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        screen.blit(game_sprites['base'], (basex, ground_y))
        screen.blit(game_sprites['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width = width + game_sprites['numbers'][digit].get_width()
        offset = (screen_width - width) / 2

        for digit in myDigits:
            screen.blit(game_sprites['numbers'][digit], (offset, screen_ht * 0.1))
            offset = offset + game_sprites['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(fps)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > ground_y - game_sprites['player'].get_height() - 1 or playery < 0:
        game_sounds['hit'].play()
        return True

    for tmpPipe in upperPipes:
        pipeHeight = game_sprites['pipe'][0].get_height()
        if playery + int(game_sprites['player'].get_height() / 2) < pipeHeight + tmpPipe['y'] \
                and 0 < tmpPipe['x'] < playerx < game_sprites['pipe'][0].get_width() + tmpPipe['x']:
            game_sounds['hit'].play()
            return True

    for tmpPipe in lowerPipes:
        if playery + int(game_sprites['player'].get_height() / 2) > tmpPipe['y'] and 0 < tmpPipe['x'] < playerx < \
                game_sprites['pipe'][0].get_width() + tmpPipe['x']:
            game_sounds['hit'].play()
            return True

    return False


def getRandomPipe():
    pipeHeight = game_sprites['pipe'][0].get_height()
    offset = screen_ht / 3
    y1 = random.randrange(int(pipeHeight / 8), int(pipeHeight / 2))
    pipeX = screen_width + 10
    y2 = pipeHeight - y1 + offset
    tmpPipe = [{'x': pipeX, 'y': -y1}, {'x': pipeX, 'y': y2}]
    return tmpPipe


if __name__ == "__main__":
    c = 0
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird')
    game_sprites['numbers'] = (
        pygame.image.load('tmp_fbird/sprites/0.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/1.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/2.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/3.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/4.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/5.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/6.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/7.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/8.png').convert_alpha(),
        pygame.image.load('tmp_fbird/sprites/9.png').convert_alpha(),
    )

    game_sprites['message'] = welcome
    game_sprites['base'] = game_base
    game_sprites['pipe'] = (pygame.transform.rotate(pygame.image.load(pipe).convert_alpha(), 180),
                            pygame.image.load(pipe).convert_alpha()
                            )

    # Game sounds
    game_sounds['die'] = pygame.mixer.Sound('tmp_fbird/audio/die.wav')
    game_sounds['hit'] = pygame.mixer.Sound('tmp_fbird/audio/hit.wav')
    game_sounds['point'] = pygame.mixer.Sound('tmp_fbird/audio/point.wav')
    game_sounds['swoosh'] = pygame.mixer.Sound('tmp_fbird/audio/swoosh.wav')
    game_sounds['wing'] = pygame.mixer.Sound('tmp_fbird/audio/wing.wav')

    game_sprites['background'] = background
    game_sprites['player'] = player

    while True:
        welcomeScreen(False, c, 0)
        c = c + 1
        mainGame(c)
