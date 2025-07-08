import pygame
import sys
import csv


class Board:
    def __init__(self, w, h, t_size, x_shift, y_shift):
        self.w, self.h = w, h
        self.tile_size = t_size
        self.x_shift, self.y_shift = x_shift, y_shift
        self.list = [[' ' for i in range(self.w)] for j in range(self.h)]

    def draw_board(self):
        # drawing borders
        for i in range(self.w + 1):
            pygame.draw.line(screen, 'white', (self.x_shift + i * self.tile_size, self.y_shift),
                             (self.x_shift + i * self.tile_size, self.y_shift + self.h * self.tile_size))
        for i in range(self.h + 1):
            pygame.draw.line(screen, 'white', (self.x_shift, self.y_shift + i * self.tile_size),
                             (self.x_shift + self.w * self.tile_size, self.y_shift + i * self.tile_size))
        # drawing tiles
        for y, line in enumerate(self.list):
            for x, elem in enumerate(line):
                if elem not in tiles.keys():
                    screen.blit(pygame.transform.scale(tiles['special'], (self.tile_size - 2, self.tile_size - 2)),
                                (self.x_shift + x * self.tile_size + 1, self.y_shift + y * self.tile_size + 1))
                else:
                    screen.blit(pygame.transform.scale(tiles[elem], (self.tile_size - 2, self.tile_size - 2)),
                                (self.x_shift + x * self.tile_size + 1, self.y_shift + y * self.tile_size + 1))

    def add_tile(self, x, y):
        # getting indexes of the tile where click happened and updating image
        if -1 < x < self.w and -1 < y < self.h:
            if current_tile_name == 'special':
                self.list[y][x] = input()
            else:
                self.list[y][x] = current_tile_name
            self.draw_board()

            global last_placed_indexes
            last_placed_indexes = x, y

    def erase(self, x, y):
        if -1 < x < self.w and -1 < y < self.h:
            self.list[y][x] = ' '
            self.draw_board()

        global last_placed_indexes
        last_placed_indexes = (-1, -1)

    def save(self, name):
        with open(name, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            for i in self.list:
                writer.writerow(i)

    def open(self, name):
        if name == 'cancel':
            return
        try:
            with open(name, encoding='utf-8-sig', mode='r') as f:
                self.list = []
                reader = csv.reader(f, delimiter=';')
                for i in reader:
                    self.list.append(i)
            self.draw_board()
        except FileNotFoundError:
            print('no such file (print "cancel" to cancel)')
            self.open(input())


def mouse_pos_to_index(x, y):
    x -= x_shift
    x //= t_size
    y -= y_shift
    y //= t_size
    return x, y


def draw_last_placed_rect(last_x, last_y):
    if last_x != last_y != -1:
        x = x_shift + last_x * t_size + 1
        y = y_shift + last_y * t_size + 1
        pygame.draw.rect(screen, 'yellow', (x, y, t_size - 2, t_size - 2), 1)


def tile_name_under_cursor(pos):
    x, y = mouse_pos_to_index(*pos)
    if -1 < x < w and -1 < y < h:
        return font.render(board.list[y][x], False, 'white')
    else:
        return default_surf


# this function makes tile sprites appear so that you can choose tile by clicking on it
def set_block_choise_fragment(x, y, tile_size, n_x, gap_size):
    i = 0
    y += tile_size + gap_size
    for key, val in tiles.items():
        if key != ' ':
            a = pygame.sprite.Sprite(tile_sprite_group)

            # tile symbol
            a.sym = key
            # sprite surface
            a.image = pygame.surface.Surface((tile_size * 2, 2 * tile_size))
            a.image.fill(default_color, (1, 1, a.image.get_width() - 2, a.image.get_height() - 2))

            # tile image
            a.image.blit(pygame.transform.scale(val, (tile_size - 2, tile_size - 2)), (1, tile_size + 1))

            # text
            text = font.render(key, False, 'white')
            coef = tile_size / text.get_height()

            a.image.blit(pygame.transform.scale(text, (min(text.get_width() * coef, a.image.get_width() - 5), tile_size)),
                         (2, 1))

            # rect
            a.rect = a.image.get_rect()
            a.rect.x, a.rect.y = x + (tile_size * 2 + gap_size) * (i % n_x), y + (tile_size * 2 + gap_size) * (i // n_x)

            i += 1


# images and surfaces
if True:
    default_color = (50, 50, 50)

    default_surf = pygame.surface.Surface((1, 1))
    default_surf.fill(default_color)

    cyan_surf = pygame.surface.Surface((1, 1))
    cyan_surf.fill('cyan')

    tiles = {'#': pygame.surface.Surface((1, 1)),
             's': pygame.image.load('data/simple_textures/spike.png'),
             '*': pygame.image.load('data/simple_textures/plat.png'),
             ' ': default_surf,
             'special': cyan_surf}

if __name__ == '__main__':
    pygame.init()

    # screen:
    size = width, height = 1200, 800
    screen = pygame.display.set_mode(size)

    # Font for text
    font = pygame.font.SysFont('Arial', 40)

    # sprites
    tile_sprite_group = pygame.sprite.Group()

    buttons_sprite_group = pygame.sprite.Group()
    # buttons
    if True:
        save_button = pygame.sprite.Sprite(buttons_sprite_group)
        save_button.image = pygame.transform.scale(pygame.image.load('data/simple_textures/save_button.png'), (80, 40))
        save_button.rect = pygame.rect.Rect(50, 5, *save_button.image.get_size())

        open_button = pygame.sprite.Sprite(buttons_sprite_group)
        open_button.image = pygame.transform.scale(pygame.image.load('data/simple_textures/open_button.png'), (80, 40))
        open_button.rect = pygame.rect.Rect(140, 5, *open_button.image.get_size())

    # current and last parameters ---------------------
    current_tile_name = '#'

    last_placed_indexes = (-1, -1)
    prev_x, prev_y, prev_m_button = -1, -1, 0

    object_name_coords = 250, 5
    # -------------------------------------------------

    # Board parameters
    params = (w, h, t_size, x_shift, y_shift) = (31, 15, 15, 20, 50)

    set_block_choise_fragment(x_shift + w * t_size + 20, y_shift, 20, 2, 5)
    board = Board(*params)

    screen.fill(default_color)
    board.draw_board()
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            # if on tile
            for i in tile_sprite_group:
                if i.rect.collidepoint(*mouse_pos):
                    # tile sprites have variable sym (symbol of tile im csv level)
                    current_tile_name = i.sym
                    prev_m_button = 0

            # if on button
            if save_button.rect.collidepoint(*mouse_pos):
                board.save(input())
            elif open_button.rect.collidepoint(*mouse_pos):
                board.open(input())

            # if on board
            ind = mouse_pos_to_index(*mouse_pos)
            if ind != (prev_x, prev_y) or prev_m_button != 0:
                (prev_x, prev_y) = ind
                board.add_tile(*ind)
                pygame.display.flip()
        elif pygame.mouse.get_pressed()[2]:
            ind = mouse_pos_to_index(*pygame.mouse.get_pos())
            if ind != (prev_x, prev_y) or prev_m_button != 2:
                (prev_x, prev_y) = ind
                board.erase(*ind)
                prev_m_button = 1
        else:
            # show last placed tile while not drawing
            draw_last_placed_rect(*last_placed_indexes)

        # show name of tile which is under cursor
        screen.blit(tile_name_under_cursor(pygame.mouse.get_pos()), object_name_coords)
        # screen.blit(edit.surface, edit.pos)
        tile_sprite_group.draw(screen)
        buttons_sprite_group.draw(screen)
        pygame.display.flip()
