import pygame as pg
import colors as c
from tunnel import Tunnel
from route_lines import RouteLines
from observer import Observer
from camera import Camera, camera_configure
from safe_zone import SafeZones
from car import Car
from cell import Cell

import random

from settings import *

pg.init()

win_len_new = DISPLAY

screen = pg.display.set_mode(DISPLAY, pg.RESIZABLE)

pg.display.set_caption("Fire in tunnel")
clock = pg.time.Clock()

bg = pg.Surface(DISPLAY)
bg.fill(c.BLUE)

observer = Observer(0, 2)
allGr = pg.sprite.Group()
allGr.add(observer)

left = right = False
tun = Tunnel()
allGr.add(tun)

for i in range(0, NUM_OF_PATHES + 1):
    allGr.add(RouteLines(i))

### Add cars to the cars group ###
carGr = pg.sprite.Group()
carsArr = []
for i in range(10):
    car = Car()
    carGr.add(car)
    carsArr.append(car)

### Add people to the people group ###
people_group = pg.sprite.Group()

### Choose What car will be settle in fire ###
badCar = carsArr[random.randint(0, len(carsArr) - 1)]
badCar.image.fill(c.WHITE)

### Init smoke cells ###
smokeGr = pg.sprite.Group()
smokeCells = []

isFire = False
fireCoor = ()
for x in range(int(MARGIN / 2), TUNNEL_LEN + int(MARGIN / 2), CELL_SIZE):
    tmpSmokeYCells = []
    for y in range(int((WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2),
                   int(((WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2) + PATH_LEN * NUM_OF_PATHES), CELL_SIZE):
        if isFire == False and (x > badCar.rect[0] and x < badCar.rect[0] + int(1.5 * CELL_SIZE) - 1) and (
                y > badCar.rect[1] and y < badCar.rect[1] + int(1.5 * CELL_SIZE)):
            smCell = Cell((x, y), c.RED, 255)
            smokeGr.add(smCell)
            tmpSmokeYCells.append(smCell)
            fireCoor = (len(smokeCells), len(tmpSmokeYCells) - 1)
            isFire = True
        else:
            smCell = Cell((x, y), c.GRAY, 0)
            smokeGr.add(smCell)
            tmpSmokeYCells.append(smCell)
    smokeCells.append(tmpSmokeYCells)
### --------------------- ###

camera = Camera(camera_configure, TUNNEL_LEN + 60, WIN_HEIGHT)

### Add evacuation exits ###
safe_zones_group = pg.sprite.Group()
tunExit = SafeZones((MARGIN / 2, (WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2), (EXIT_SIZE, PATH_LEN * NUM_OF_PATHES))
tunEnter = SafeZones((TUNNEL_LEN + MARGIN / 2, (WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2),
                     (EXIT_SIZE, PATH_LEN * NUM_OF_PATHES))

j = 1
for i in range(0, TUNNEL_LEN):
    if (i % meters_to_pixels(500) == 0):
        topSZ = SafeZones(
            (MARGIN / 2 + meters_to_pixels(500) * j, (WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2 - EXIT_SIZE / 2),
            (EXIT_SIZE * 2, EXIT_SIZE))
        downSZ = SafeZones((MARGIN / 2 + meters_to_pixels(500) * j,
                            (WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2 - EXIT_SIZE / 2 + NUM_OF_PATHES * PATH_LEN),
                           (EXIT_SIZE * 2, EXIT_SIZE))
        allGr.add(topSZ, downSZ)
        safe_zones_group.add(topSZ, downSZ)

allGr.add(tunExit, tunEnter)
safe_zones_group.add(tunEnter, tunExit)

fire_spreding_coor = [1, 1]
fire_radius = 1
clock = pg.time.Clock()
time = 0
fire_waves = 0
while RUNNING:
    clock.tick(250)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            RUNNING = False

        if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
            left = True
        if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
            right = True

        if event.type == pg.KEYUP and event.key == pg.K_RIGHT:
            right = False
        if event.type == pg.KEYUP and event.key == pg.K_LEFT:
            left = False

        if event.type == pg.VIDEORESIZE:
            win_len_new = (event.w, event.h)
            screen = pg.display.set_mode(win_len_new, pg.RESIZABLE)
            bg = pg.Surface(win_len_new)
            bg.fill(c.BLUE)

    screen.blit(bg, (0, 0))

    observer.update(left, right, win_len_new)

    camera.update(observer)

    time = time + clock.get_time()

    if time >= 750:
        # def f = ...
        for y in range(0, len(smokeCells[0])):
            for x in range(0, len(smokeCells)):
                for i in range(0, 10):
                    if ((x - fireCoor[0]) ** 2 + (y - fireCoor[1]) ** 2 < (fire_radius ** 2) - fire_radius * 3 * i):
                        smokeCells[x][y].set_smoke_density(100 + 10 * i)

        fire_radius += 1
        time = 0

    for a in allGr:
        screen.blit(a.image, camera.apply(a))

    for car in carGr:
        screen.blit(car.image, camera.apply(car))

    for a in smokeGr:
        screen.blit(a.image, camera.apply(a))

    pg.display.update()

pg.quit()
