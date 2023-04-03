import pygame
import os
import csv


class Board:
    def __init__(self, w, h, tile_size, tiles_images, lines_color, last_placed_color):
        # size
        self.w, self.h = w, h
        self.tile_size = tile_size

        # board w * h size with borders (included in w*h)
        self.list = [['#' for i in range(self.w)]] + \
                    [['#'] + [' ' for i in range(self.w - 2)] + ['#'] for j in range(self.h - 2)] + \
                    [['#' for i in range(self.w)]]

        # board surface (draw on it, then blit on needed surface)
        self.surface = pygame.surface.Surface((w * tile_size, h * tile_size))

        # list of images for every object name
        self.tiles_images = tiles_images
        self.lines_color = lines_color
        self.last_placed_color = last_placed_color

        # list indexes of the last placed tile, (-1, -1) if it should not be shown
        self.last_placed = (-1, -1)

        self.draw_board()

    def draw_board(self):
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

    def add_tile(self, x, y, tile_name):
        self.last_placed = x, y

        self.list[y][x] = tile_name
        self.draw_board()

    def erase(self, x, y):
        self.last_placed = (-1, -1)

        self.list[y][x] = ' '
        self.draw_board()

    def save(self, name):
        # if file exists, ask permission to save
        if os.path.exists(name):
            print('This file already exists\nReplace it?\nPrint Y to accept, new path to save with other path '
                  'or anything else to cancel\n')
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

    def open(self, name):
        if name == 'cancel':
            return
        try:
            with open(name, encoding='utf-8-sig', mode='r') as f:
                reader = csv.reader(f, delimiter=';')
                self.list = [i for i in reader]
                self.w, self.h = len(self.list[0]), len(self.list)
                self.surface = pygame.surface.Surface((self.w * self.tile_size, self.h * self.tile_size))
            self.draw_board()
        except FileNotFoundError:
            print('no such file (print "cancel" to cancel)')
            self.open(input())

    def change_tile_size(self, first):
        if first:
            print('Write new tile size, please\n')
        else:
            print('Please write integer\n')
        new_t_size = input()
        try:
            self.tile_size = int(new_t_size)
            self.draw_board()
        except ValueError:
            self.change_tile_size(False)
