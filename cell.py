import pygame as pg
import colors as c
from settings import *

class Cell(pg.sprite.Sprite):
    def __init__(self, pos, color, alpha):
        self.size = (CELL_SIZE, CELL_SIZE)
        self.pos = pos
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(self.size)
        self.image.fill(color)
        self.image.set_alpha(alpha)
        self.rect = pg.Rect(self.pos, self.size )

    def set_smoke_density(self, alpha):
        self.image.set_alpha(alpha)
    
    def get_smoke_density(self):
        return self.image.get_alpha()