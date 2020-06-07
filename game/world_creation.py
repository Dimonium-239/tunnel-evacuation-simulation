import pygame
import pygame.locals

CYCLE_NUMBER = 1


class Cell:
    """
    Single cell representing world element.
    """

    def __init__(self, is_fire=False, is_smoke=False, is_person=False, is_wall=False, is_car=False, is_empty=True):
        self.is_empty = is_empty
        self.is_fire = is_fire
        self.is_smoke = is_smoke
        self.is_person = is_person
        self.is_wall = is_wall
        self.is_car = is_car

    def put_empty_here(self):
        self.is_empty = True
        self.is_fire = False
        self.is_smoke = False
        self.is_person = False
        self.is_wall = False
        self.is_car = False

    def put_fire_here(self):
        if self.is_car:
            self.is_empty = False
            self.is_fire = True

    def put_smoke_here(self):
        if not self.is_wall:
            self.is_empty = False
            self.is_smoke = True

    def put_person_here(self):
        if self.is_empty:
            self.is_empty = False
            self.is_person = True

    def remove_person(self):
        if self.is_person:
            self.put_empty_here()

    def put_wall_here(self):
        self.is_empty = False
        self.is_wall = True

    def put_car_here(self):
        if self.is_empty:
            self.is_empty = False
            self.is_person = False
            self.is_car = True


class World:
    """
    World with all of its elements.
    """

    def __init__(self, width, height, cell_size=10):
        """
        Create settings of the simulation world.

        :param width: cells number
        :param height: cells number
        :param cell_size: cell size in pixels
        """
        self.box_size = cell_size
        self.height = height
        self.width = width
        self.generation = self.reset_world()

    def reset_world(self):
        """
        Create and return restarted tunnel.
        """

        return [[Cell(is_wall=True) if (y == 0 or y == self.height - 1) else Cell() for y in range(self.height)] for x
                in range(self.width)]

    def draw_on_static(self, surface):
        """
        Draw static element of the world (walls, entries).
        """

        for x, y in self.find_wall_cells():
            size = (self.box_size, self.box_size)
            position = (x * self.box_size, y * self.box_size)
            color = (55, 6, 23)
            thickness = 0
            pygame.draw.rect(surface, color, pygame.locals.Rect(position, size), thickness)

    def find_wall_cells(self):
        for x in range(len(self.generation)):
            column = self.generation[x]
            for y in range(len(column)):
                if column[y].is_wall:
                    yield x, y

    def handle_mouse(self):
        """
        Create people in left-click cells and cars in right-click cells.
        """
        buttons = pygame.mouse.get_pressed()
        if not any(buttons):
            return

        person = True if buttons[0] else False
        fire = True if buttons[1] else False
        car = True if buttons[2] else False

        x, y = pygame.mouse.get_pos()
        x /= self.box_size
        y /= self.box_size

        if person:
            self.generation[int(x)][int(y)].put_person_here()
        elif car:
            try:
                for x_car in [x, x + 1, x + 2, x + 3]:
                    for y_car in [y - 1, y, y + 1]:
                        self.generation[int(x_car)][int(y_car)].put_car_here()
            except:
                pass
        elif fire:
            self.generation[int(x)][int(y)].put_fire_here()

    def draw_on(self, surface):
        """
        Draw cells of people, cars, fire and smoke on the board.
        """
        for x, y in self.find_person_cells():
            radius = self.box_size // 2
            position = (x * self.box_size + radius, y * self.box_size + radius)
            color = (255, 255, 255)
            pygame.draw.circle(surface, color, position, radius)

        for x, y in self.find_empty_cells():
            size = (self.box_size, self.box_size)
            position = (x * self.box_size, y * self.box_size)
            color = (0, 0, 0)
            thickness = 0
            pygame.draw.rect(surface, color, pygame.locals.Rect(position, size), thickness)

        for x, y in self.find_car_cells():
            size = (self.box_size, self.box_size)
            position = (x * self.box_size, y * self.box_size)
            color = (255, 186, 8)
            thickness = 0
            pygame.draw.rect(surface, color, pygame.locals.Rect(position, size), thickness)

        for x, y in self.find_fire_cells():
            radius = self.box_size // 2
            position = (x * self.box_size + radius, y * self.box_size + radius)
            color = (208, 0, 0)
            pygame.draw.circle(surface, color, position, radius)

        for x, y in self.find_smoke_cells():
            size = (self.box_size, self.box_size)
            position = (x * self.box_size, y * self.box_size)
            color = (153, 153, 153)

            smoke_surface = pygame.Surface(size)
            smoke_surface.set_alpha(150)
            smoke_surface.fill(color)
            surface.blit(smoke_surface, position)

    def find_person_cells(self):
        """
        Function generating coordinates of people.
        """
        for x in range(len(self.generation)):
            column = self.generation[x]
            for y in range(len(column)):
                if column[y].is_person:
                    yield x, y

    def find_car_cells(self):
        """
        Function generating coordinates of cars.
        """
        for x in range(len(self.generation)):
            column = self.generation[x]
            for y in range(len(column)):
                if column[y].is_car:
                    yield x, y

    def find_fire_cells(self):
        """
        Function generating coordinates of fire.
        """
        for x in range(len(self.generation)):
            column = self.generation[x]
            for y in range(len(column)):
                if column[y].is_fire:
                    yield x, y

    def find_smoke_cells(self):
        """
        Function generating coordinates of fire.
        """
        for x in range(len(self.generation)):
            column = self.generation[x]
            for y in range(len(column)):
                if column[y].is_smoke:
                    yield x, y

    def find_empty_cells(self):
        """
        Function generating coordinates of empty cells.
        """
        for x in range(len(self.generation)):
            column = self.generation[x]
            for y in range(len(column)):
                if column[y].is_empty and not column[y].is_wall:
                    yield x, y

    def find_neighbours_to_smoke(self, x, y):
        """
        Find coordinates of every neighbour. In each cycle the area radius is one cell bigger.
        :param x:  item x
        :param y:  item y
        :return: neighbours coordinates
        """

        global CYCLE_NUMBER
        CYCLE_NUMBER = CYCLE_NUMBER + 0.2
        INT_CYCLE_NUMBER = int(CYCLE_NUMBER)

        return [(nx, ny) for nx in range(x - INT_CYCLE_NUMBER, x + INT_CYCLE_NUMBER + 1) for ny in
                range(y - INT_CYCLE_NUMBER, y + INT_CYCLE_NUMBER + 1) if nx > 0 and ny > 0]

    def generate_smoke(self):
        """
        Smoke generation.
        """
        for x, y in self.find_fire_cells():
            for (x_to_smoke, y_to_smoke) in self.find_neighbours_to_smoke(int(x), int(y)):
                try:
                    self.generation[int(x_to_smoke)][int(y_to_smoke)].put_smoke_here()
                except:
                    continue

    def evacuate_people(self):
        """
        People evacuation from the smoked tunnel.
        Person attempts to go to the nearest exit. If it is impossible - go up, then - down, then - to the another exit.
        """
        for x, y in self.find_person_cells():
            try:
                if x < self.width / 2:
                    if self.generation[x - 1][y].is_empty or self.generation[x - 1][y].is_smoke:
                        self.generation[x][y].remove_person()
                        self.generation[x - 1][y].put_person_here()
                    elif self.generation[x][y - 1].is_empty or self.generation[x][y - 1].is_smoke:
                        self.generation[x][y].remove_person()
                        self.generation[x][y - 1].put_person_here()
                    elif self.generation[x][y + 1].is_empty or self.generation[x][y + 1].is_smoke:
                        self.generation[x][y].remove_person()
                        self.generation[x][y + 1].put_person_here()

                elif x == self.width - 1:
                    self.generation[x][y].remove_person()

                if x > self.width / 2:
                    if self.generation[x + 1][y].is_empty or self.generation[x + 1][y].is_smoke:
                        self.generation[x][y].remove_person()
                        self.generation[x + 1][y].put_person_here()
                    elif self.generation[x][y - 1].is_empty or self.generation[x][y - 1].is_smoke:
                        self.generation[x][y].remove_person()
                        self.generation[x][y - 1].put_person_here()
                    elif self.generation[x][y + 1].is_empty or self.generation[x][y + 1].is_smoke:
                        self.generation[x][y].remove_person()
                        self.generation[x][y + 1].put_person_here()
                    elif self.generation[x - 1][y].is_empty or self.generation[x - 1][y].is_smoke:
                        self.generation[x][y].remove_person()
                        self.generation[x - 1][y].put_person_here()
            except:
                continue
