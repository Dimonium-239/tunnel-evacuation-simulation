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
    def __init__(self, settings_tuple):
        pg.sprite.Sprite.__init__(self)
        
        self.path_len, \
        self.tunnel_len, \
        self.exit_size, \
        self.car_margin, \
        self.cell_size, \
        self.num_of_pathes, \
        self.margin, \
        self.car_quantity = settings_tuple


        self.tunnel_group = pg.sprite.Group()
        self.exit_group = pg.sprite.Group()
        self.cars_group = pg.sprite.Group()
        self.smoke_group = pg.sprite.Group()
        self.people_group = pg.sprite.Group()
        self.cars_array = []
        self.people_array = []
        self.exit_array = []

        self.image = pg.Surface(((self.tunnel_len, (self.num_of_pathes*self.path_len)+1)))
        self.image.fill(c.BLACK)
        
        self.rect = pg.Rect( (self.margin, (WIN_HEIGHT-self.num_of_pathes*self.path_len)/2), (self.tunnel_len, self.num_of_pathes*self.path_len) )        
        self._smoke_time = 0

        self.__draw_cars(self.car_quantity)       # Set numbers of car on the tunnel

        self.__draw_tunnel()
        self.__draw_evacuating_exites()
        self._burning_car = self.__make_car_burn()
        self.__init_fire_place()
        self.find_peoples_coordinates()
        self.fire_x, self.fire_y = self.get_fire_coordinates()
        self.__find_closest_exit()
          
    
    def find_peoples_coordinates(self):
        """
        Iterate by array of cars to generate one person near the car.
        """
        for car in self.cars_array:
            if car.size[0] >= self.meters_to_pixels(8):
                for i in range(random.randint(3, 8)):
                    self.__init_person(car.rect.x + 15*i, car.rect.y + self.path_len-self.car_margin + 1)
            else:
                for i in range(1,random.randint(2, 5)):
                    self.__init_person(car.rect.x + (15 + i)*int(bool(2//i)), \
                        car.rect.y + (self.path_len-self.car_margin+1)*(1-(i%2)) - (self.car_margin+1-self.cell_size*2)*(i%2))

    def blit_tunnel(self, r, surface, camera):
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
        for elem in self.exit_group:
            self.image.blit(elem.image, (elem.rect[0], elem.rect[1]))

        self.__blit_it(surface, camera, self.tunnel_group)
        self.image.fill((0,0,0))
        self.__draw_tunnel()
        for elem in self.cars_group:
            self.image.blit(elem.image, (elem.rect[0], elem.rect[1]) )
        
        for elem in self.people_array:
            elem.display(self.image)
        
        for i in range(1, 7):
            if((r - (10*i)*math.log(i))>=0):
                smk = Smoke(r - (10*i)*math.log(i)+25, (10*i)*math.log(i)+25, self.get_fire_coordinates(), self.image)
                self.smoke_group.add(smk)
        
        
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
        _x_coord = self._burning_car.rect[0]
        _y_coord = self._burning_car.rect[1]
        _width = int(self._burning_car.rect[2]/7)
        _len = int(self._burning_car.rect[3]/2)
        return _x_coord+_width, _y_coord+_len


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
                if y_p in range(c.rect[1], c.rect[1]+c.rect[3]+10) and person.prev_step[1] in range(c.rect[1], c.rect[1]+c.rect[3]+10):
                    person.rect.x = person.rect.x
                    if y_p < y_e:
                        person.rect.y += 5
                    if y_p > y_e:
                        person.rect.y -= 5
                    person.set_prev_step( (person.rect.x, person.rect.y) )
                    continue
                if y_p in range(c.rect[0], c.rect[0]+c.rect[2]+6) and person.prev_step[0] in range(c.rect[0], c.rect[0]+c.rect[2]+6):
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
            close_exit = self.tunnel_len
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
        for i in range(0, self.num_of_pathes + 1):
            pg.draw.line(self.image, c.WHITE, (0, self.path_len*i), (self.tunnel_len, self.path_len*i))


    def __init_person(self, x, y):
        """
        Add peoples to array of peoples
        """
        self.people_array.append(_Person( (x,y), self.cell_size ))
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
            new_car = _Car(self.path_len, self.car_margin, self.tunnel_len, self.num_of_pathes)
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
    
        tunEnter = _SafeZones((0,0), (self.exit_size, self.path_len * self.num_of_pathes))
        tunExit = _SafeZones((self.tunnel_len-self.margin, 0), (self.exit_size, self.path_len * self.num_of_pathes))

        self.exit_array.extend([tunEnter, tunExit])
        self.exit_group.add([tunEnter,tunExit])

        ev_exits_len = self.meters_to_pixels(500)
        if self.tunnel_len > ev_exits_len:
            for i in range(ev_exits_len, self.tunnel_len):
                if (i % ev_exits_len == 0):
                    topSZ = _SafeZones(
                        (self.margin / 2 + ev_exits_len, -int(self.margin/2)), (self.exit_size * 2, self.exit_size))
                    downSZ = _SafeZones((self.margin / 2 + ev_exits_len, self.path_len * self.num_of_pathes -int(self.margin/2)),\
                                    (self.exit_size * 2, self.exit_size))
                    self.exit_group.add(topSZ, downSZ)
                    self.exit_array.extend([topSZ, downSZ])

    def meters_to_pixels(self, meters):
        return int((meters*self.path_len)/2.55)

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
        _fire_coor = self.get_fire_coordinates() 

        
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


class Smoke(pg.sprite.Sprite):
    def __init__(self, r, alpha, coord, surface):
        pg.sprite.Sprite.__init__(self)
        self.r = int(r)
        self.image = pg.Surface( (self.r, self.r), flags=pg.SRCALPHA )
        self.rect = pg.Rect( (coord[0] - self.image.get_width() // 2, coord[1] - self.image.get_height() // 2 ), (self.r, self.r) )
        pg.draw.circle(self.image, (128, 128, 128, alpha), (int(self.r/2), int(self.r/2)), int(self.r/2))
        surface.blit(self.image, (coord[0] - self.image.get_width() // 2, coord[1] - self.image.get_height() // 2 ))

    def set_smoke_density(self, alpha):
        self.image.set_alpha(alpha)
    
    def get_smoke_density(self):
        return self.image.get_alpha()


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
    def __init__(self, path_len, car_margin, tunnel_len, num_of_pathes):
        pg.sprite.Sprite.__init__(self)
        self.path_len = path_len
        self.car_margin = car_margin
        self.tunnel_len = tunnel_len
        self.num_of_pathes = num_of_pathes
        car_sizes = [self.meters_to_pixels(3.3), self.meters_to_pixels(3.6), self.meters_to_pixels(4), \
            self.meters_to_pixels(3.3), self.meters_to_pixels(8)]
        self.size = (random.choice(car_sizes), self.path_len-self.car_margin) 
        self.image = pg.Surface(self.size)
        self.image.fill(c.RED)
        self.rect = pg.Rect((random.randrange(0, self.tunnel_len), \
                   path_len*random.randrange(0, self.num_of_pathes) + self.car_margin/2), self.size )
        
    def meters_to_pixels(self, meters):
        return int((meters*self.path_len)/2.55)

    def pixels_to_meters(self, pixels, path_len):
        return int((pixels*2.55)/self.path_len)

class _Person(pg.sprite.Sprite):
    def __init__(self, coord, cell_size):
        pg.sprite.Sprite.__init__(self)
        self.cell_size = cell_size
        self.image = pg.Surface((self.cell_size, self.cell_size))
        self.image.fill( (0, 255, 0) )
        self.coord = coord
        self.rect = pg.Rect(self.coord, (self.cell_size, self.cell_size))

        self.hp = 500
        self.close_exit = 0
        self.prev_step = ()
        
    def move(self):
        self.rect.centerx += 2 

    def display(self, screen):
        if(self.hp > 0):
            screen.blit(self.image, (self.rect[0], self.rect[1]))

    def get_hp(self):
        return self.hp

    def set_prev_step(self, ps):
        self.prev_step = ps

    def get_prev_step(self):
        return self.prev_step
    
    def decrease_hp(self, smoke_density):
        if smoke_density > 43:
            self.hp -= 3
        else:
            self.hp -= 1
        self.__hp_indicator()

    def __hp_indicator(self):
        if self.hp in range(500, 601):
            self.image.fill( (0, 255, 0) )
        elif self.hp in range(400, 501):
            self.image.fill( (128, 255, 0) )
        elif self.hp in range(300, 401):
            self.image.fill( (255, 255, 0) )
        elif self.hp in range(200, 301):
            self.image.fill( (255, 128, 0) )
        elif self.hp in range(100, 201):
            self.image.fill( (128, 64, 0) )
        else:
            self.image.fill( (128, 0, 0) )