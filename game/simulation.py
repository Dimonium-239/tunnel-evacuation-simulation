import pygame
import pygame.locals

from world_creation import World


class Board:
    """
    Simulation area. It's responsible for drawing simulation background.
    """

    def __init__(self, width, height):
        """
        Initialize simulation area.

        """
        self.surface = pygame.display.set_mode((width, height), 0, 32, pygame.SRCALPHA)
        pygame.display.set_caption('Game of life')

    def draw_static_elements(self, *args):
        """
        Draw static elements (background, walls, entries) in the simulation area.
        """
        background = (0, 0, 0)
        self.surface.fill(background)
        for drawable in args:
            drawable.draw_on_static(self.surface)

        pygame.display.update()

    def draw_editable_elements(self, *args):
        """
        Draw dynamic elements (people, cars, fire source) in the simulation area.

        :param args: object list to draw
        """

        for drawable in args:
            drawable.draw_on(self.surface)

        pygame.display.update()


class SmokedTunnelSimulation:
    """
    Main class. It simulates evacuation from the smoked tunnel.
    """

    def __init__(self, width, height, cell_size=10):
        """
        Simulations parameters setting.
        :param cell_size: cell size in pixels
        """
        pygame.init()
        self.board = Board(width * cell_size, height * cell_size)
        self.fps_clock = pygame.time.Clock()
        self.population = World(width, height, cell_size)

    def run(self):
        """
        Simulation main loop.
        """

        self.board.draw_static_elements(self.population)
        while not self.handle_events():
            self.board.draw_editable_elements(
                self.population,
            )
            if getattr(self, "started", None):
                self.population.generate_smoke()
                self.population.evacuate_people()
                self.fps_clock.tick(15)


    def handle_events(self):
        """
        Events service. In this case only quit.
        :return True if quit is active
        """
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                return True

            from pygame.locals import MOUSEMOTION, MOUSEBUTTONDOWN
            if event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN:
                self.population.handle_mouse()

            from pygame.locals import KEYDOWN, K_RETURN
            if event.type == KEYDOWN and event.key == K_RETURN:
                self.started = True


if __name__ == "__main__":
    game = SmokedTunnelSimulation(120, 40)
    game.run()
