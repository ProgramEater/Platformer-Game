import json

import pygame
import sys
from Level_Editor_modules.Level_Editor_Interface import Interface
from Level_Editor_modules.Board_class import Board


def setup():
    # loads everything from files
    # Params, textures and so on

    # resolution and textures
    resolution, extra, tiles = tuple(), {}, {}

    # params
    params = {
        "board_x_shift": 50,
        "board_y_shift": 50,
        "font_size": 30,
        "text_color": [255, 255, 255],
        "tile_choice_tile_size": 20,
        "tile_choice_columns_number": 8,
        "tile_choice_gap_size": 5,
        "button_w": 80,
        "button_h": 40,
        "button_gap_size": 5,
        "board_w": 20,
        "board_h": 20,
        "board_tile_size": 20,
        "board_lines_color": [255, 255, 255],
        "board_last_placed_color": [255, 255, 0],
        "default_color": [50, 50, 50]
    }

    # tile texture if proper texture doesn't exist
    not_found_texture = pygame.surface.Surface((1, 1))
    not_found_texture.fill((255, 0, 255))

    # resolution ------------------------------------------------------------------------
    with open('Level_Editor_modules/data/resolution.txt', mode='r') as f:
        try:
            x, y = [i.strip() for i in f.readline().split()]
            resolution = (int(x), int(y))
        except ValueError:
            print('Incorrect resolution! Check "Level_Editor_modules/data/resolution.txt"')
            resolution = 1200, 800

    # tile images (from .json) ----------------------------------------------------------
    with open('Level_Editor_modules/data/json_params/tiles_images.json', mode='r') as f:
        tiles_json = json.load(f)

    tiles = {}
    for key, val in tiles_json.items():
        try:
            tiles[key] = pygame.image.load(val)
        except FileNotFoundError:
            print(f"couldn't find texture for \"{key}\" tile, {val} doesn't exist")
            tiles[key] = not_found_texture

    # extra images ----------------------------------------------------------------------
    with open('Level_Editor_modules/data/json_params/extra_images.json', mode='r') as f:
        extra_json = json.load(f)

    extra = {}
    for key, val in extra_json.items():
        try:
            extra[key] = pygame.image.load(val)
        except FileNotFoundError:
            print(f"couldn't find texture for \"{key}\" element, {val} doesn't exist")
            extra[key] = not_found_texture

    # other params ----------------------------------------------------------------------
    with open('Level_Editor_modules/data/json_params/params.json', mode='r') as f:
        params_json = json.load(f)
        typ = ''
        for key, val in params.items():
            try:
                if isinstance(val, int):
                    params[key] = int(params_json[key])
                    typ = 'INTEGER'
                elif isinstance(val, list):
                    params[key] = tuple(params_json[key])
                    typ = 'LIST of 3 values (RGB)'
                    if len(tuple(params_json[key])) != 3:
                        raise ValueError
            except ValueError:
                print(f'Incorrect parameter - {key}, should be {typ}\n'
                      f'check Level_Editor_modules/data/json_params/params.json')

    return resolution, tiles, extra, params


def save_preferences():
    params["text_color"] = list(params["text_color"])
    params["board_w"] = board.w
    params["board_h"] = board.h
    params["board_tile_size"] = board.tile_size
    params["board_lines_color"] = list(params["board_lines_color"])
    params["board_last_placed_color"] = list(params["board_last_placed_color"])
    params["default_color"] = list(params["default_color"])
    with open('Level_Editor_modules/data/json_params/params.json', mode='w') as f:
        json.dump(params, f, indent=4)


if __name__ == '__main__':
    pygame.init()

    resolution, tile_images, extra_images, params = setup()

    # screen:
    screen = pygame.display.set_mode(resolution)

    font = pygame.font.SysFont('Arial', params['font_size'])

    clock = pygame.time.Clock()

    # setup
    board = Board(params['board_w'], params['board_h'], params['board_tile_size'], tile_images,
                  params['board_lines_color'], params['board_last_placed_color'], params['default_color'])
    interface = Interface(screen, board, params['board_x_shift'], params['board_y_shift'],
                          tile_images, extra_images, font, params['text_color'],
                          params['tile_choice_tile_size'], params['tile_choice_columns_number'],
                          params["tile_choice_gap_size"],
                          params["button_w"], params["button_h"], params["button_gap_size"], params['default_color'])
    i = 1
    while True:
        clock.tick(60)
        screen.fill(params['default_color'])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_preferences()
                pygame.quit()
                sys.exit()

        interface.update()
        screen.blit(interface.surface, (0, 0))
        pygame.display.flip()

