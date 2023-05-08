import json

import pygame

import sys
from Level_Editor_modules.Level_Editor_Interface import Interface
from Level_Editor_modules.Board_class import Board


def setup():
    # loads everything from files
    # Params, textures and so on

    # resolution and textures
    extra, tiles = {}, {}

    # params
    params = {
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
        "board_lines_color": [255, 255, 255],
        "board_last_placed_color": [255, 255, 0],
        "default_color": [50, 50, 50]
    }

    # tile texture if proper texture doesn't exist
    not_found_texture = pygame.surface.Surface((1, 1))
    not_found_texture.fill((255, 0, 255))

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

    return tiles, extra, params


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

    tile_images, extra_images, params = setup()

    # resolution again
    resolution = 1200, 900

    # screen:
    screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)

    font = pygame.font.SysFont('Arial', params['font_size'])

    clock = pygame.time.Clock()

    # setup
    board = Board(params['board_w'], params['board_h'], 10, tile_images,
                  params['board_lines_color'], params['board_last_placed_color'], params['default_color'], screen)
    interface = Interface(screen, board, 10, 10,
                          tile_images, extra_images, font, params['text_color'],
                          params['tile_choice_tile_size'], params['tile_choice_columns_number'],
                          params["tile_choice_gap_size"],
                          params["button_w"], params["button_h"], params["button_gap_size"], params['default_color'])

    # board coordinates
    board_x, board_y = 30, 100
    last_x, last_y = -1, -1
    holding = False

    clock.tick(60)

    while True:
        # mouse
        pos = pygame.mouse.get_pos()
        m_keys = pygame.mouse.get_pressed()

        if not holding:
            last_x, last_y = pos

        screen.fill(params['default_color'])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_preferences()
                pygame.quit()
                sys.exit()

            # move board
            m_keys = pygame.mouse.get_pressed()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if m_keys[1]:
                    holding = True

            elif event.type == pygame.MOUSEBUTTONUP and holding:
                holding = False
                board_x, board_y = (board_x + pos[0] - last_x,
                                    board_y + pos[1] - last_y)
                interface.board_x_shift, interface.board_y_shift = board_x, board_y

            # resize board tiles
            if event.type == pygame.MOUSEWHEEL:
                new_ts = min(board.tile_size - 1, int(board.tile_size * 0.95)) if event.y < 0 \
                    else max(board.tile_size + 1, int(board.tile_size * 1.05))
                board.change_tile_size(new_ts)

            # window resize
            if event.type == pygame.VIDEORESIZE:
                # There's some code to add back window content here.
                surface = pygame.display.set_mode((event.w, event.h),
                                                  pygame.RESIZABLE)

        # draw or erase tiles on the board
        if m_keys[0]:
            board.add_tile(*board.mpos_to_index(pos, (board_x, board_y)), interface.current_tile)
        elif m_keys[2]:
            board.erase(*board.mpos_to_index(pos, (board_x, board_y)))

        interface.update()

        screen.blit(board.surface, (board_x + pos[0] - last_x, board_y + pos[1] - last_y))
        screen.blit(interface.surface, (0, 0))

        # draw selected tile name
        tile_name = board.tile_name_under_cursor(pos, (board_x, board_y))
        if tile_name:
            sel_tile = font.render(tile_name, True, params['text_color'])
            back_rect = pygame.rect.Rect(5, interface.surface.get_height() + 10,
                                         sel_tile.get_width() + 20, sel_tile.get_height() + 20)
            pygame.draw.rect(screen, params['default_color'], back_rect)
            pygame.draw.rect(screen, 'black', back_rect, 2)
            screen.blit(sel_tile, (back_rect.x + 10, back_rect.y + 10))

        pygame.display.flip()

