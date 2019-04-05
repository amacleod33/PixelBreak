import sys
import random
import math
import os
import pygame
from pygame.locals import *

# initializes pygame
pygame.init()

# name

NAME = "PIXEL BREAK"

# colors

RED = (252, 62, 62)
ORANGE = (255, 135, 30)
YELLOW = (229, 247, 66)
GREEN = (0, 245, 16)
BLUE = (65, 218, 255)
PURPLE = (141, 67, 172)

WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
GRAY = (121, 121, 121)
DARK_GRAY = (55, 55, 55)
BLACK = (0, 0, 0)

COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, BLACK, DARK_GRAY, GRAY, LIGHT_GRAY, WHITE]


# game constants

SIZE = WIDTH, HEIGHT = 544, 580


def load_png(name):
    """ Load image and return image object
    copied from given code"""
    fullname = os.path.join('assets', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            # logic adapted from
            # https://stackoverflow.com/questions/12879225/pygame-applying-transparency-to-an-image-with-alpha
            surface = pygame.Surface(image.get_size(), depth=24)
            key = (0, 255, 0)
            surface.fill(key)
            surface.set_colorkey(key)
            surface.blit(image, (0, 0))
            surface.set_alpha(128)
            image = surface

        return image
    except pygame.error:
        print('Cannot load image:', fullname)


def get_asset(name):
    """ Load image and return image object
    modified from given code"""
    return os.path.join('assets', name)


def calcnewpos(rect, vector):
    (angle, z) = vector
    (dx, dy) = (z * math.cos(angle), z * math.sin(angle))
    return rect.move(dx, dy)


def read_board(filename, group):
    """Read plain text and add bricks to a passed group accordingly"""
    with open(os.path.join('boards', filename)) as file:
        lines = file.readlines()
        for i in range(len(lines)):
            # list of strings
            split_line = lines[i].split(",")
            for j in range(len(split_line)):
                if int(split_line[j]) > 0:
                    # arg1: passes int value of element for color
                    # arg2: passes location in matrix as coordinate multiplied by brick dimensions + 2
                    group.add(Brick(int(split_line[j])-1, (j * 33 + 1, i * 17 + 1)))


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    def update(self):
        pass
    pass


class Bar(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.surface = load_png("quadbar.png")
        self.rect = self.surface.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 20

        # 0 == stationary, 1 == left, 2 == right
        self.state = 0

        self.reinit()

    def reinit(self):
        self.state = "still"
        self.movepos = [0, 0]
        self.rect.midbottom = self.area.midbottom

    def update(self):
        pass


class Brick(pygame.sprite.Sprite):
    def __init__(self, color_code, coordinates):
        pygame.sprite.Sprite.__init__(self)
        self.color_code = color_code
        self.surface = pygame.Surface(load_png("brick.png").get_size())
        self.rect = pygame.Rect(coordinates[0], coordinates[1], self.surface.get_width(), self.surface.get_height())

    def brick_draw(self):
        self.surface.fill(COLORS[self.color_code])
        background.blit(self.surface, self.rect)
        self.surface = load_png("brick.png")
        background.blit(self.surface, self.rect)

    def update(self):
        pass


def main():

    # initialize screen
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption(NAME)

    # create background surface
    global background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(BLACK)

    # initialize title surface and do initial blit
    # load_png creates and returns a surface object using pygame.image.load()
    title = load_png("title.png")
    # gets rectangle for blitting title by get_rect(), specifying center to be x centered to background
    titlepos = title.get_rect(centerx=background.get_width() / 2)
    background.blit(title, titlepos)

    # blits background surface onto screen surface
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # initialize clock
    clock = pygame.time.Clock()

    # initialize font
    pygame.font.Font(get_asset("font.TTF"), 36)

    # sets mouse cursor not to be visible
    pygame.mouse.set_visible(0)

    # initialize game state
    # 0 == play, 1 == paused, 2 == game over, 3 == title
    state = 3

    # initialize level
    level = 1

    # initialize lives
    lives = 5

    # initialize ball and bar
    ball = Ball()
    bar = Bar()
    brick_group = pygame.sprite.Group()
    read_board("board1.txt", brick_group)


    # main loop
    while 1:

        # defines whether entire screen needs updated
        should_update_entire_screen = False

        # make sure game doesn't run at more than 60 frames per second
        clock.tick(60)

        # initialize dirty rect list
        global dirty_rects
        dirty_rects = []

        for event in pygame.event.get():
            # this enables closing the window
            if event.type == pygame.QUIT:
                return

            # if a key has been pressed or unpressed
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return

                # play state
                if state == 0:
                    ball.update()
                    # check for space bar

                # pause state
                elif state == 1:
                    pass

                # game over state
                elif state == 2:
                    # check for enter
                    # change state, reload
                    pass

                # title state
                elif state == 3:
                    if event.key == pygame.K_RETURN:
                        state = 0
                        # fills in the background surface object
                        background.fill(BLACK)
                        background.blit(bar.surface, bar.rect)
                        screen.blit(background, (0, 0))
                        for brick in brick_group:
                            brick.brick_draw()
                        should_update_entire_screen = True


        if not should_update_entire_screen:
            pygame.display.update(dirty_rects)
        else:
            pygame.display.flip()




if __name__ == '__main__':
    main()
