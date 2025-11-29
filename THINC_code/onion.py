import pygame
from pygame.locals import *


class Onion(pygame.sprite.Sprite):
    
    def __init__(self, screen, id, x, y):
        pygame.sprite.Sprite.__init__(self)

        if Onion.image is None:
            # This is the first time this class has been
            # instantiated. So, load the image for this and
            # all subsequence instances.
            Onion.image = pygame.draw.circle(screen, (0, 255, 0), (x - 100, y), 75)

        self.image = Onion.image
        self.x = x
        self.y = y
        self.id = id
    
    def update(self, x, y):
        self.x = x
        self.y = y