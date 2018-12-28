#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import random
import math
from datetime import datetime
from pygame.locals import *

random.seed(datetime.now().second)


def load_image(filename):
    try:
        image = pygame.image.load(filename).convert_alpha()
    except pygame.error as message:
        raise SystemExit(message)
    return image


def distance(point1, point2):
    return math.sqrt(math.pow(point2[0] - point1[0], 2) + math.pow(point2[1] - point1[1], 2))


class FlappySprite(pygame.sprite.Sprite):

    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game  # A reference to the container game
        self.image = load_image("assets/flappy.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = self.game.WIDTH / 3
        self.rect.centery = int(self.game.HEIGHT * (1 / 3))
        self.speed = 0.1
        self.accel = 0.1
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, time, keys):
        if self.rect.top >= 0 and self.rect.bottom <= self.game.HEIGHT:  # No se sale por arriba ni por abajo
            if keys[K_SPACE]:
                self.jump(time)
            else:
                self.fall(time)
        elif self.rect.top <= 0:
            self.fall(time)

    def fall(self, time):
        self.rect.centery += .08 * self.accel * time ** 2 * self.speed * time

    def jump(self, time):
        self.rect.centery -= .2 * self.accel * time ** 2 + self.speed * time

    def reset(self):
        self.rect.centerx = self.game.WIDTH / 3
        self.rect.centery = int(self.game.HEIGHT * (1 / 3))


class TubeSprite(pygame.sprite.Sprite):
    UP = 0
    DOWN = 1

    def __init__(self, type):
        pygame.sprite.Sprite.__init__(self)
        if type == TubeSprite.UP:
            self.image = load_image('assets/tube_up.png')
        elif type == TubeSprite.DOWN:
            self.image = load_image('assets/tube_down.png')
        self.rect = self.image.get_rect()
        self.speed = 0.2
        self.moving = True
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, time):
        # Los tubos siempre se mueven hacia la izquierda
        if self.moving:
            self.rect.centerx -= self.speed * time


class TubesPair:
    VERTICAL_GAP = 150

    def __init__(self, game):
        self.game = game
        self.tube_up = TubeSprite(TubeSprite.UP)
        self.tube_down = TubeSprite(TubeSprite.DOWN)

        self.center = None

        self.set_center()

        # Ambos parten a la derecha
        self.tube_up.rect.left = self.game.WIDTH
        self.tube_down.rect.left = self.game.WIDTH

        self.group = pygame.sprite.Group(self.tube_up, self.tube_down)

        # Se usa para calcular cuando reposicionar los tubos al inicio
        self.left_limit = -(self.game.TUBES_DISTANCE - int(self.game.WIDTH % self.game.TUBES_DISTANCE))

    def update(self, *args):
        self.group.update(*args)
        # Si los tubos están a la izquierda fuera de la pantalla se resetean
        if self.tube_up.rect.left < self.left_limit:
            self.reset()

    def get_group(self):
        return self.group

    def reset(self):
        self.set_xpos(self.game.WIDTH)
        self.set_center()

    def set_xpos(self, xpos):
        self.tube_up.rect.left = xpos
        self.tube_down.rect.left = xpos

    def set_center(self):
        self.center = random.uniform(int(self.game.HEIGHT * (2 / 5)), int(self.game.HEIGHT * (3 / 5)))
        self.tube_up.rect.top = self.center + int(self.VERTICAL_GAP / 2)
        self.tube_down.rect.bottom = self.center - int(self.VERTICAL_GAP / 2)


class GameStates:
    START = 0
    PLAYING = 1
    RESET = 2


class FlappyGame:
    WIDTH = 810
    HEIGHT = 540
    TUBES_DISTANCE = 350
    TUBES_PAIRS = 3

    def __init__(self):
        self.background = None
        self.screen = None
        self.player = None
        self.tubes_pairs = []
        self.score = 0
        self.clock = None
        self.is_executing = False
        self.next_tubes = 0
        self.font = None
        self.state = GameStates.START
        self.ground = None

    def init_engine(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
        pygame.display.set_caption("Flappy IA")
        self.background = load_image('assets/background.png')
        self.player = FlappySprite(self)
        self.clock = pygame.time.Clock()
        self.is_executing = True
        self.font = pygame.font.Font('assets/ARCADECLASSIC.TTF', 30)
        self.init_tubes()

        # Un sprite invisible para el suelo
        self.ground = pygame.sprite.Sprite()
        self.ground.image = pygame.Surface((self.WIDTH, 10))
        self.ground.rect = self.ground.image.get_rect(topleft=(0, self.HEIGHT))

    def init_tubes(self):
        for i in range(self.TUBES_PAIRS):
            self.tubes_pairs.append(TubesPair(self))
            # Se separan los tubos horizontalmente
            self.tubes_pairs[-1].set_xpos(int(self.WIDTH + self.TUBES_DISTANCE * i))

    def execute(self):
        self.init_engine()

        while self.is_executing:
            time = self.clock.tick(60)
            keys = self.get_keys()
            for events in pygame.event.get():
                self.handle_event(events, keys)

            if self.state == GameStates.PLAYING:
                self.update_state(time, keys)
                self.check_collision()
                self.draw_screen()
            elif self.state == GameStates.START:
                self.draw_start_screen()
            elif self.state == GameStates.RESET:
                self.draw_reset_screen()
            pygame.display.flip()

        pygame.display.quit()

    def update_state(self, time, keys):
        self.player.update(time, keys)
        for tubes in self.tubes_pairs:
            tubes.update(time)
        # update score
        self.update_score()

    def update_score(self):
        # Los tubos que estaban al frente ahora están atrás del ave
        if self.tubes_pairs[self.next_tubes].tube_up.rect.right < self.player.rect.left:
            # Se anota un punto
            self.score += 1
            # Se actualiza el next
            self.next_tubes = int((self.next_tubes + 1) % self.TUBES_PAIRS)

    def draw_screen(self):
        self.screen.blit(pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT)), (0, 0))
        self.screen.blit(self.player.image, self.player.rect)
        for tubes in self.tubes_pairs:
            tubes.get_group().draw(self.screen)
        self.draw_score()
        self.place_ground()

    def draw_score(self):
        s = self.font.render('Score  {}'.format(self.score), True, (255, 255, 255))
        self.screen.blit(s, (10, 10))

    def check_collision(self):
        if (pygame.sprite.spritecollideany(self.player,
                                           self.tubes_pairs[self.next_tubes].group,
                                           collided=pygame.sprite.collide_mask) or
                pygame.sprite.collide_rect(self.player, self.ground)):
            self.game_over()

    def reset(self):
        self.player.reset()
        self.score = 0
        self.next_tubes = 0
        self.tubes_pairs.clear()
        self.init_tubes()
        self.state = GameStates.PLAYING

    def game_over(self):
        self.state = GameStates.RESET

    def handle_event(self, events, keys):
        if events.type == QUIT:
            self.is_executing = False
        if keys[K_SPACE]:
            if self.state == GameStates.RESET:
                self.reset()
            elif self.state == GameStates.START:
                self.state = GameStates.PLAYING
            elif self.state == GameStates.RESET:
                self.reset()

    @staticmethod
    def get_keys():
        return pygame.key.get_pressed()

    def get_distances(self):
        """
        Retorna las siguientes distancias desde el player el centro del player:

        1. Distancia al suelo
        2. Distancia al borde superior derecho del tubo que viene por abajo
        3. Distancia al borde inferior derecho del tube que viene por arriba
        """
        return (self.HEIGHT - self.player.rect.centery,
                distance(self.player.rect.center, self.tubes_pairs[self.next_tubes].tube_up.rect.topright),
                distance(self.player.rect.center, self.tubes_pairs[self.next_tubes].tube_down.rect.bottomright))

    def draw_start_screen(self):
        s = self.font.render("Presiona  ESPACIO  para  iniciar  el  juego", True, (255, 255, 255))
        self.screen.blit(s, s.get_rect(center=(self.WIDTH / 2, self.HEIGHT / 2)))

    def draw_reset_screen(self):
        s = self.font.render("Juego  terminado  tu  puntaje  fue  {}".format(self.score), True, (0, 0, 0))
        self.screen.blit(s, s.get_rect(center=(self.WIDTH / 2, self.HEIGHT / 2)))


    def place_ground(self):
        self.screen.blit(self.ground.image, self.ground.rect)


if __name__ == '__main__':
    game = FlappyGame()
    game.execute()
