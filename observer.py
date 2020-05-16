import pygame as pg
import colors as c
from settings import *

class Observer(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.xvel = 0
        self.startX = x
        self.startY = y
        self.image = pg.Surface((20, 20))
        self.image.fill(c.RED)
        self.rect = pg.Rect(x, y, 20, 20)

    def update(self, left, right, win_len_new):
        right_margin = TUNNEL_LEN
        if(self.rect.x >= 30 and self.rect.x <= right_margin):
            if left:
                self.xvel = -10
            if right:
                self.xvel = 10
            if not (left or right):
                self.xvel = 0
        if(self.rect.x < MARGIN):
            self.rect.x = MARGIN
            self.xvel = 0
        if(self.rect.x > right_margin):
            self.rect.x = right_margin
            self.xvel = 0
        self.rect.x += self.xvel
