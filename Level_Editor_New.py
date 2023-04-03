import pygame
import sys
from Level_Editor_modules.Level_Editor_Interface import Interface
from Level_Editor_modules.Board_class import Board

if __name__ == '__main__':
    pygame.init()

    # screen:
    size = width, height = 1400, 900
    screen = pygame.display.set_mode(size)

    # decorations
    if True:
        default_color = (50, 50, 50)

        default_surf = pygame.surface.Surface((1, 1))
        default_surf.fill(default_color)

        cyan_surf = pygame.surface.Surface((1, 1))
        cyan_surf.fill('cyan')

        extra_images = {'default_color': (50, 50, 50),
                        'default_surf': default_surf,
                        'cyan_surf': cyan_surf,
                        'save_button': pygame.image.load('data/simple_textures/save_button.png'),
                        'open_button': pygame.image.load('data/simple_textures/open_button.png'),
                        'change_size_button': pygame.image.load('data/simple_textures/change_size_button.png')}

    tiles_images = {'#': pygame.surface.Surface((1, 1)),
                    's': pygame.image.load('data/simple_textures/spike.png'),
                    '*': pygame.image.load('data/simple_textures/plat.png'),
                    ' ': default_surf,
                    'special': cyan_surf}

    font = pygame.font.SysFont('Arial', 30)

    clock = pygame.time.Clock()

    # setup
    board = Board(30, 30, 20, tiles_images, (100, 100, 100), 'yellow')
    interface = Interface(board, 50, 50, tiles_images, extra_images, font, 'white', 20, 8, 5, 80, 40, 5)
    i = 1
    while True:
        clock.tick(60)
        screen.fill(default_color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        interface.update()
        screen.blit(interface.surface, (0, 0))
        pygame.display.flip()