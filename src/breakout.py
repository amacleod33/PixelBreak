import sys
import random
import math
import os
import pygame
from pygame.locals import *

LIVES = 1

global block_sprite_path_strings
block_sprite_path_strings = ["basic_block.png", "med_block.png", "hard_block.png"]

def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('.\\img', name)
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


class Paddle(pygame.sprite.Sprite):
    """Movable tennis 'bat' with which one hits the ball
    Returns: bat object
    Functions: reinit, update, moveup, movedown
    Attributes: which, speed"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png('paddle.png')
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 20
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
        self.lives = 5
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

            targetbrick = pygame.sprite.spritecollideany(self, bricks)
            if targetbrick is not None:
                audio_brick_hit.play()
                self.score += 10

                tl = targetbrick.rect.collidepoint(newpos.topleft)
                tr = targetbrick.rect.collidepoint(newpos.topright)
                bl = targetbrick.rect.collidepoint(newpos.bottomleft)
                br = targetbrick.rect.collidepoint(newpos.bottomright)

                if (tr and tl) or (br and bl):
                    angle = -angle
                elif (tl or bl) or (tr or br):
                    angle = math.pi - angle

                targetbrick.health -= 1
                if targetbrick.health < 1:
                    targetbrick.image.fill((0,0,0))
                    bricks.remove(targetbrick)

            #####
            # if self.rect.colliderect(brick.rect):
            #     angle = math.pi - angle
            #     brick.health = brick.health - 1
            #     if brick.health == 0:
            #         brick.rect.w = 0
            #         brick.rect.h = 0


        self.vector = (angle, z)

class Brick(pygame.sprite.Sprite):
    def __init__(self, side, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_png(block_sprite_path_strings[health-1])
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.side = side
        self.speed = 0
        self.health = health


    #     self.state = 'Still'
    #     self.reinit()
    #
    # def reinit(self):
    #     self.state = "still"
    #     self.movepos = [0, 0]


        if self.side == "left":
            self.rect.midleft = (self.area.midleft[0], self.area.midleft[1] + 36)
        elif self.side == "center":
            self.rect.center = (self.area.center[0], self.area.center[1] + 36)
        elif self.side == "right":
            self.rect.midright = (self.area.midright[0], self.area.midright[1] + 36)
        elif self.side == "topleft":
            self.rect.topleft = (self.area.topleft[0], self.area.topleft[1] + 48)
        elif self.side == "topcenter":
            self.rect.midtop = (self.area.midtop[0],  self.area.midtop[1] + 48)
        elif self.side == "topright":
            self.rect.topright = (self.area.topright[0], self.area.topright[1] + 48)


def main():
    # Initialize screen
    global screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Breakout!')

    # Fill background
    global background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    # Initialize players
    global player
    player = Paddle()

    global score
    score = 0

    # Initialize ball

    speed = 6
    rand = 0.1 * random.randint(5, 8)
    ball = Ball((.7, speed))

    # Initialize bricks
    global bricks
    bricks = pygame.sprite.Group()
    brick1 = Brick('topcenter', 2)
    brick3 = Brick("left", 1)
    brick4 = Brick('center', 1)
    brick5 = Brick('right', 1)

    bricks.add(brick1,brick3,brick4,brick5)

    global font
    font = pygame.font.Font(os.path.join('assets', "font.TTF"), 36)

    # Initialize sprites
    # global score_surface
    # score_surface = font.render(str(score), False, (255, 255, 255))
    # score_pos = score_surface.get_rect(topright=background.get_rect().topright)

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
                if event.key == pygame.K_RIGHT:
                    player.moveright()
                if event.key == pygame.K_LEFT:
                    player.moveleft()
                if event.key == pygame.K_SPACE:
                    audio_pause.play()
                    if ball.state == 0:
                        ball.state = 1
                    else:
                        ball.state = 0
                if event.key == pygame.K_RETURN:
                    if ball.state == 2:

                        ball.lives = 5
                        background.fill((0,0,0))
                        score_surface = font.render(str(ball.score), False, (255, 255, 255))
                        score_pos = score_surface.get_rect(topright=background.get_rect().topright)
                        background.blit(score_surface, score_pos)
                        screen.blit(background, (0, 0))

                        brick1 = Brick('topcenter', 2)
                        brick3 = Brick("left", 1)
                        brick4 = Brick('center', 1)
                        brick5 = Brick('right', 1)

                        bricks.add(brick1, brick3, brick4, brick5)
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
            game_over_surface = font.render("GAME OVER", False, (255, 255, 255))
            game_over_pos = game_over_surface.get_rect(centerx=background.get_width() / 2)
            background.fill((0,0,0))
            background.blit(game_over_surface, game_over_pos)
            screen.blit(background, (0,0))

        if ball.state < 1:
            if not bricks:
                audio_next_level.play()
                ball.score += 100
                bricks = pygame.sprite.Group()
                brick0 = Brick('topleft', 2)
                brick1 = Brick('topcenter', 2)
                brick2 = Brick('topright', 2)
                brick3 = Brick("left", 1)
                brick4 = Brick('center', 1)
                brick5 = Brick('right', 1)

                bricks.add(brick0, brick1, brick2, brick3, brick4, brick5)

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

            print(ball.score)

        pygame.display.flip()

if __name__ == '__main__':
    main()

