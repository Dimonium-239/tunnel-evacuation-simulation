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
        self.image.fill(c.BLUE)
        self.rect = pg.Rect(x, y, 20, 20)

    def update(self, left, right, win_len_new):
        if(self.rect.x >= 30 and self.rect.x <= TUNNEL_LEN+MARGIN*2 - win_len_new[0]/2):
            if left:
                self.xvel = -10
            if right:
                self.xvel = 10
            if not (left or right):
                self.xvel = 0
        if(self.rect.x < MARGIN):
            self.rect.x = MARGIN
            self.xvel = 0
        if(self.rect.x > TUNNEL_LEN+MARGIN*2 - win_len_new[0]/2):
            self.rect.x = TUNNEL_LEN+MARGIN*2 - win_len_new[0]/2
            self.xvel = 0
        self.rect.x += self.xvel
