import pygame
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

def draw_window(win, player, spikes, score):
    win.blit(BG_IMG, (0, 0))

    score_label = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    for spike in spikes:
        spike.draw(win)

    player.draw(win)
    pygame.display.update()

def eval_genomes():
    spike_amount = 4
    gap_size = 300
    top = 0
    bottom = 0
    spikes = []

    def set_gap():
        nonlocal top, bottom
        top = random.randrange(0, 350)
        bottom = top + gap_size

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

    spawn_right()

    player = Player(50, 50)
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.change_gravity()

        for spike in spikes:
            if spike.collide(player):
                run = False
                pygame.quit()
                quit()

        if player.r_collide():
            player.change_dir()
            spawn_left()
            score += 1

        if player.l_collide():
            player.change_dir()
            spawn_right()
            score += 1

        if player.border_collide():
            run = False
            pygame.quit()
            quit()

        player.move()
        draw_window(win, player, spikes, score)

eval_genomes()
