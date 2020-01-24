import pygame
import neat
import os
import random

pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 900
win = pygame.display.set_mode((600, 900), pygame.FULLSCREEN)

STAT_FONT = pygame.font.SysFont("comicsans", 50)

PLAYER_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'player.png')).convert_alpha())
RIGHTSPIKE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'spikeright.png')).convert_alpha())
LEFTSPIKE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'spikeleft.png')).convert_alpha())
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bgwhite.png")).convert_alpha(), (600, 900))

class Player:
    IMG = PLAYER_IMG
    TERMINAL_VEL_UP = -25
    TERMINAL_VEL_DOWN = 25
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xvel = 7.5
        self.yvel = 0
        self.yaccel = 2
    
    def move(self):
        xd = self.xvel
        self.yvel += self.yaccel

        if self.yvel <= self.TERMINAL_VEL_UP:
            self.yvel = self.TERMINAL_VEL_UP
        elif self.yvel >= self.TERMINAL_VEL_DOWN:
            self.yvel = self.TERMINAL_VEL_DOWN

        yd = self.yvel
        
        self.x += xd
        self.y += yd
        
    def change_gravity(self):
        self.yaccel = -self.yaccel

    def change_dir(self):
        self.xvel = -self.xvel

    def l_collide(self):
        return self.x <= 0

    def r_collide(self):
        return self.x + self.IMG.get_width() >= 600

    def border_collide(self):
        return self.y <= 0 or self.y + self.IMG.get_height() >= 900
        
    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

class LeftSpike:
    X = 0
    IMG = LEFTSPIKE_IMG

    def __init__(self, y):
        self.x = self.X
        self.y = y

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

    def collide(self, player):
        player_mask = player.get_mask()
        spike_mask = self.get_mask()
        offset = (self.x - round(player.x), self.y - round(player.y))

        point = player_mask.overlap(spike_mask, offset)

        if point:
            return True

        return False

class RightSpike:
    X = 520
    IMG = RIGHTSPIKE_IMG

    def __init__(self, y):
        self.x = self.X
        self.y = y

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

    def collide(self, player):
        player_mask = player.get_mask()
        spike_mask = self.get_mask()
        offset = (self.x - round(player.x), self.y - round(player.y))

        point = player_mask.overlap(spike_mask, offset)

        if point:
            return True

        return False

def draw_window(win, players, spikes, score):
    win.blit(BG_IMG, (0, 0))

    score_label = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    for spike in spikes:
        spike.draw(win)

    for player in players:
         player.draw(win)

    pygame.display.update()

def eval_genomes(genomes, config):
    gap_size = 275
    top = 400
    bottom = 625
    spikes = []

    def set_gap():
        nonlocal top, bottom
        top = random.randrange(175, 500)
        bottom = top + gap_size

    def spawn_start():
        nonlocal spikes
        spikes = []
        for i in range(10):
            spike_displacement = i * 80
            spikes.append(RightSpike(top - spike_displacement))
            spikes.append(RightSpike(bottom + spike_displacement))

    def spawn_left():
        nonlocal spikes
        set_gap()
        spikes = []
        for i in range(10):
            spike_displacement = i * 80
            spikes.append(LeftSpike(top - spike_displacement))
            spikes.append(LeftSpike(bottom + spike_displacement))

    def spawn_right():
        nonlocal spikes
        set_gap()
        spikes = []
        for i in range(10):
            spike_displacement = i * 80
            spikes.append(RightSpike(top - spike_displacement))
            spikes.append(RightSpike(bottom + spike_displacement))

    spawn_start()

    players = []
    nets = []
    ge = []

    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(300, 150))
        ge.append(g)

    score = 0
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if len(players) <= 0:
            run = False
            break

        for x, player in enumerate(players):
            player.move()
            ge[x].fitness += 0.2

            acc = player.yaccel
            vel = player.yvel
            pos = player.y
            spike1 = abs((top + 80) - pos)
            spike2 = abs(bottom - pos)

            output = nets[players.index(player)].activate((acc, vel, pos, spike1, spike2))

            if output[0] > 0.5:
                player.change_gravity()

        if players[0].r_collide():
            for x, player in enumerate(players):
                player.change_dir()
                ge[x].fitness += 10
            spawn_left()
            score += 1

        if players[0].l_collide():
            for x, player in enumerate(players):
                player.change_dir()
                ge[x].fitness += 10
            spawn_right()
            score += 1

        for spike in spikes:
            for x, player in enumerate(players):
                if spike.collide(player):
                    ge[x].fitness -= (abs(player.y - (top + 150)) / 200)
                    players.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    
        for x, player in enumerate(players):
            if player.border_collide():
                ge[x].fitness -= ((abs(player.y - (top + 150)) / 200) + 2)
                players.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, players, spikes, score)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 500)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
