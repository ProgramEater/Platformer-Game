import pygame
import os
import csv


class Board:
    def __init__(self, w, h, tile_size, tiles_images, lines_color, last_placed_color, default_color, parent_surf):
        # size
        self.w, self.h = w, h
        self.tile_size = tile_size

        # board w * h size with borders (included in w*h)
        self.list = self.make_new_list()

        # board surface (draw on it, then blit on needed surface)
        self.surface = pygame.surface.Surface((w * tile_size, h * tile_size))

        self.display = parent_surf

        # list of images for every object name
        self.tiles_images = tiles_images
        self.lines_color = lines_color
        self.last_placed_color = last_placed_color
        self.default_color = default_color

        self.font = pygame.font.SysFont('arial', 50)

        # list indexes of the last placed tile, (-1, -1) if it should not be shown
        self.last_placed = (-1, -1)

        self.draw_board()

    def make_new_list(self):
        return [['#' for i in range(self.w)]] + [['#'] + [' ' for i in range(self.w - 2)] +
                                                 ['#'] for j in range(self.h - 2)] + [['#' for i in range(self.w)]]

    def draw_board(self):
        self.surface.fill(self.default_color)
        # drawing borders
        for i in range(self.w + 1):
            pygame.draw.line(self.surface, self.lines_color, (i * self.tile_size, 0),
                             (i * self.tile_size, self.h * self.tile_size))
        for i in range(self.h + 1):
            pygame.draw.line(self.surface, self.lines_color, (0, i * self.tile_size),
                             (self.w * self.tile_size, i * self.tile_size))
        # drawing tiles
        for y, line in enumerate(self.list):
            for x, elem in enumerate(line):
                if elem not in self.tiles_images.keys():
                    self.surface.blit(pygame.transform.scale(self.tiles_images['special'],
                                                             (self.tile_size - 2, self.tile_size - 2)),
                                      (x * self.tile_size + 1, y * self.tile_size + 1))
                else:
                    self.surface.blit(pygame.transform.scale(self.tiles_images[elem],
                                                             (self.tile_size - 2, self.tile_size - 2)),
                                      (x * self.tile_size + 1, y * self.tile_size + 1))

        # draw a border around last placed tile if possible
        if self.last_placed != (-1, -1):
            pygame.draw.rect(self.surface, self.last_placed_color, (self.last_placed[0] * self.tile_size + 1,
                                                                    self.last_placed[1] * self.tile_size + 1,
                                                                    self.tile_size - 2, self.tile_size - 2), 1)

    def mpos_to_index(self, pos, board_offset):
        x, y = pos
        x, y = ((x - board_offset[0]) // self.tile_size,
                (y - board_offset[1]) // self.tile_size)
        return x, y

    def tile_name_under_cursor(self, pos, board_offset):
        x, y = self.mpos_to_index(pos, board_offset)
        if -1 < x < self.w and -1 < y < self.h and self.list[y][x] not in ['', ' ']:
            return f'selected tile: "{self.list[y][x]}"   x: {x + 1} y: {self.h - y}'
        elif -1 < x < self.w and -1 < y < self.h and self.list[y][x] == ' ':
            return f'x: {x + 1} y: {self.h - y}'
        else:
            return ''

    def add_tile(self, x, y, tile_name):
        if 0 <= x < len(self.list[0]) and 0 <= y < len(self.list):

            # return if tile matches the one that is already here or we try to replace special for special
            if tile_name == 'special':
                if self.list[y][x] != ' ' and self.list[y][x] not in self.tiles_images.keys():
                    return

            if tile_name == self.list[y][x]:
                return

            # get the name if tile is special
            if tile_name == 'special':
                self.display.blit(self.font.render('open console (it opens with that app)', True, 'white'),
                                  (self.display.get_width() // 2 - 100, self.display.get_height() // 2 - 20))
                pygame.display.flip()
                # if tile name still hasn't been changed (i will change it in main code
                tile_name = input('What tile name do you want for this tile?\n')

            self.last_placed = x, y

            self.list[y][x] = tile_name
            self.draw_board()

    def erase(self, x, y):
        if 0 <= x < len(self.list[0]) and 0 <= y < len(self.list):
            self.last_placed = (-1, -1)

            self.list[y][x] = ' '
            self.draw_board()

    def save(self, name):
        # if file exists, ask permission to save
        if '.csv' == name[-4:]:
            if os.path.exists(name):
                print('\nThis file already exists\nReplace it?\nPrint Y to accept, new path to save with other path '
                      'or anything else to cancel')
                response = input()
                # if Y => replace file, else cancel
                if response == 'Y':
                    pass
                elif len(response) >= 4 and response[-4:] == '.csv':
                    self.save(response)
                    return
                else:
                    print('cancelling...\n')
                    return
            # if file doesn't exist, we save file
            with open(name, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                for i in self.list:
                    writer.writerow(i)
        else:
            print('File should be in --> .csv format <--\n')
            self.save(input())

    def open(self, name):
        if name == 'cancel':
            return
        if os.path.exists(name):
            if '.csv' == name[-4:]:
                with open(name, encoding='utf-8-sig', mode='r') as f:
                    reader = csv.reader(f, delimiter=';')
                    self.list = [i for i in reader]
                    self.w, self.h = len(self.list[0]), len(self.list)
                    self.surface = pygame.surface.Surface((self.w * self.tile_size, self.h * self.tile_size))
                self.draw_board()
            else:
                print('please, write a path to --> .csv file <--\n')
                self.open(input())
        else:
            print('the file doesn\'t exist, write "cancel" to cancel or new path\n')
            self.open(input())

    def change_tile_size(self, new_ts):
        new_t_size = new_ts
        try:
            if int(new_t_size) <= 0:
                raise ValueError
            self.tile_size = int(new_t_size)
            self.surface = pygame.surface.Surface((self.w * self.tile_size, self.h * self.tile_size))
            self.draw_board()
        except ValueError as e:
            return str(e)

    def change_size(self, first, show_incorrect_input=True):
        if first:
            print('\nWrite board width and height (cells)\n20 30\n will create board 20 cells wide '
                  "and 30 cells in height (cancel to cancel)\n Remember! All you've drawn will be deleted!")
        elif show_incorrect_input:
            print('Incorrect input\nTry:\n  5 3\n Type cancel to cancel')

        new_size = input().split()

        if new_size[0] == 'cancel':
            return

        if len(new_size) == 2:
            try:
                if not(1 <= int(new_size[0]) and 1 <= int(new_size[1])):
                    print('width and height should be >= 1\n')
                    self.change_size(False, show_incorrect_input=False)
                    return
                self.w, self.h = int(new_size[0]), int(new_size[1])
                self.surface = pygame.surface.Surface((self.w * self.tile_size, self.h * self.tile_size))
                self.list = self.make_new_list()
                self.draw_board()
            except ValueError:
                self.change_size(False)
        else:
            self.change_size(False)
