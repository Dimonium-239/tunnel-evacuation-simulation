import pygame as pg
import colors as c
from settings import *

import math
import random

class Tunnel(pg.sprite.Sprite):
    """
    A class used to represent routes of tunnel

    ...

    Attributes
    ----------
    tunnel_group : 
        group which contain routes, lines
    exit_group :
        group which contain evacuation exits
    cars_group :
        group which contain cars
    image : 
        image of routes
    rect : 
        figure of tunnel
    
    Methods
    -------
    draw_tunnel(surface, camera)
        Draw tunnel with lines on it.

    get_burning_car()
        getter for burning car
    """
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        
        self.tunnel_group = pg.sprite.Group()
        self.exit_group = pg.sprite.Group()
        self.cars_group = pg.sprite.Group()
        self.smoke_group = pg.sprite.Group()
        self.people_group = pg.sprite.Group()
        self.cars_array = []
        self.people_array = []
        self.exit_array = []
        self.cell_grid = []

        self.image = pg.Surface(((TUNNEL_LEN, NUM_OF_PATHES*PATH_LEN)))
        self.image.fill(c.BLACK)
        
        self.rect = pg.Rect( (MARGIN, (WIN_HEIGHT-NUM_OF_PATHES*PATH_LEN)/2), (TUNNEL_LEN, NUM_OF_PATHES*PATH_LEN) )        
        self._smoke_time = 0

        self.__draw_cars(100)       # Set numbers of car on the tunnel

        self.__draw_tunnel()
        self.__draw_evacuating_exites()
        self._burning_car = self.__make_car_burn()
        self.__make_cell_grid()
        self.__init_fire_place()
        self.find_peoples_coordinates()
        self.fire_x, self.fire_y = self.get_fire_coordinates()
        self.__find_closest_exit()


    def smoke_spreading_update(self, time, fire_radius, class_obj):
        """
        Increase fire radius in defined step of time

        Parameters
        ----------
        time : int, 
            Time from python timer
        fire_radius : int,
            Radius of fire
        """
        if time >= 750:
            for y in range(0, len(self.cell_grid[0])):
                for x in range(0, len(self.cell_grid)):
                    for i in range(0, 8):
                        if ((x - self.fire_x) ** 2 + (y - self.fire_y) ** 2 < (fire_radius ** 2) - fire_radius * 3 * i):
                            self.cell_grid[x][y].set_smoke_density(100 + 10 * i)
                            self.smoke_group.add(self.cell_grid[x][y])

            fire_radius += 1
            class_obj.kill_people()
            time = 0
            return time, fire_radius
        return time, fire_radius
        
    
    def find_peoples_coordinates(self):
        """
        Iterate by array of cars to generate one person near the car.

        TODO: Generate rondomly 1-4 peoples for small cars (<4 m)
        TODO: Generate rondomly 1-8 peoples for small cars (>13 m)  
        """
        for car in self.cars_array:
            self.__init_person(car.rect.x, car.rect.y + PATH_LEN-CAR_MARGIN + 1)

    def blit_tunnel(self, surface, camera):
        """
        Blit all tunnel elemnts on screen

        Parameters
        ----------
        surface : pygame.Surface, 
            Main surface where everything is drawn.        
        camera : camera.Camera,
            Camera object for ability to follow tunnel in all its length.
        """
        self.cars_group.add(self.cars_array)
        self.__blit_it(surface, camera, self.tunnel_group)
        self.__blit_it(surface, camera, self.exit_group)
        self.__blit_it(surface, camera, self.cars_group)
        self.__blit_it(surface, camera, self.people_group)
        
    def blit_smoke(self, surface, camera):
        """
        Blit smoke on screen

        Parameters
        ----------
        surface : pygame.Surface, 
            Main surface where everything is drawn.        
        camera : camera.Camera,
            Camera object for ability to follow tunnel in all its length.
        """
        self.__blit_it(surface, camera, self.smoke_group)


    def get_burning_car(self):
        """
        Returns
        -------
            Car which will be smoke generator
        """
        return self._burning_car
    
    def get_fire_coordinates(self):
        """
        Returns
        -------
            Tuple (x, y) with hearth of flame coordinates
        """
        for cell_line in self.cell_grid: 
            for cell in cell_line:
                if (cell.rect.x in range(self._burning_car.rect[0], self._burning_car.rect[0] + int(1.5 * CELL_SIZE) - 1)) and (cell.rect.y in range(self._burning_car.rect[1], self._burning_car.rect[1] + int(1.5 * CELL_SIZE)) ):
                    return self.cell_grid.index(cell_line), cell_line.index(cell) 

    def move_person(self):
        for person in self.people_array:
            x_p, y_p, *_ = person.rect
            x_e, y_e = person.close_exit
            step = 0
            
            person_TEMP_group = pg.sprite.Group()
            person_TEMP_group.add(person)

            person_car = pg.sprite.groupcollide(person_TEMP_group, self.cars_group, False, False)
            if list(person_car.keys()):
                c = list(person_car.keys())[0]
                if y_p in range(c.rect[1], c.rect[1]+c.rect[3]+5) and person.prev_step[1] in range(c.rect[1], c.rect[1]+c.rect[3]+5):
                    person.rect.x = person.rect.x
                    if y_p < y_e:
                        person.rect.y += 5
                    if y_p > y_e:
                        person.rect.y -= 5
                    person.set_prev_step( (person.rect.x, person.rect.y) )
                    continue
                if y_p in range(c.rect[0], c.rect[0]+c.rect[2]+5) and person.prev_step[0] in range(c.rect[0], c.rect[0]+c.rect[2]+5):
                    person.rect.x = person.rect.x
                    if x_p < x_e:
                        person.rect.x += 5
                    if x_p > x_e:
                        person.rect.x -= 5
                    person.set_prev_step( (person.rect.x, person.rect.y) )
                    continue
            else:
                if x_p > x_e:
                    step = -5
                if x_p < x_e:
                    step = +5

                x = person.rect.x + step
                y = self.__path_equality((x_p,y_p), (x_e, y_e), x)
                person.set_prev_step((person.rect[0], person.rect[1]))
                person.rect.x = x
                person.rect.y = y 


    def __find_closest_exit(self):
        for person in self.people_array:
            close_exit = TUNNEL_LEN
            for e in self.exit_array:
                x, y, s_x, s_y = e.rect
                x_p, y_p, *_ = person.rect

                centre = (x + s_x//2, y + s_y//2) 
            
                if int( ((x_p - centre[0])**2 + (y_p - centre[1])**2)**0.5 ) < close_exit:
                    close_exit = int( ((x_p - centre[0])**2 + (y_p - centre[1])**2)**0.5 )
                    if x < y:
                        person.close_exit = centre[0], person.rect.y
                    else:
                        person.close_exit = centre
        
    
    def __path_equality(self, dot1, dot2, x):
        x_A, y_A = dot1
        x_B, y_B = dot2
        try:
            y = ((y_A - y_B)/(x_A - x_B))*x + (y_A - (y_A - y_B)/(x_A - x_B)*x_A)
        except:
            y = ((y_A - y_B)/(x_A - x_B+1))*x + (y_A - (y_A - y_B)/(x_A - x_B+1)*x_A)
        return y 
            

    def __draw_tunnel(self):
        """
        Draws tunnel with lines on it.
        """
        self.tunnel_group.add(self)
        for i in range(0, NUM_OF_PATHES + 1):
            self.tunnel_group.add(_RouteLines(i))
             
    def __init_person(self, x, y):
        """
        Add peoples to array of peoples
        """
        self.people_array.append(_Person( (x,y) ))
        self.people_group.add(self.people_array)

    def __draw_cars(self, car_number):
        """
        Generate cars. 

        Iterates while number in array of cars is less than 
        car number parameter and checks car position to prevent collisions

        BUG: If tunnel is too small and number of cars is too big loop can 
        never reach a stop condition
        ----------
        Parametr:
        ----------
        car_number: how much we need cars in our tunnel
        """
        while len(self.cars_array) < car_number:
            new_car = _Car()
            is_good_position = True
            for car_i in self.cars_array:
                if self.__collision(new_car, car_i):
                    is_good_position = False
                    break
            if is_good_position:
                self.cars_array.append(new_car)

    def __draw_evacuating_exites(self):
        """
        Add evacuation exits to pygame.group
        """
        tunExit = _SafeZones((MARGIN / 2, (WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2), (EXIT_SIZE, PATH_LEN * NUM_OF_PATHES))
        tunEnter = _SafeZones((TUNNEL_LEN + MARGIN / 2, (WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2),
                     (EXIT_SIZE, PATH_LEN * NUM_OF_PATHES))
        
        self.exit_array.extend([tunEnter, tunExit])
        self.exit_group.add([tunEnter,tunExit])

        ev_exits_len = meters_to_pixels(500)
        if TUNNEL_LEN > ev_exits_len:
            for i in range(ev_exits_len, TUNNEL_LEN):
                if (i % ev_exits_len == 0):
                    topSZ = _SafeZones(
                        (MARGIN / 2 + ev_exits_len, (WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2 - EXIT_SIZE / 2),
                        (EXIT_SIZE * 2, EXIT_SIZE))
                    downSZ = _SafeZones((MARGIN / 2 + ev_exits_len,
                                        (WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2 - EXIT_SIZE / 2 + NUM_OF_PATHES * PATH_LEN),
                                    (EXIT_SIZE * 2, EXIT_SIZE))
                    self.exit_group.add(topSZ, downSZ)
                    self.exit_array.extend([topSZ, downSZ])


    def __make_car_burn(self):
        """
        Randomly chooses car which will be smoke generator
        """
        pos = random.randint(0, len(self.cars_array) - 1)
        burning_car = self.cars_array[pos]
        burning_car.image.fill(c.WHITE)
        self.cars_array[pos] = burning_car
        return burning_car
   
    def __init_fire_place(self):
        """
        Change color, densety of hearth of flame cell and
        add it to groupe of smoke
        """
        fire_x, fire_y = self.get_fire_coordinates() 
        self.cell_grid[fire_x][fire_y].image.fill(c.RED)
        self.cell_grid[fire_x][fire_y].set_smoke_density(225)
        
        self.smoke_group.add(self.cell_grid[fire_x][fire_y])
    
    def __collision(self, car1, car2):
        """
        Auxiliary function to check collision
        """
        return car1.rect.colliderect(car2.rect)

    
    def __blit_it(self, surface, camera, group):
        """
        Auxiliary function for blit_tunnel
        """
        for elem in group:
            surface.blit(elem.image, camera.apply(elem))

    def __make_cell_grid(self):
        """
        Auxiliary function for making array of cells. Will serve as base for drawing smoke
        """
        for x in range(int(MARGIN / 2), TUNNEL_LEN + int(MARGIN / 2), CELL_SIZE):
            tmpSmokeYCells = []
            for y in range(int((WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2),
                        int(((WIN_HEIGHT - NUM_OF_PATHES * PATH_LEN) / 2) + PATH_LEN * NUM_OF_PATHES), CELL_SIZE):
                smCell = _Cell((x, y), c.GRAY, 0)
                tmpSmokeYCells.append(smCell)
            self.cell_grid.append(tmpSmokeYCells)

    
class _Cell(pg.sprite.Sprite):
    def __init__(self, pos, color, alpha):
        pg.sprite.Sprite.__init__(self)
        self.size = (CELL_SIZE, CELL_SIZE)
        self.pos = pos
        self.image = pg.Surface(self.size)
        self.image.fill(color)
        self.image.set_alpha(alpha)
        self.rect = pg.Rect(self.pos, self.size )

    def set_smoke_density(self, alpha):
        self.image.set_alpha(alpha)
    
    def get_smoke_density(self):
        return self.image.get_alpha()


class _RouteLines(pg.sprite.Sprite):
    """
    Lines on the road.
    Parameter
    ----------
    i : iterator for drawing many lines with defined step.
    """
    def __init__(self, i):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((TUNNEL_LEN, 1))
        self.image.fill(c.WHITE)
        self.rect = pg.Rect( (MARGIN, ((WIN_HEIGHT-NUM_OF_PATHES*PATH_LEN)/2) +PATH_LEN*i), (TUNNEL_LEN, NUM_OF_PATHES*PATH_LEN) )
        

class _SafeZones(pg.sprite.Sprite):
    """
    Evacuation zones, reaching which people are saved.
    """
    def __init__(self, position, size):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(size)
        self.image.fill(c.GREEN)
        self.rect = pg.Rect( position, size )


class _Car(pg.sprite.Sprite):
    """
    Cars in tunnel
    """
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        car_sizes = [meters_to_pixels(3.3), meters_to_pixels(3.6), meters_to_pixels(4), meters_to_pixels(3.3), meters_to_pixels(8)]
        self.size = (random.choice(car_sizes), PATH_LEN-CAR_MARGIN)
        self.image = pg.Surface(self.size)
        self.image.fill(c.RED)
        self.rect = pg.Rect((random.randrange(MARGIN, TUNNEL_LEN), ((WIN_HEIGHT-NUM_OF_PATHES*PATH_LEN)/2) + PATH_LEN*random.randrange(0, NUM_OF_PATHES) + CAR_MARGIN/2), self.size )


class _Person(pg.sprite.Sprite):
    def __init__(self, coord):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill( (0, 255, 0) )
        self.rect = pg.Rect(coord, (CELL_SIZE, CELL_SIZE))

        self.hp = 100
        self.close_exit = 0
        self.prev_step = ()
    
    def get_hp(self):
        return self.hp

    def set_prev_step(self, ps):
        self.prev_step = ps

    def get_prev_step(self):
        return self.prev_step
    
    def decrease_hp(self, smoke_density):
        if smoke_density == 110:
            self.hp -= 2
        elif smoke_density == 120:
            self.hp -= 2
        elif smoke_density == 130:
            self.hp -= 2
        elif smoke_density == 140:
            self.hp -= 5
        elif smoke_density == 150:
            self.hp -= 5
        elif smoke_density > 150:
            self.hp -= 15
        self.__hp_indicator()

    def __hp_indicator(self):
        if self.hp in range(95, 101):
            self.image.fill( (0, 255, 0) )
        elif self.hp in range(85, 95):
            self.image.fill( (128, 255, 0) )
        elif self.hp in range(65, 85):
            self.image.fill( (255, 255, 0) )
        elif self.hp in range(45, 65):
            self.image.fill( (255, 128, 0) )
        elif self.hp in range(25, 45):
            self.image.fill( (128, 64, 0) )
        else:
            self.image.fill( (128, 0, 0) )