import pygame as pg
from settings import *

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pg.Rect(0, 0, width, height)
        self.win_size = (WIN_WIDTH, WIN_HEIGHT)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target, win_size):
        self.win_size = win_size
        self.state = self.camera_func(self.state, target.rect, self.win_size)


def camera_configure(camera, target_rect, win_size):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + win_size[0] / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)
    l = max(-(camera.width - win_size[0]), l)
    t = max(-(camera.height - WIN_HEIGHT), t)
    t = min(0, t)

    return pg.Rect(l, t, w, h)
