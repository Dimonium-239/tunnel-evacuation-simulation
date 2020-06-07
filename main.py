import pygame as pg
import colors as c
from tunnel import *
from observer import Observer
from camera import Camera, camera_configure
from start_menu import *

from settings import *


class Screen:
    def __init__(self, settings_tuple):
        """
        Initialize simulation area.
    
        """
        self.screen_len_new = DISPLAY
        self.screen = pg.display.set_mode(DISPLAY, pg.RESIZABLE)
        pg.display.set_caption("Fire in tunnel")


        self.bg = pg.Surface(DISPLAY)
        self.bg.fill(c.BLUE)
        self.observer = Observer(0, 2)
        self.tunnel = Tunnel(settings_tuple)
        self.camera = Camera(camera_configure, settings_tuple[1] + 60, WIN_HEIGHT)
        self.settings_tuple = settings_tuple

    def draw_on_screen(self, r, left, right):
        self.screen.blit(self.bg, (0, 0))
        self.camera.update(self.observer, self.screen_len_new)
        self.tunnel.blit_tunnel(r ,self.screen, self.camera)
        #self.tunnel.blit_smoke(self.screen, self.camera)
        self.observer.update(left, right, self.screen_len_new, self.settings_tuple[1], self.settings_tuple[6])


class Simulation:
    def __init__(self, settings_tuple):
        pg.init()
        self.clock = pg.time.Clock()
        self.font = pg.font.Font('freesansbold.ttf', 16) 
        self.left = False 
        self.right = False

        self.fire_radius = 1
        self.time = 0
        self.time2 = 0
        self.screen = Screen(settings_tuple)
        self.started = False    
        self.deadth_counter = 0
        self.rescue_people_counter = 0

    def event_handler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    self.left = True
                if event.key == pg.K_RIGHT:
                    self.right = True
                if event.key == pg.K_RETURN:
                    self.started = not self.started
                if event.key == pg.K_f:
                    self.screen.observer.rect.x = self.screen.tunnel.get_burning_car().rect.x
                if event.key == pg.K_HOME:
                    self.screen.observer.rect.x = MARGIN
                if event.key == pg.K_END:
                    self.screen.observer.rect.x = TUNNEL_LEN - MARGIN
            

            if event.type == pg.KEYUP: 
                if event.key == pg.K_RIGHT:
                    self.right = False
                if event.key == pg.K_LEFT:
                    self.left = False

            if event.type == pg.VIDEORESIZE:
                win_len_new = (event.w, event.h)
                self.screen.screen = pg.display.set_mode(win_len_new, pg.RESIZABLE)
                self.screen.bg = pg.Surface(win_len_new)
                self.screen.bg.fill(c.BLUE)
                self.screen.screen_len_new = win_len_new
            
        return False

    def kill_people(self):
        people_in_smoke_dict = pg.sprite.groupcollide(self.screen.tunnel.people_group, self.screen.tunnel.smoke_group, False, False)
        if list(people_in_smoke_dict.keys()):
            for person in list(people_in_smoke_dict.keys()):
                person.decrease_hp(list(people_in_smoke_dict.get(person))[-1].get_smoke_density())
                if(person.get_hp() < 0):
                    self.deadth_counter += 1
                    person.kill()

    def rescue_people(self):
        if(pg.sprite.groupcollide(self.screen.tunnel.people_group, self.screen.tunnel.exit_group, True, False)):
            self.rescue_people_counter += 1

    def init_text(self, text, i=0):
        text_ = self.font.render(text, True, c.WHITE) 
        textRect = text_.get_rect()  
        textRect.center = (30*3, 30+32*i)
        self.screen.screen.blit(text_, textRect) 
    

    def run(self):
        while not self.event_handler():
            self.screen.draw_on_screen(self.fire_radius, self.left, self.right)
            self.clock.tick(250)            
            if(self.started):
                self.time = self.time + self.clock.get_time()
            
                self.time2 = self.time2 + self.clock.get_time()
                if self.time2 >= 450:
                    self.screen.tunnel.move_person()
                    self.time2 = 0
                    self.fire_radius += 4
            self.kill_people()
            self.rescue_people()
            self.init_text('All people: ' + str(len(self.screen.tunnel.people_array)), 0)
            self.init_text('Evacuated people: ' + str(self.rescue_people_counter), 1)
            self.init_text('Dead people: ' + str(self.deadth_counter), 2)

            pg.display.update()
        pg.quit()

if __name__ == "__main__":
    aa = Menu()
    game = Simulation(aa.get_settings())
    game.run()
