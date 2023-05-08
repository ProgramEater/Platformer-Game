import math

import pygame


class Interface:
    def __init__(self, window_surface, board, off_x, off_y, tiles_images_dict, extra_images, font,
                 text_color, tile_choice_tile_size, tile_choice_columns_number, tile_choice_gap_size,
                 button_w, button_h, button_gap_size, default_color):
        # Board and board params
        self.window_surface = window_surface
        self.board = board

        # current tile
        self.current_tile = '#'

        # button press cooldown
        self.button_press_cd = 60
        self.time_until_buttons_enabled = 0

        # decoration--------------------------------------------------------------------------
        self.extra_images = extra_images
        self.tiles_images_dict = tiles_images_dict
        self.font = font
        self.text_color = text_color
        self.default_color = default_color
        # ------------------------------------------------------------------------------------

        # buttons setup
        all_buttons_width = button_w * 2.5 + button_gap_size * 2

        self.buttons_sprite_group = pygame.sprite.Group()
        # buttons
        if True:
            self.save_button = pygame.sprite.Sprite(self.buttons_sprite_group)
            self.save_button.image = pygame.transform.scale(self.extra_images['save_button'], (button_w, button_h))
            self.save_button.rect = pygame.rect.Rect(off_x, off_y, *self.save_button.image.get_size())

            self.open_button = pygame.sprite.Sprite(self.buttons_sprite_group)
            self.open_button.image = pygame.transform.scale(self.extra_images['open_button'], (button_w, button_h))
            self.open_button.rect = pygame.rect.Rect(off_x + button_w + button_gap_size, off_y,
                                                     *self.open_button.image.get_size())

            self.change_size_button = pygame.sprite.Sprite(self.buttons_sprite_group)
            self.change_size_button.image = pygame.transform.scale(self.extra_images['change_size_button'],
                                                                   (button_w // 2, button_h))
            self.change_size_button.rect = pygame.rect.Rect(off_x + 2 * button_w + 2 * button_gap_size, off_y,
                                                            *self.change_size_button.image.get_size())

        # tile choice setup
        self.tile_sprite_group = pygame.sprite.Group()
        if True:
            line_num = math.ceil((len(tiles_images_dict.keys()) - 1) / tile_choice_columns_number)

            self.set_tile_choice_fragment(off_x + all_buttons_width + tile_choice_gap_size,
                                          off_y, tile_choice_tile_size,
                                          tile_choice_columns_number,
                                          tile_choice_gap_size)

            # whole tile choice area size
            all_tile_choice_width = min(len(self.tile_sprite_group), tile_choice_columns_number) * \
                                       (tile_choice_tile_size * 2 + tile_choice_gap_size)
            all_tile_choice_height = line_num * (tile_choice_tile_size * 2 + tile_choice_gap_size)

        # interface surface
        self.surface = pygame.surface.Surface((2 * off_x + all_buttons_width + all_tile_choice_width,
                                               max(all_tile_choice_height, button_h) + 2 * off_y + 20))
        self.draw()

    def draw(self):
        self.surface.fill(self.default_color)
        self.tile_sprite_group.draw(self.surface)
        self.buttons_sprite_group.draw(self.surface)

        pygame.draw.rect(self.surface, 'black', self.surface.get_rect(), 2)

    def update(self):
        self.time_until_buttons_enabled = max(self.time_until_buttons_enabled - 1, 0)
        m_pos = pygame.mouse.get_pos()
        m_keys = pygame.mouse.get_pressed()

        # Left mouse button is clicked
        if m_keys[0]:
            # if sprite from tile choice is clicked
            for sprite in self.tile_sprite_group:
                if sprite.rect.collidepoint(*m_pos):
                    # if clicked on sprite from tile choice, current_tile = sprite symbol.
                    # Only tile sprites have "sym" (sprite symbol which defines it in csv table)
                    self.current_tile = sprite.sym

            # if button is clicked (if we didn't press any buttons for some time (cooldown time))
            if not self.time_until_buttons_enabled:
                if self.save_button.rect.collidepoint(*m_pos):
                    # set button cd
                    self.time_until_buttons_enabled = self.button_press_cd

                    self.wait()

                    self.board.save(input('\nWrite the path to the file (.csv format)\n'))
                elif self.open_button.rect.collidepoint(*m_pos):
                    # set button cd
                    self.time_until_buttons_enabled = self.button_press_cd

                    self.wait()

                    self.board.open(input('\nWrite the path to the file (.csv format)\n'))

                elif self.change_size_button.rect.collidepoint(*m_pos):
                    # set button cd
                    self.time_until_buttons_enabled = self.button_press_cd

                    self.wait()
                    self.board.change_size(True)

        self.draw()

    # this function makes tile sprites appear so that you can choose tile by clicking on it
    def set_tile_choice_fragment(self, x, y, tile_size, n_x, gap_size):
        i = 0
        for key, val in self.tiles_images_dict.items():
            if key != ' ':
                a = pygame.sprite.Sprite(self.tile_sprite_group)

                # tile symbol
                a.sym = key
                # sprite surface
                a.image = pygame.surface.Surface((tile_size * 2, 2 * tile_size))
                a.image.fill(self.default_color, (1, 1, a.image.get_width() - 2, a.image.get_height() - 2))

                # tile image
                a.image.blit(pygame.transform.scale(val, (tile_size - 2, tile_size - 2)), (1, tile_size + 1))

                # text
                text = self.font.render(key, False, 'white')
                coef = tile_size / text.get_height()

                a.image.blit(pygame.transform.scale(text,
                                                    (min(text.get_width() * coef, a.image.get_width() - 5), tile_size)),
                             (2, 1))

                # rect
                a.rect = a.image.get_rect()
                a.rect.x, a.rect.y = (x + (tile_size * 2 + gap_size) * (i % n_x),
                                      y + (tile_size * 2 + gap_size) * (i // n_x))

                i += 1

    def wait(self):
        coef = 0.4
        self.window_surface.blit(self.surface, (0, 0))

        x_size = int(self.window_surface.get_height() * coef * 2)
        self.window_surface.blit(pygame.transform.scale(self.extra_images['waiting_image'],
                                                        (x_size, x_size // 2)),
                                 (self.window_surface.get_width() * 0.5 - x_size // 2,
                                  self.window_surface.get_height() * 0.5 - x_size // 4))
        pygame.display.flip()
