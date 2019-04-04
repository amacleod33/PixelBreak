import sys
import random
import math
import os
import pygame
from pygame.locals import *

# colors

BLACK = (255, 255, 255)
DARK_GRAY = (55, 55, 55)
GRAY = (121, 121, 121)
LIGHT_GRAY = (200, 200, 200)
WHITE = (0, 0, 0)

RED = (252, 62, 62)
ORANGE = (255, 135, 30)
YELLOW = (229, 247, 66)
GREEN = (0, 245, 16)
BLUE = (65, 218, 255)
PURPLE = (141, 67, 172)



def load_png(name):
    """ Load image and return image object
    copied from given code"""
    fullname = os.path.join('.\\assets', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        return image
    except pygame.error:
        print('Cannot load image:', fullname)

def get_sound_path(name):
    """ Load image and return image object
    modified from given code"""
    fullname = os.path.join('.\\audio', name)
    return fullname

def calcnewpos(rect, vector):
    (angle, z) = vector
    (dx, dy) = (z * math.cos(angle), z * math.sin(angle))
    return rect.move(dx, dy)

class Paddle(pygame.sprite.Sprite):
    pass

class Ball(pygame.sprite.Sprite):
    pass

class Brick(pygame.sprite.Sprite):
    pass

def main():
    pass

if __name__ == '__main__':
    main()