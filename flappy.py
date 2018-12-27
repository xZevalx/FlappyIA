#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Módulos
import sys, pygame
from pygame.locals import *

# Constantes
WIDTH = 393
HEIGHT = 700


# Clases
# ---------------------------------------------------------------------

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("assets/ball.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT / 2
        self.speed = [0.2, -0.2]

    def update(self, time, trampoline):
        self.rect.centerx += self.speed[0] * time
        self.rect.centery += self.speed[1] * time
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed[0] = -self.speed[0]
            self.rect.centerx += self.speed[0] * time
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed[1] = -self.speed[1]
            self.rect.centery += self.speed[1] * time

        if pygame.sprite.collide_rect(self, trampoline):
            self.speed[1] = -self.speed[1]
            self.rect.centery += self.speed[1] * time


class Trampoline(pygame.sprite.Sprite):

    def __init__(self, ypos):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("assets/trampoline.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.centery = ypos
        self.speed = 0.5

    def update(self, time, keys):
        if self.rect.left >= 0:
            if keys[K_LEFT]:
                self.rect.centerx -= self.speed * time
        if self.rect.right <= WIDTH:
            if keys[K_RIGHT]:
                self.rect.centerx += self.speed * time


class Flappy(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("assets/flappy.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT / 2
        self.speed = 0.1
        self.accel = 0.1

    def update(self, time, keys):
        if self.rect.top >= 0 and self.rect.bottom <= HEIGHT:  # No se sale por arriba ni por abajo
            self.rect.centery += .1 * self.accel * time ** 2 * self.speed * time  # Va cayendo
            if keys[K_SPACE]:
                # Salto
                self.rect.centery -= .5 * self.accel * time ** 2 + self.speed * time


# ---------------------------------------------------------------------

# Funciones
# ---------------------------------------------------------------------

def load_image(filename):
    try:
        image = pygame.image.load(filename)
    except pygame.error as message:
        raise SystemExit(message)
    image = image.convert_alpha()
    return image


# ---------------------------------------------------------------------

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
    pygame.display.set_caption("Flappy IA")

    background_image = load_image('assets/background.jpg')
    flappy = Flappy()

    clock = pygame.time.Clock()

    run = True
    while run:
        time = clock.tick(60)
        keys = pygame.key.get_pressed()
        for events in pygame.event.get():
            if events.type == QUIT:
                run = False
        flappy.update(time, keys)
        screen.blit(pygame.transform.scale(background_image, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(flappy.image, flappy.rect)
        pygame.display.flip()
    pygame.display.quit()
    return 0


if __name__ == '__main__':
    pygame.init()
    main()
