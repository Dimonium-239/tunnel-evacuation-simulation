import pygame as pg
import colors as c
from settings import *
import random

class Car(pg.sprite.Sprite):
    def __init__(self):
        self.size = (random.randrange(meters_to_pixels(2.5), meters_to_pixels(4)), PATH_LEN-CAR_MARGIN)
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(self.size)
        self.image.fill(c.RED)
        self.rect = pg.Rect((random.randrange(MARGIN, meters_to_pixels(200)), ((WIN_HEIGHT-NUM_OF_PATHES*PATH_LEN)/2) + PATH_LEN*random.randrange(0, NUM_OF_PATHES) + CAR_MARGIN/2), self.size )
