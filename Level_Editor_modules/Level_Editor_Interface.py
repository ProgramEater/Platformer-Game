import pygame


class Interface:
    def __init__(self, board, board_x_shift, board_y_shift, tiles_images_dict, extra_images, font, text_color,
                 tile_choice_tile_size, tile_choice_columns_number, tile_choice_gap_size, button_w, button_h,
                 button_gap_size):
        # Board and board params
        self.board = board
        self.board_x_shift, self.board_y_shift = board_x_shift, board_y_shift

        # current tile
        self.current_tile = '#'

        # button press cooldown
        self.button_press_cd = 60
        self.time_until_buttons_enabled = 0

        # decoration
        self.extra_images = extra_images
        self.tiles_images_dict = tiles_images_dict
        self.font = font
        self.text_color = text_color

        # buttons setup
        self.button_params = (button_w, button_h, button_gap_size)
        self.buttons_sprite_group = pygame.sprite.Group()
        # buttons
        if True:
            if int(button_h) > self.board_y_shift - 6:
                button_w //= int(button_h) / (self.board_y_shift - 6)
                button_h = self.board_y_shift - 6

            self.save_button = pygame.sprite.Sprite(self.buttons_sprite_group)
            self.save_button.image = pygame.transform.scale(self.extra_images['save_button'], (button_w, button_h))
            self.save_button.rect = pygame.rect.Rect(self.board_x_shift, 3, *self.save_button.image.get_size())

            self.open_button = pygame.sprite.Sprite(self.buttons_sprite_group)
            self.open_button.image = pygame.transform.scale(self.extra_images['open_button'], (button_w, button_h))
            self.open_button.rect = pygame.rect.Rect(self.board_x_shift + button_w + button_gap_size, 3,
                                                     *self.open_button.image.get_size())

            self.change_size_button = pygame.sprite.Sprite(self.buttons_sprite_group)
            self.change_size_button.image = pygame.transform.scale(self.extra_images['change_size_button'],
                                                                   (button_w // 2, button_h))
            self.change_size_button.rect = pygame.rect.Rect(self.board_x_shift + 2 * button_w + 2 * button_gap_size, 3,
                                                            *self.change_size_button.image.get_size())

        # tile choice setup
        self.tile_choice_params = tile_choice_tile_size, tile_choice_columns_number, tile_choice_gap_size
        self.tile_sprite_group = pygame.sprite.Group()
        if True:
            line_num = (len(tiles_images_dict.keys()) - 1) / tile_choice_columns_number
            line_num = int(line_num) if line_num % 1 == 0 else int(line_num) + 1
            choice_tile_size = min(tile_choice_tile_size, self.board_y_shift - 6)
            choice_tile_size //= line_num
            self.set_tile_choice_fragment(self.board_x_shift + button_w * 2.5 + button_gap_size * 2 +
                                          tile_choice_gap_size,
                                          3, choice_tile_size, tile_choice_columns_number, tile_choice_gap_size)

        # interface surface
        self.surface = pygame.surface.Surface((max(self.board_x_shift + self.board.w * self.board.tile_size,
                                                   self.board_x_shift + 2.5 * button_w + 2 * button_gap_size +
                                                   ((choice_tile_size +
                                                     tile_choice_gap_size) * tile_choice_columns_number)
                                                   - tile_choice_gap_size),
                                               self.board_y_shift + self.board.h * self.board.tile_size))
        self.draw()

    def draw(self):
        self.surface.fill(self.extra_images['default_color'])
        self.surface.blit(self.board.surface, (self.board_x_shift, self.board_y_shift))
        self.tile_sprite_group.draw(self.surface)
        self.buttons_sprite_group.draw(self.surface)

        self.surface.blit(self.tile_name_under_cursor(pygame.mouse.get_pos()), (0, 0))

    def update(self):
        self.time_until_buttons_enabled = max(self.time_until_buttons_enabled - 1, 0)
        m_pos = pygame.mouse.get_pos()
        m_keys = pygame.mouse.get_pressed()

        x, y = self.mouse_pos_to_index(*m_pos)
        # Left mouse button is clicked
        if m_keys[0]:
            # if board is clicked
            if -1 < x < self.board.w and -1 < y < self.board.h:
                if self.current_tile == 'special':
                    self.board.add_tile(x, y, input())
                else:
                    self.board.add_tile(x, y, self.current_tile)
            else:
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

                        self.board.save(input())
                    elif self.open_button.rect.collidepoint(*m_pos):
                        # set button cd
                        self.time_until_buttons_enabled = self.button_press_cd

                        self.board.open(input())

                        # remake surface
                        self.surface = pygame.surface.Surface((max(self.open_button.rect.x + self.open_button.rect.w + 5,
                                                                   self.board_x_shift +
                                                                   self.board.w * self.board.tile_size),
                                                               self.board_x_shift + self.board.h * self.board.tile_size))
                    elif self.change_size_button.rect.collidepoint(*m_pos):
                        # set button cd
                        self.time_until_buttons_enabled = self.button_press_cd

                        self.board.change_tile_size(True)

                        # remake surface
                        self.surface = pygame.surface.Surface((max(self.open_button.rect.x + self.open_button.rect.w + 5,
                                                                   self.board_x_shift +
                                                                   self.board.w * self.board.tile_size),
                                                               self.board_x_shift + self.board.h * self.board.tile_size))
        # Right mouse button clicked
        elif m_keys[2]:
            if -1 < x < self.board.w and -1 < y < self.board.h:
                self.board.erase(x, y)

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
                a.image.fill(self.extra_images['default_color'], (1, 1, a.image.get_width() - 2, a.image.get_height() - 2))

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
                a.rect.x, a.rect.y = x + (tile_size * 2 + gap_size) * (i % n_x), y + (tile_size * 2 + gap_size) * (i // n_x)

                i += 1

    def mouse_pos_to_index(self, x, y):
        x -= self.board_x_shift
        x //= self.board.tile_size
        y -= self.board_y_shift
        y //= self.board.tile_size
        return x, y

    def tile_name_under_cursor(self, pos):
        x, y = self.mouse_pos_to_index(*pos)
        if -1 < x < self.board.w and -1 < y < self.board.h:
            return self.font.render(self.board.list[y][x], False, self.text_color)
        else:
            return self.extra_images['default_surf']
