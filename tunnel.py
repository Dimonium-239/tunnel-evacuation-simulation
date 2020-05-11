import pygame as pg
import colors as c
from settings import *

class Tunnel(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(((TUNNEL_LEN, NUM_OF_PATHES*PATH_LEN)))
        self.image.fill(c.BLACK)
        self.rect = pg.Rect( (MARGIN, (WIN_HEIGHT-NUM_OF_PATHES*PATH_LEN)/2), (TUNNEL_LEN, NUM_OF_PATHES*PATH_LEN) )

    