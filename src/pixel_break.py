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

# game constants

BLACK = (0, 0, 0)
SIZE = WIDTH, HEIGHT = 512, 640

#######


# CURRENT AS OF 4/10/19 5:15
# FIX UPDATE IN BALL, JUST STARTED


#######

def load_png(name):
    """ Load image and return image object
    copied from given code"""
    fullname = os.path.join('assets', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
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
                if int(split_line[j]) != 0:
                    # arg1: passes int value of element for color
                    # arg2: passes location in matrix as coordinate multiplied by brick dimensions + 2
                    group.add(Brick(int(split_line[j]), (j * 16, (i * 16) + 36)))
                    print(split_line[j])


class Ball(pygame.sprite.Sprite):
    def __init__(self, vector):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png("ball.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = ((SIZE[0] / 2) - 8, -(48 - SIZE[1]))
        # the rect which the ball must stay within at all times
        self.area = screen.get_rect()
        self.vector = vector

    def update(self):
        # returns a rect for this cycle's ball position
        newpos = calcnewpos(self.rect, self.vector)
        self.rect = newpos
        (angle, z) = self.vector

        if not self.area.contains(newpos):
            # true if top left point of ball rect is not in the screen area
            tl = not self.area.collidepoint(newpos.topleft)

            # true if top right point of ball rect is not in the screen area
            tr = not self.area.collidepoint(newpos.topright)

            # true if bottom left point of ball rect is not in the screen area
            bl = not self.area.collidepoint(newpos.bottomleft)

            # true if bottom right point of ball rect is not in the screen area
            br = not self.area.collidepoint(newpos.bottomright)


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
    def __init__(self, hp, coordinates):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png(str(hp) + ".png")
        self.rect = self.image.get_rect()
        self.rect.topleft = coordinates
        self.hp = hp

    def hit(self):
        if self.hp > 0:
            self.hp -= 1
        elif self.hp < 0:
            self.hp += 1
        else:
            print("You should not get here! The hit function should not be called on bricks with 0 HP.")


def main():
    # initialize screen
    # screen is global so that the ball can reference its rect to determine acceptable area of movement
    global screen
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
    ball = Ball((0.7, 10))
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
                        background.blit(ball.image, bar.rect)
                        brick_group.draw(background)
                        screen.blit(background, (0, 0))
                        should_update_entire_screen = True


        if not should_update_entire_screen:
            pygame.display.update(dirty_rects)
        else:
            pygame.display.flip()




if __name__ == '__main__':
    main()
