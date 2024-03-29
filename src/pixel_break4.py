# Written by Nick Napora and Alex MacLeod for CPSC 250L Spring 2019 at Christopher Newport University
# Assignment written by Matthew Bartgis
# Adapted from Tom's Pong
# Rabbototo character created by Nick Napora

import math
import os
import pygame
from pygame.locals import *
import struct

SIZE = WIDTH, HEIGHT = 512, 640
LIVES = 5

PADDLE_SPEED = 16

STARTING_SPEED = 9
STARTING_ANGLE = (3 * math.pi) / 4

BALL_STARTING_X = 300
BALL_STARTING_Y = 556


def load_png(name):
    """ Load image and return image object"""
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


def get_sound_path(name):
    fullname = os.path.join('audio', name)
    return fullname


def calcnewpos(rect, vector):
    (angle, z) = vector
    (dx, dy) = (z * math.cos(angle), z * math.sin(angle))
    return rect.move(dx, dy)


def read_board(filename):
    """Read comma separated file and add bricks to a passed group accordingly"""
    with open(os.path.join('boards', filename)) as file:
        output_list = []
        lines = file.readlines()
        for i in range(len(lines)):
            # list of strings
            split_line = lines[i].split(",")
            for j in range(len(split_line)):
                output_list.append(int(split_line[j]))
                if int(split_line[j]) != 0:
                    # arg1: passes int value of element for color
                    # arg2: passes location in matrix as coordinate multiplied by brick dimensions + 2
                    bricks.add(Brick(int(split_line[j]), (j * 16, (i * 16) + 36)))
        return output_list


def bricks_to_numbers(group):
    list = [0] * 1024
    for brick in group:
        position = (brick.rect.topleft[0] // 16) + ((brick.rect.topleft[1] - 36) * 2)
        list[position] = int(brick.hp)
    return list


class Brick(pygame.sprite.Sprite):
    def __init__(self, hp, coordinates):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png(str(hp) + ".png")
        self.rect = self.image.get_rect()

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = coordinates
        self.hp = hp


class Paddle(pygame.sprite.Sprite):
    """The paddle with which one hits the ball, adapted from Tom's Pong
    Returns: bat object
    Functions: reinit, update, moveleft, moveright
    Attributes: area, speed, state"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png('quadbar.png')
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = PADDLE_SPEED
        self.state = "still"
        self.reinit()

    def reinit(self):
        self.state = "still"
        self.movepos = [0, 0]
        self.rect.midbottom = self.area.midbottom

    def update(self):
        newpos = self.rect.move(self.movepos)
        if self.area.contains(newpos):
            self.rect = newpos
        pygame.event.pump()

    def moveleft(self):
        self.movepos[0] = self.movepos[0] - self.speed
        self.state = "moveleft"

    def moveright(self):
        self.movepos[0] = self.movepos[0] + self.speed
        self.state = "moveright"

    def still(self):
        self.movepos = [0, 0]
        self.state = "still"


class Ball(pygame.sprite.Sprite):
    """A ball that will move across the screen, adapted from Tom's Pong
    Returns: ball object
    Functions: update
    Attributes: area, vector"""

    def __init__(self, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png('ball.png')
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.rect.center = (BALL_STARTING_X, BALL_STARTING_Y)
        self.area = screen.get_rect()
        self.speed = STARTING_SPEED
        self.vector = (angle, self.speed)
        self.hit = 0
        self.score = 0
        self.lives = LIVES
        self.state = 2

        self.previous_brick = None
        self.just_hit_paddle = False


    def update(self):


        newpos = calcnewpos(self.rect, self.vector)

        self.rect = newpos
        (angle, z) = self.vector

        if not self.area.contains(newpos):

            # hits bottom
            if self.rect.bottomleft[1] > HEIGHT:

                self.just_hit_paddle = False

                self.lives -= 1
                if self.lives < 1:
                    self.state = 2

                else:
                    self.rect.x = BALL_STARTING_X
                    self.rect.y = BALL_STARTING_Y
                    angle = STARTING_ANGLE
                    z = STARTING_SPEED
                    player.reinit()


            # hits top
            elif self.rect.topleft[1] < 0:

                self.just_hit_paddle = False

                if angle < ((3 * math.pi) / 2):
                    angle = math.pi - (angle - math.pi)
                else:
                    angle = (2 * math.pi) - angle



            # hits right
            elif self.rect.midright[0] > WIDTH:

                self.just_hit_paddle = False

                if not ((0 <= angle <= math.pi / 2) or (((3 * math.pi) / 2) <= angle < (2 * math.pi))):
                    print("out of range!")

                elif angle < (math.pi / 2):
                    angle = math.pi - angle

                else:
                    angle = (2 * math.pi) - (angle - math.pi)


            # hits left
            elif self.rect.midleft[0] < 0:

                self.just_hit_paddle = False

                if not ((math.pi / 2) <= angle <= (3 * math.pi) / 2):
                    print("out of range!")

                elif angle < math.pi:
                    angle = math.pi - angle

                else:
                    angle = (2 * math.pi) - (angle - math.pi)

            # corner case
            else:
                if angle < math.pi:
                    angle += math.pi
                else:
                    angle -= math.pi

        else:
            # this is for the brick calculations
            targetbrick = pygame.sprite.spritecollideany(self, bricksprite)

            if (player.rect.colliderect(newpos)) and (not self.just_hit_paddle):
                self.just_hit_paddle = True
                audio_ball_hit.play()
                angle = (2 * math.pi) - angle

                if player.state == "moveleft":
                    # ball going right, steeper
                    if angle < math.pi:
                        angle = angle - ((angle - ((3 * math.pi) / 2)) / 2)
                    # ball going left, shallower
                    else:
                        angle = angle + ((math.pi - angle) / 2)

                elif player.state == "moveright":
                    # ball going right, shallower
                    if angle < math.pi:
                        angle = angle + (((2 * math.pi) - angle) / 2)
                    # ball going left, steeper
                    else:
                        angle = angle - ((angle - ((3 * math.pi) / 2)) / 2)

            elif targetbrick is not None and (targetbrick != self.previous_brick):
                audio_brick_hit.play()
                self.score += 10

                self.previous_brick = targetbrick
                self.just_hit_paddle = False

                tl = targetbrick.rect.collidepoint(newpos.topleft)
                tr = targetbrick.rect.collidepoint(newpos.topright)
                bl = targetbrick.rect.collidepoint(newpos.bottomleft)
                br = targetbrick.rect.collidepoint(newpos.bottomright)

                # going southeast
                if 0 < angle < (math.pi / 2):
                    # hits left side
                    if tr:
                        angle = math.pi - angle

                    # hits top
                    elif br or bl:
                        angle = (2 * math.pi) - angle

                    # ruh roh
                    else:
                        print("ruh roh")

                # going southwest
                elif angle < math.pi:
                    # hits right side
                    if tl:
                        angle = math.pi - angle

                    # hits top
                    elif bl or br:
                        angle = (2 * math.pi) - angle

                    # ruh roh
                    else:
                        print("ruh roh")

                # going northwest
                elif angle < ((3 * math.pi) / 2):
                    # hits right side
                    if bl:
                        angle = (2 * math.pi) - (angle - math.pi)

                    # hits bottom
                    elif tl or tr:
                        angle = math.pi - (angle - math.pi)

                    # ruh roh
                    else:
                        print("ruh roh")

                # going northeast
                elif angle < (2 * math.pi):
                    # hits left side
                    if br:
                        angle = (2 * math.pi) - (angle - math.pi)

                    # hits bottom
                    elif tr or tl:
                        angle = (2 * math.pi) - angle

                    # ruh roh
                    else:
                        print("ruh roh")

                # ruh roh
                else:
                    print("ruh roh raggy")

                if targetbrick.hp > 0:
                    targetbrick.hp -= 1
                elif targetbrick.hp < 0:
                    targetbrick.hp += 1
                else:
                    print("You should not get here! The hit function should not be called on bricks with 0 HP.")

                if targetbrick.hp == 0:
                    targetbrick.image.fill((0, 0, 0))
                    bricksprite.remove(targetbrick)

                else:
                    targetbrick.image = load_png(str(targetbrick.hp) + ".png")

            else:
                self.previous_brick = None

        self.vector = (angle, z)



def main():

    # Initialize screen
    global screen
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('PIXEL BREAK')

    # Fill background
    global background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    # Initialize players
    global player
    player = Paddle()

    global level
    level = 1

    save = False
    load = False

    # Initialize ball

    ball = Ball(STARTING_ANGLE)


    # Initialize bricks
    global bricks
    bricks = pygame.sprite.Group()
    read_board("board1.txt")

    global font
    font = pygame.font.Font(os.path.join('assets', "font.TTF"), 36)

    playersprites = pygame.sprite.RenderPlain((player))
    global bricksprite
    bricksprite = pygame.sprite.RenderPlain(bricks)
    ballsprite = pygame.sprite.RenderPlain(ball)


    # initialize selector
    select = pygame.sprite.Sprite()
    select.image = load_png("select.png")
    select.rect = select.image.get_rect()
    select_coordinates = (0, 36)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialize clock
    clock = pygame.time.Clock()

    # makes mouse invisible
    pygame.mouse.set_visible(False)

    global audio_ball_hit
    audio_ball_hit = pygame.mixer.Sound(get_sound_path("sfx_sounds_Blip4.wav"))
    global audio_brick_hit
    audio_brick_hit = pygame.mixer.Sound(get_sound_path("sfx_damage_hit1.wav"))
    global audio_pause
    audio_pause = pygame.mixer.Sound(get_sound_path("sfx_sounds_Blip2.wav"))
    global audio_next_level
    audio_next_level = pygame.mixer.Sound(get_sound_path("sfx_damage_hit10.wav"))

    # create mode parameters
    editing = False
    brick_active = False
    create_bricks = []
    user_file = ""

    # Event loop

    while True:
        # Make sure game doesn't run at more than 60 frames per second
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:

                # create mode
                if ball.state == 3 and editing == False:

                    bricks.empty()
                    bricksprite.empty()


                    if event.key == pygame.K_1 or event.key == pygame.K_2 or event.key == pygame.K_3 or event.key == pygame.K_4 or event.key == pygame.K_5:
                        editing = True
                        if event.key == pygame.K_1:
                            # sets bricks group to user file
                            create_bricks = read_board("user1.txt")
                            user_file = "user1.txt"
                            local_draw = True

                        elif event.key == pygame.K_2:
                            # sets bricks group to user file
                            create_bricks = read_board("user2.txt")
                            user_file = "user2.txt"
                            local_draw = True

                        elif event.key == pygame.K_3:
                            # sets bricks group to user file
                            create_bricks = read_board("user3.txt")
                            user_file = "user3.txt"
                            local_draw = True

                        elif event.key == pygame.K_4:
                            # sets bricks group to user file
                            create_bricks = read_board("user4.txt")
                            user_file = "user4.txt"
                            local_draw = True

                        elif event.key == pygame.K_5:
                            # sets bricks group to user file
                            create_bricks = read_board("user5.txt")
                            user_file = "user5.txt"
                            local_draw = True

                        background.fill((0, 0, 0))
                        bricksprite = pygame.sprite.RenderPlain(bricks)
                        bricksprite.draw(background)
                        background.blit(select.image, select_coordinates)
                        screen.blit(background, (0, 0))

                    elif event.key == pygame.K_F1 or event.key == pygame.K_F2 or event.key == pygame.K_F3 or event.key == pygame.K_F4 or event.key == pygame.K_F5:

                        if event.key == pygame.K_F1:
                            read_board("user1.txt")

                        elif event.key == pygame.K_F2:
                            read_board("user2.txt")

                        elif event.key == pygame.K_F3:
                            read_board("user3.txt")

                        elif event.key == pygame.K_F4:
                            read_board("user4.txt")

                        elif event.key == pygame.K_F5:
                            read_board("user5.txt")

                        background.fill((0, 0, 0))
                        screen.blit(background, (0, 0))
                        bricksprite = pygame.sprite.RenderPlain(bricks)
                        level = 0
                        ball.state = 0

                    elif event.key == pygame.K_RETURN:
                        background.fill((0, 0, 0))
                        screen.blit(background, (0, 0))
                        ball.state = 2


                elif editing and not brick_active:
                    if event.key == pygame.K_UP and select_coordinates[1] >= 52:
                        previous = pygame.Rect(select_coordinates[0], select_coordinates[1], 16, 16)
                        background.fill((0, 0, 0), previous)
                        bricksprite.draw(background)
                        select_coordinates = (select_coordinates[0], select_coordinates[1] - 16)
                        background.blit(select.image, select_coordinates)
                        screen.blit(background, (0, 0))

                    elif event.key == pygame.K_DOWN and select_coordinates[1] <= 531:
                        previous = pygame.Rect(select_coordinates[0], select_coordinates[1], 16, 16)
                        background.fill((0, 0, 0), previous)
                        bricksprite.draw(background)
                        select_coordinates = (select_coordinates[0], select_coordinates[1] + 16)
                        background.blit(select.image, select_coordinates)
                        screen.blit(background, (0, 0))

                    elif event.key == pygame.K_LEFT and select_coordinates[0] >= 16:
                        previous = pygame.Rect(select_coordinates[0], select_coordinates[1], 16, 16)
                        background.fill((0, 0, 0), previous)
                        bricksprite.draw(background)
                        select_coordinates = (select_coordinates[0] - 16, select_coordinates[1])
                        background.blit(select.image, select_coordinates)
                        screen.blit(background, (0, 0))

                    elif event.key == pygame.K_RIGHT and select_coordinates[0] <= 495:
                        previous = pygame.Rect(select_coordinates[0], select_coordinates[1], 16, 16)
                        background.fill((0, 0, 0), previous)
                        bricksprite.draw(background)
                        select_coordinates = (select_coordinates[0] + 16, select_coordinates[1])
                        background.blit(select.image, select_coordinates)
                        screen.blit(background, (0, 0))

                    elif event.key == pygame.K_SPACE:
                        brick_active = True
                        previous = pygame.Rect(select_coordinates[0], select_coordinates[1], 16, 16)
                        background.fill((0, 0, 0), previous)
                        bricksprite.draw(background)
                        screen.blit(background, (0, 0))

                    elif event.key == pygame.K_s:
                        string = ""
                        for i in range(1024):
                            if i == 0:
                                string += str(create_bricks[i]) + ","
                            elif ((i + 1) % 32) == 0:
                                string += str(create_bricks[i]) + "\n"
                            else:
                                string += str(create_bricks[i]) + ","
                        with open(os.path.join('boards', user_file), "w") as file:
                            file.write(string)

                    elif event.key == pygame.K_RETURN:
                        editing = False
                        background.fill((0, 0, 0))
                        screen.blit(background, (0, 0))
                        ball.state = 2

                elif editing and brick_active:
                    if event.key == pygame.K_SPACE:
                        brick_active = False
                        background.blit(select.image, select_coordinates)
                        screen.blit(background, (0, 0))

                    elif event.key == pygame.K_UP:
                        position = (select_coordinates[0] // 16) + ((select_coordinates[1] - 36) * 2)
                        if create_bricks[position] < 9:
                            create_bricks[position] += 1
                        else:
                            create_bricks[position] = -5
                        bricks.empty()
                        bricksprite.empty()

                        for j in range(1024):
                            if create_bricks[j] != 0:
                                # arg1: passes int value of element for color
                                # arg2: passes location in matrix as coordinate multiplied by brick dimensions

                                bricksprite.add(
                                    Brick(create_bricks[j], (16 * (j - ((j // 32) * 32)), ((j // 32) * 16) + 36)))

                        background.fill((0, 0, 0))
                        bricksprite.draw(background)
                        screen.blit(background, (0, 0))

                    elif event.key == pygame.K_DOWN:
                        position = (select_coordinates[0] // 16) + ((select_coordinates[1] - 36) * 2)
                        if create_bricks[position] > -5:
                            create_bricks[position] -= 1
                        else:
                            create_bricks[position] = 9
                        bricks.empty()
                        bricksprite.empty()

                        for j in range(1024):
                            if create_bricks[j] != 0:
                                # arg1: passes int value of element for color
                                # arg2: passes location in matrix as coordinate multiplied by brick dimensions

                                bricksprite.add(
                                    Brick(create_bricks[j], (16 * (j - ((j // 32) * 32)), ((j // 32) * 16) + 36)))

                        background.fill((0, 0, 0))
                        bricksprite.draw(background)
                        screen.blit(background, (0, 0))

                elif event.key == pygame.K_c and ball.state == 2:
                    background.blit(load_png("create.png"), (0, 0))
                    screen.blit(background, (0, 0))

                    ball.state = 3

                elif event.key == pygame.K_l:
                    audio_pause.play()
                    load_screen = load_png('load.png')
                    background.fill((0, 0, 0))
                    background.blit(load_screen, (0, 0))
                    screen.blit(background, (0, 0))
                    audio_pause.play()

                    ball.state = 1
                    load = True

                # load here
                # checks if 1, 2, or 3 is pressed while loading OR on title screen
                elif (event.key == pygame.K_1 or event.key == pygame.K_2 or event.key == pygame.K_3) and (load == True or ball.state == 2):
                    if event.key == pygame.K_1:
                        filename = 'save_state1.dat'
                    elif event.key == pygame.K_2:
                        filename = 'save_state2.dat'
                    else:
                        filename = 'save_state3.dat'
                    with open(filename, 'rb') as file:
                        ba = bytearray(file.read())

                        num_array = []

                        data = struct.unpack('1033i', ba)
                        num_array.extend(list(data))

                        player.rect.topleft = (num_array[-2], num_array[-1])
                        level = num_array[-3]
                        ball.vector = ((float(num_array[-5] / 100)), num_array[-4])

                        ball.rect.topleft = (num_array[-7], num_array[-6])

                        ball.lives = num_array[-8]
                        ball.score = num_array[-9]

                        for i in range(1, 10):
                            num_array.pop(-1)

                        bricks.empty()
                        bricksprite.empty()

                        for j in range(len(num_array)):
                            if int(num_array[j]) != 0:
                                # arg1: passes int value of element for color
                                # arg2: passes location in matrix as coordinate multiplied by brick dimensions
                                bricksprite.add(
                                    Brick(num_array[j], (16 * (j - ((j // 32) * 32)), ((j // 32) * 16) + 36)))

                        background.fill((0, 0, 0), background.get_rect())
                        screen.blit(background, (0, 0))
                        ball.state = 0
                        load = False

                elif event.key == pygame.K_s:
                    audio_pause.play()
                    pause_screen = load_png('save.png')
                    background.fill((0, 0, 0))
                    background.blit(pause_screen, (0, 0))
                    screen.blit(background, (0,0))
                    ball.state = 1
                    save = True

                elif (event.key == pygame.K_1 or event.key == pygame.K_2 or event.key == pygame.K_3) and save == True:
                    if event.key == pygame.K_1:
                        filename = 'save_state1.dat'
                    elif event.key == pygame.K_2:
                        filename = 'save_state2.dat'
                    else:
                        filename = 'save_state3.dat'
                # save here
                    with open(os.path.join(filename), 'wb') as binary_file:
                        ba = bytearray()
                        parameter_list = bricks_to_numbers(bricksprite)
                        parameter_list.extend((ball.score, ball.lives, ball.rect.topleft[0], ball.rect.topleft[1],
                                               int(ball.vector[0] * 100), ball.vector[1], level, player.rect.topleft[0],
                                               player.rect.topleft[1]))
                        ba.extend(
                            struct.pack('1033i', *parameter_list))
                        binary_file.write(ba)
                        if event.key == pygame.K_SPACE:
                            background.fill((0, 0, 0))
                            screen.blit(background, (0, 0))
                            screen.blit(background, player.rect, player.rect)
                            bricks.draw(background)
                            screen.blit(background, ball.rect, ball.rect)
                            audio_pause.play()
                            if ball.state == 0:
                                ball.state = 1
                            elif ball.state == 1:
                                ball.state = 0

                # pause
                elif event.key == pygame.K_SPACE:

                    background.fill((0, 0, 0))
                    screen.blit(background, (0, 0))
                    screen.blit(background, player.rect, player.rect)
                    bricks.draw(background)
                    screen.blit(background, ball.rect, ball.rect)
                    audio_pause.play()
                    if ball.state == 0:
                        ball.state = 1
                    elif ball.state == 1:
                        ball.state = 0

                    score_surface = font.render(str(ball.score), False, (255, 255, 255))
                    score_pos = score_surface.get_rect(topright=background.get_rect().topright)
                    background.blit(score_surface, score_pos)

                    lives_surface = font.render(str(ball.lives), False, (255, 255, 255))
                    lives_pos = lives_surface.get_rect(topleft=background.get_rect().topleft)
                    background.blit(lives_surface, lives_pos)

                    screen.blit(background, (0, 0))

                    bricksprite.draw(screen)
                    playersprites.draw(screen)
                    ballsprite.draw(screen)

                elif event.key == pygame.K_RIGHT:
                    player.moveright()

                elif event.key == pygame.K_LEFT:
                    player.moveleft()

                elif event.key == pygame.K_RETURN:
                    if ball.state == 2:
                        ball.lives = LIVES
                        ball.score = 0

                        background.fill((0, 0, 0))

                        screen.blit(background, (0, 0))
                        screen.blit(background, player.rect, player.rect)
                        bricks.draw(background)
                        screen.blit(background, ball.rect, ball.rect)

                        score_surface = font.render(str(ball.score), False, (255, 255, 255))
                        score_pos = score_surface.get_rect(topright=background.get_rect().topright)
                        background.blit(score_surface, score_pos)
                        screen.blit(background, (0, 0))

                        read_board("board1.txt")
                        bricksprite = pygame.sprite.RenderPlain(bricks)

                        ball.state = 0

                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return

                # cheats

                elif event.key == pygame.K_r:
                    ball.image = load_png("rabbototo.png")

                elif event.key == pygame.K_e:
                    ball.image = load_png("ball.png")

                elif event.key == pygame.K_9:
                    ball.lives += 9

                elif event.key == pygame.K_m:
                    if ball.vector[1] > 4:
                        ball.vector = (ball.vector[0], 4)
                    else:
                        ball.vector = (ball.vector[0], STARTING_SPEED)

                elif event.key == pygame.K_n:
                    if ball.vector[1] < 20:
                        ball.vector = (ball.vector[0], 20)
                    else:
                        ball.vector = (ball.vector[0], STARTING_SPEED)

            # what? did I write this? this is stupid
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    player.still()

        if ball.state == 2:

            if bricks:
                bricks.empty()
            game_over_surface = load_png('title.png')
            game_over_pos = game_over_surface.get_rect(centerx=background.get_width() / 2)

            ball.lives = LIVES
            ball.score = 0

            background.fill((0, 0, 0))
            background.blit(game_over_surface, game_over_pos)
            screen.blit(background, (0, 0))

            level = 1

        if ball.state < 1:

            # next level
            if (not bricksprite) and ball.just_hit_paddle:
                bricksprite.empty()
                level += 1
                read_board("board" + str(level) + ".txt")
                bricksprite = pygame.sprite.RenderPlain(bricks)

            screen.blit(background, player.rect, player.rect)
            bricks.draw(background)
            screen.blit(background, ball.rect, ball.rect)

            background.fill((0, 0, 0),
                            rect=(background.get_rect().left, background.get_rect().top, background.get_width(), 36))
            score_surface = font.render(str(ball.score), False, (255, 255, 255))
            score_pos = score_surface.get_rect(topright=background.get_rect().topright)
            # background.fill((0, 0, 0), rect=score_pos)
            background.blit(score_surface, score_pos)

            lives_surface = font.render(str(ball.lives), False, (255, 255, 255))
            lives_pos = lives_surface.get_rect(topleft=background.get_rect().topleft)
            # background.fill((0, 0, 0), rect=score_pos)
            background.blit(lives_surface, lives_pos)

            screen.blit(background, (0, 0))

            playersprites.update()
            ballsprite.update()

            bricksprite.draw(screen)
            playersprites.draw(screen)
            ballsprite.draw(screen)

        pygame.display.flip()


if __name__ == '__main__':
    main()
