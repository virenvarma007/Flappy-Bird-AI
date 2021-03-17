import os
import sys
import pickle
import pygame
import neat
import time
import random
import keyboard
from pygame.locals import *
pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 800

Bird_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png")))]
PIPE_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "bg.png")))


STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    IMGS = Bird_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        #self.vel = 3

        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self. ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x, pgap, velo, nnheight):
        if x > 500:
            self.x = x
        else:
            self.x = 500
        self.height = 0
        self.vel = velo
        if pgap < 200:
            self.gap = self.GAP
        else:
            self.gap = pgap
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.vel

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        else:
            return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    pygame.display.update()


def main(genomes, config):

    nets = []
    ge = []
    print(len(genomes))

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        ge.append(g)

    loc = 700
    pgap = 200
    velo = 5
    nnheight = random.randrange(50, 450)
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(loc, pgap, velo, nnheight)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    loc = 700
    pgap = 200
    velo = 5
    nnheight = random.randrange(50, 450)
    with open('best.pickle', 'rb') as f:
        model = pickle.load(f)

    score = 0
    once = 0

    run = True
    while run:
        clock.tick(30)
        add_pipe = False
        rem = []
        bird.move()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        """pipe_ind = 0
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        output = model.activate((bird.y, abs(
            bird.y - pipes[pipe_ind].height), abs(bird.y + pipes[pipe_ind].bottom)))

        if output[0] > 0.5:
            bird.jump()"""

        if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
            bird.jump()
        for pipe in pipes:
            if pipe.collide(bird):
                ge[0].fitness += 100
                run = False
                # break
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()

        pipe_ind = 0
        if len(pipes) > 0 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = len(pipes) - 1

        if add_pipe:
            score += 1

            ge[0].fitness -= 5
            output = nets[0].activate((bird.y, abs(
                bird.y - pipes[pipe_ind].height), abs(bird.y + pipes[pipe_ind].bottom)))
            # pipe adding location 500-700
            loc = 500 + 200*output[0]
            # pipe gap
            pgap = 150 + 350*output[1]
            # pipe velocity
            velo = 2 + 8*output[2]
            # pipe height
            nnheight = 50 + 400 * output[3]

            pipes.append(Pipe(loc, pgap, velo, nnheight))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() > 730 or bird.y + bird.img.get_height() < 0:
            ge[0].fitness += 30
            pass
            #ge[1].fitness += 30
            #run = False
            # break
        base.move()
        draw_window(win, bird, pipes, base, score)

    # pygame.quit()
    sys.exit()


def run(config):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)  # Here 50 means the number of generations


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward - 2.txt")
    run(config_path)
