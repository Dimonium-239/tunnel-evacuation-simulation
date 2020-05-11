import pygame as pg
import colors as c
from settings import *

class RouteLines(pg.sprite.Sprite):
    def __init__(self, i):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((TUNNEL_LEN, 1))
        self.image.fill(c.WHITE)
        self.rect = pg.Rect( (MARGIN, ((WIN_HEIGHT-NUM_OF_PATHES*PATH_LEN)/2) +PATH_LEN*i), (TUNNEL_LEN, NUM_OF_PATHES*PATH_LEN) )
        