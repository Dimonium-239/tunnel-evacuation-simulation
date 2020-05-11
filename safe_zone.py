import pygame as pg
import colors as c
from settings import *

class SafeZones(pg.sprite.Sprite):
    def __init__(self, position, size):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(size)
        self.image.fill(c.GREEN)
        self.rect = pg.Rect( position, size )
