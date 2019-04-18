import sys
import random
import math
import os
import pygame
from pygame.locals import *
import struct

SIZE = WIDTH, HEIGHT = 512, 640
LIVES = 1


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
    """ Load image and return image object"""
    fullname = os.path.join('audio', name)
    return fullname

def calcnewpos(rect, vector):
    (angle, z) = vector
    (dx, dy) = (z * math.cos(angle), z * math.sin(angle))
    return rect.move(dx, dy)

def read_board(filename):
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
                    bricks.add(Brick(int(split_line[j]), (j * 16, (i * 16) + 36)))
                    print(split_line[j])

def bricks_to_numbers(group):
    list = [0] * 1024
    for brick in group:
        # position = 0
        # position += ((brick.rect.topleft[1] - 36) // 16) * 32
        # position += brick.rect.topleft[0] // 16
        position = (brick.rect.topleft[0]//16) + ((brick.rect.topleft[1] - 36) * 2)

        list[position] = int(brick.hp)

    return list


class Paddle(pygame.sprite.Sprite):
    """Movable tennis 'bat' with which one hits the ball
    Returns: bat object
    Functions: reinit, update, moveup, movedown
    Attributes: which, speed"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png('quadbar.png')
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 10
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
    """A ball that will move across the screen
    Returns: ball object
    Functions: update, calcnewpos
    Attributes: area, vector"""

    def __init__(self, vector):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png('ball.png')
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.rect.center = (320, 420)
        self.area = screen.get_rect()
        self.vector = vector
        self.hit = 0
        self.score = 0
        self.lives = LIVES
        self.state = 2

    def update(self):
        newpos = calcnewpos(self.rect, self.vector)
        self.rect = newpos
        (angle, z) = self.vector

        if not self.area.contains(newpos):
            tl = not self.area.collidepoint(newpos.topleft)
            tr = not self.area.collidepoint(newpos.topright)
            bl = not self.area.collidepoint(newpos.bottomleft)
            br = not self.area.collidepoint(newpos.bottomright)
            if bl and br:
                self.lives -= 1
                if self.lives < 1:
                    self.state = 2
                else:
                    self.rect.x = 320
                    self.rect.y = 420
                    self.vector = (.7, 0)
                    player.reinit()

            elif (tl and bl) or (tr and br):
                angle = math.pi - angle
            elif tr and tl:
                angle = -angle

        else:
            # Deflate the rectangles so you can't catch a ball behind the bat
            #player.rect.inflate(-3, -3)
            # Do ball and bat collide?
            # Note I put in an odd rule that sets self.hit to 1 when they collide, and unsets it in the next
            # iteration. this is to stop odd ball behaviour where it finds a collision *inside* the
            # bat, the ball reverses, and is still inside the bat, so bounces around inside.
            # This way, the ball can always escape and bounce away cleanly
            tl = player.rect.collidepoint(newpos.topleft)
            tr = player.rect.collidepoint(newpos.topright)
            bl = player.rect.collidepoint(newpos.bottomleft)
            br = player.rect.collidepoint(newpos.bottomright)

            if (br and bl):
                # if not self.hit:
                #     audio_ball_hit.play()
                #     angle = -angle
                # else:
                #     self.hit = not self.hit

                audio_ball_hit.play()
                angle = -angle

            elif tl or bl or tr or br:
                # if not self.hit:
                #     audio_ball_hit.play()
                #     angle = math.pi - angle
                # else:
                #     self.hit = not self.hit

                audio_ball_hit.play()
                angle = math.pi - angle

            targetbrick = pygame.sprite.spritecollideany(self, bricksprite)
            if targetbrick is not None:
                audio_brick_hit.play()
                self.score += 10

                tl = targetbrick.rect.collidepoint(newpos.topleft)
                tr = targetbrick.rect.collidepoint(newpos.topright)
                bl = targetbrick.rect.collidepoint(newpos.bottomleft)
                br = targetbrick.rect.collidepoint(newpos.bottomright)

                if (tr and tl) or (br and bl):
                    angle = -angle
                elif tl or bl or tr or br:
                    angle = math.pi - angle

                if targetbrick.hp > 0:
                    targetbrick.hp -= 1
                elif targetbrick.hp < 0:
                    targetbrick.hp += 1
                else:
                    print("You should not get here! The hit function should not be called on bricks with 0 HP.")

                if targetbrick.hp == 0:
                    targetbrick.image.fill((0,0,0))
                    bricksprite.remove(targetbrick)

                else:
                    targetbrick.image = load_png(str(targetbrick.hp) + ".png")

        self.vector = (angle, z)

class Brick(pygame.sprite.Sprite):
    def __init__(self, hp, coordinates):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png(str(hp) + ".png")
        self.rect = self.image.get_rect()

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = coordinates
        self.hp = hp


    #     self.state = 'Still'
    #     self.reinit()
    #
    # def reinit(self):
    #     self.state = "still"
    #     self.movepos = [0, 0]



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

    # Initialize ball

    speed = 6
    rand = 0.1 * random.randint(5, 8)
    ball = Ball((.7, speed))

    # Initialize bricks
    global bricks
    bricks = pygame.sprite.Group()
    read_board("board" + str(level) + ".txt")

    global font
    font = pygame.font.Font(os.path.join('assets', "font.TTF"), 36)

    playersprites = pygame.sprite.RenderPlain((player))
    global bricksprite
    bricksprite = pygame.sprite.RenderPlain(bricks)
    ballsprite = pygame.sprite.RenderPlain(ball)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialize clock
    clock = pygame.time.Clock()


    #Initialize sound
    #global audio
    #audio = pygame.mixer(frequency=22050, size=-16, channels=2, buffer=4096)
    global audio_ball_hit
    audio_ball_hit = pygame.mixer.Sound(get_sound_path("sfx_sounds_Blip4.wav"))
    global audio_brick_hit
    audio_brick_hit = pygame.mixer.Sound(get_sound_path("sfx_damage_hit1.wav"))
    global audio_pause
    audio_pause = pygame.mixer.Sound(get_sound_path("sfx_sounds_Blip2.wav"))
    global audio_next_level
    audio_next_level = pygame.mixer.Sound(get_sound_path("sfx_damage_hit10.wav"))

    # Event loop
    while True:
        # Make sure game doesn't run at more than 60 frames per second
        clock.tick(60)




        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    audio_pause.play()

                    ball.state = 1

                    # load here
                    with open('binary_data.dat', 'rb') as file:
                        ba = bytearray(file.read())
                        # chunk_size = struct.calcsize('>5120i')

                        num_array = []

                        # for i in range(len(ba) // chunk_size):
                        #     data = struct.unpack('1032i', ba)
                        #     num_array.extend(list(data))
                        #numpy_array = np.array(str(num_array))

                        data = struct.unpack('1033i', ba)
                        print("Data: " + str(data))
                        num_array.extend(list(data))
                        print("Num array: " + str(num_array))

                        player.rect.topleft = (num_array[-2], num_array[-1])
                        print(player.rect)
                        level = num_array[-3]
                        ball.vector = ((float(num_array[-5] / 100)), num_array[-4])

                        ball.rect.topleft = (num_array[-7], num_array[-6])

                        ball.lives = num_array[-8]
                        ball.score = num_array[-9]

                        for i in range(1, 10):
                            num_array.pop(-1)

                        print("Brick array??: " + str(num_array))

                        bricks.empty()
                        bricksprite.empty()
 
                        for j in range(len(num_array)):
                            if int(num_array[j]) != 0:
                                # arg1: passes int value of element for color
                                # arg2: passes location in matrix as coordinate multiplied by brick dimensions

                                # brick_column = j - ((j // 32) * 32)
                                # brick_row = j - (j // 32)
                                # bricksprite.add(Brick(num_array[j], (brick_column * 16, (brick_row * 16) + 36)))

                                bricksprite.add(Brick(num_array[j], (16 * (j - ((j // 32) * 32)), ((j // 32) * 16) + 36)))

                        background.fill((0, 0, 0))
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


                        print(num_array)

                if event.key == pygame.K_s:

                    audio_pause.play()

                    ball.state = 1

                    # save here
                    with open(os.path.join('binary_data.dat'), 'wb') as binary_file:
                        ba = bytearray()
                        parameter_list = bricks_to_numbers(bricksprite)
                        parameter_list.extend((ball.score, ball.lives, ball.rect.topleft[0], ball.rect.topleft[1], int(ball.vector[0] * 100), ball.vector[1], level, player.rect.topleft[0], player.rect.topleft[1]))
                        print(parameter_list)
                        ba.extend(
                            struct.pack('1033i', *parameter_list))
                        binary_file.write(ba)
                        if event.key == pygame.K_SPACE:
                            audio_pause.play()
                            if ball.state == 0:
                                ball.state = 1
                            elif ball.state == 1:
                                ball.state = 0

                if event.key == pygame.K_RIGHT:
                    player.moveright()
                if event.key == pygame.K_LEFT:
                    player.moveleft()
                if event.key == pygame.K_SPACE:
                    audio_pause.play()
                    if ball.state == 0:
                        ball.state = 1
                    elif ball.state == 1:
                        ball.state = 0
                if event.key == pygame.K_RETURN:
                    if ball.state == 2:

                        ball.lives = 5
                        ball.score = 0
                        background.fill((0, 0, 0))
                        score_surface = font.render(str(ball.score), False, (255, 255, 255))
                        score_pos = score_surface.get_rect(topright=background.get_rect().topright)
                        background.blit(score_surface, score_pos)
                        screen.blit(background, (0, 0))

                        read_board("board" + str(level) + ".txt")
                        bricksprite = pygame.sprite.RenderPlain(bricks)

                        ball.state = 0

                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    player.still()

        if ball.state == 2:
            if bricks:
                bricks.empty()
            game_over_surface = load_png('title.png')
            game_over_pos = game_over_surface.get_rect(centerx=background.get_width() / 2)
            background.fill((0,0,0))
            background.blit(game_over_surface, game_over_pos)
            screen.blit(background, (0,0))
            level = 1


        if ball.state < 1:
            # next level
            if not bricksprite:
                print("thinks bricksprite is empty!")
                bricksprite.empty()
                level += 1
                read_board("board" + str(level) + ".txt")
                bricksprite = pygame.sprite.RenderPlain(bricks)

            screen.blit(background, player.rect, player.rect)
            bricks.draw(background)
            screen.blit(background, ball.rect, ball.rect)

            background.fill((0, 0, 0), rect=(background.get_rect().left, background.get_rect().top,background.get_width(),36))
            score_surface = font.render(str(ball.score), False, (255, 255, 255))
            score_pos = score_surface.get_rect(topright=background.get_rect().topright)
            #background.fill((0, 0, 0), rect=score_pos)
            background.blit(score_surface, score_pos)

            lives_surface = font.render(str(ball.lives), False, (255, 255, 255))
            lives_pos = lives_surface.get_rect(topleft=background.get_rect().topleft)
            #background.fill((0, 0, 0), rect=score_pos)
            background.blit(lives_surface, lives_pos)


            screen.blit(background, (0, 0))

            bricksprite.update()
            playersprites.update()
            ballsprite.update()

            bricksprite.draw(screen)
            playersprites.draw(screen)
            ballsprite.draw(screen)


        pygame.display.flip()

if __name__ == '__main__':
    main()
