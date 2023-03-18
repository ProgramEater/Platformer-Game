import pygame
import os
PIX_IN_M = 72


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group)
        self.size = (1 * PIX_IN_M, 1.5 * PIX_IN_M)
        self.image = pygame.Surface(self.size)

        # sprite rect
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # set respawn position to first spawn position. When player interacts with respawn area
        # this position will be updated to the areas coords
        self.respawn_pos = (x, y)

        self.animation_dir = {'walk': [], 'jump': [], 'idle': [], 'fall': []}
        self.current_frame = 0
        self.animation_speed = 0.15
        for j in self.animation_dir.keys():
            self.animation_dir[j] = cut_the_frames(f'data/textures/{j}.png', self.rect.w, self.rect.h)

        # constant speeds and accelerations
        self.SPEED = 6
        self.G = 1.3

        self.JUMP_SPEED = -12.5
        self.MAX_JUMP_TIME = 15

        self.xACC = 0.2
        self.DASH_SPEED = 5.6
        self.DASH_CD_DEFAULT = 15
        self.DASH_ACC = 0.8

        # x speed of player
        self.dirX = 0
        # direction player is facing (True if he is facing to the right)
        self.dirTowards = True

        # is player dashing
        self.dashing = False
        # if player dashed but doesn't release dash button, we won't let him dash
        self.dash_enabled = True
        # dash cooldown, interval between dashes
        self.dash_CD = 0

        # player Y speed
        self.speedY = 0

        # current jump speed (JUMP_SPEED for convenience)
        self.jump = self.JUMP_SPEED
        self.current_jump_time = 0

        # if player jumped in air we remember ticks when he did it
        # and if he was near the surface, we perform jump anyway
        self.jump_clicked = 0
        self.remember_first_jump_frame = False

        # this variable contains hit sprite. If it's None => we are not hitting otherwise we do
        self.hit_sprite = Hit(self)

        # speed of knockback when target is hit
        self.hit_pogo_speed_y = 20
        self.hit_pogo_speed_x = 2

    def animate(self):
        # в зависимости от статуса менять self.image (flip if self.dirTowards)
        # для трекинга кадра анимации: менять current_frame с 0 до количества кадров
        status = self.moving_status()
        self.current_frame += self.animation_speed
        self.current_frame = 0 if len(self.animation_dir[status]) <= self.current_frame else self.current_frame
        self.image = self.animation_dir[status][int(self.current_frame)]
        if not self.dirTowards:
            self.image = pygame.transform.flip(pygame.transform.scale(self.image, self.size), True, False)

    def moving_status(self):
        if self.dirX > 0 and not self.hit_sprite.active:
            self.dirTowards = True
        elif self.dirX < 0 and not self.hit_sprite.active:
            self.dirTowards = False
        if self.speedY < 0:
            return 'jump'
        elif self.speedY == 0 and self.dirX == 0:
            return 'idle'
        elif self.speedY == 0 and self.dirX != 0:
            return 'walk'
        elif self.speedY > 0:
            return 'fall'
        # возвращать прыжок, ходьбу и т.д. в зависимости от того, что делает игрок (по скорости)
        # менять self.dirTowards здесь

    def get_input(self):
        keys = pygame.key.get_pressed()

        # X MOVEMENT
        # if player is not dashing, we check pressed keys and move player to the right or left
        # or we stop player if both keys are pressed or none of them are
        if not self.dashing:
            # Left
            if keys[pygame.K_LEFT]:
                self.dirX -= self.xACC
                self.dirX = -1 if self.dirX < -1 else self.dirX
            # Right
            if keys[pygame.K_RIGHT]:
                self.dirX += self.xACC
                self.dirX = 1 if self.dirX > 1 else self.dirX
            # Stopping if both or none are pressed
            if keys[pygame.K_LEFT] == keys[pygame.K_RIGHT]:
                if abs(self.dirX) - self.xACC < 0:
                    self.dirX = 0
                else:
                    self.dirX -= self.xACC if self.dirX > 0 else -self.xACC

        # Jump
        if keys[pygame.K_z]:
            # if player clicked jump, we remember the time when he just hit the jump
            # if he was in the air at the time, but he was near the ground, we still let him jump
            if self.remember_first_jump_frame:
                self.jump_clicked = pygame.time.get_ticks()
                self.remember_first_jump_frame = False
            # If jump is enabled, y speed is equal jump
            if self.jump:
                self.speedY = self.jump
        else:
            if self.current_jump_time:
                self.jump = 0
            self.remember_first_jump_frame = True

        # Dash
        # we dash if we are not dashing at the moment, dash cooldown is 0 and if player hit dash
        # and player is not holding dash button and he touched the floor (or pogo)
        if keys[pygame.K_c] and not self.dashing and not self.dash_CD and self.dash_enabled:
            self.dash_enabled = False
            self.dashing = True

        if not self.dashing and keys[pygame.K_x] and not self.hit_sprite.active:
            self.hit_sprite.activate('up' if keys[pygame.K_UP] else 'down' if keys[pygame.K_DOWN] else 'side')

    def update(self):
        self.animate()
        self.get_input()

        # jump time and update
        if self.current_jump_time != self.MAX_JUMP_TIME:
            self.current_jump_time += 1
        else:
            self.jump = 0
        if self.speedY > 0:
            self.jump = 0

        # dash update and stopping
        if self.dashing:
            # you don't fall or jump while dashing, so y speed = 0
            # that is actually causing a bug: when you jump touching the wall and dash, you stop moving upwards
            self.speedY = 0
            self.dirX += self.DASH_ACC if self.dirTowards > 0 else -self.DASH_ACC
            if abs(self.dirX) >= self.DASH_SPEED:
                self.DASH_ACC *= -1
            if abs(self.dirX) <= 1 and self.DASH_ACC < 0:
                self.DASH_ACC *= -1
                self.dirX = 1 if self.dirTowards else -1
                self.dashing = False
                self.dash_CD = self.DASH_CD_DEFAULT
        if self.dash_CD:
            self.dash_CD -= 1

        self.gravity()

        # calculate collisions
        self.rect.y += self.speedY
        self.collision('y')
        self.rect.x += self.dirX * self.SPEED
        self.collision('x')

        # updating respawn position
        global camera
        self.respawn_pos = (self.respawn_pos[0] + camera.dx + camera.x_shift,
                            self.respawn_pos[1] + camera.dy + camera.y_shift)

        # collision with spikes transitions and so on
        if pygame.sprite.spritecollideany(self, spike_group):
            self.respawn()
        if pygame.sprite.spritecollideany(self, transition_group):
            transition = pygame.sprite.spritecollide(self, transition_group, False)[0]
            self.transition(transition)

    def stop_player(self):
        self.dashing = False
        self.dirX = 0
        self.jump = 0
        self.hit_sprite.deactivate()
        self.speedY = 0

    def collision(self, axis):
        if pygame.sprite.spritecollide(self, platform_group, False):
            plat = pygame.sprite.spritecollide(self, platform_group, False)[0]
            if axis == 'y':
                self.rect.y = plat.rect.y - self.rect.h if self.speedY >= 0 else plat.rect.y + plat.rect.h
                self.speedY = 0
                # or (pygame.time.get_ticks() - self.jump_clicked) < 50 is needed to make jump timing bigger
                # player will be able to jump if he hit jump button 0.05 seconds (50 ticks) before touching the ground
                if not pygame.key.get_pressed()[pygame.K_z] or (pygame.time.get_ticks() - self.jump_clicked) < 50:
                    self.jump = self.JUMP_SPEED
                    self.current_jump_time = 0
                else:
                    self.jump = 0
                # if player touched the ground and he doesn't hold dash button
                if not pygame.key.get_pressed()[pygame.K_c]:
                    self.dash_enabled = True
            else:
                self.rect.x = plat.rect.x - self.rect.w if self.dirX > 0 else plat.rect.x + plat.rect.w
                self.dirX = 0
                # stop dashing if hit the platform to the side
                if self.dashing:
                    # player shouldn't be able to jump if he hits the platform while dashing
                    self.jump = 0
                    self.dash_CD = self.DASH_CD_DEFAULT
                self.dashing = False
                self.DASH_ACC *= -1 if self.DASH_ACC < 0 else 1

    def respawn(self):
        # this method respawns player on last respawn area
        # if player falls in the spikes he will be respawned
        self.stop_player()

        pygame.time.delay(50)
        self.rect.x, self.rect.y = self.respawn_pos

    def transition(self, trans_sprite):
        global the_level, text_surface, my_font
        if the_level.current_level == 0:
            text_surface = my_font.render('"c" - dash', False, (0, 0, 0))
        elif the_level.current_level == 2:
            text_surface = my_font.render('YOU WON!!!!!!!!!', False, (0, 0, 0))
        else:
            text_surface = my_font.render('', False, (0, 0, 0))
        the_level.transitioning_from = the_level.current_level
        self.stop_player()
        the_level.load_level(trans_sprite.next_level_ind)

    def gravity(self):
        self.speedY += self.G
        self.speedY = 30 if self.speedY > 30 else self.speedY


class Hit(pygame.sprite.Sprite):
    def __init__(self, player_sp):
        super().__init__(hit_group)

        # create transparent surface for hit whenever it isn't active
        self.transp_surface = pygame.Surface((PIX_IN_M, PIX_IN_M), pygame.SRCALPHA)
        self.transp_surface.convert_alpha()

        self.rect = pygame.rect.Rect(0, 0, PIX_IN_M, PIX_IN_M)
        self.image = self.transp_surface

        self.active = False

        self.animation_dir = {}
        self.animate_to_the_end = False

        for i in ['side', 'up', 'down']:
            self.animation_dir[i] = cut_the_frames(f'data/textures/{i}_slash.png', self.rect.w, self.rect.h)

        self.current_frame = 0

        # sprite of sender (Hit sprite is created in player)
        self.player = player_sp

        # direction of hit
        self.dir = None
        # if hit button is not released player can't hit
        self.hit_enabled = True

        # hit speed (hit time in ticks is --- self.hit_speed * len(self.frames)
        self.hit_speed = 0.4

    def activate(self, direction):
        if self.hit_enabled:
            self.active = True
            self.dir = direction
            self.hit_enabled = False

    def deactivate(self):
        self.active = False
        self.current_frame = 0
        self.image = self.transp_surface

    def update(self):
        keys = pygame.key.get_pressed()

        # position update
        if not self.active and not self.animate_to_the_end:
            if keys[pygame.K_DOWN] == keys[pygame.K_UP]:
                self.rect.y = self.player.rect.y
                self.rect.x = (self.player.rect.x + self.player.rect.w) if self.player.dirTowards \
                    else (self.player.rect.x - self.player.rect.w)
            elif keys[pygame.K_DOWN]:
                self.rect.y, self.rect.x = self.player.rect.y + self.player.rect.h, self.player.rect.x
            elif keys[pygame.K_UP]:
                self.rect.y, self.rect.x = self.player.rect.y - self.rect.h, self.player.rect.x

        # animation is played if hit is active OR if we want it to play to the end
        # (be fully played even if hit is not already active)
        if self.active or self.animate_to_the_end:
            self.animate()

        # enable hit if hit button is released
        if not self.hit_enabled and not keys[pygame.K_x]:
            self.hit_enabled = True

        self.pogo()

    def animate(self):
        self.current_frame += self.hit_speed
        if self.current_frame >= len(self.animation_dir[self.dir]):
            self.animate_to_the_end = False
            self.current_frame = 0
            self.active = False
            self.image = self.transp_surface
        else:
            self.image = self.animation_dir[self.dir][int(self.current_frame)]
            self.image = pygame.transform.flip(self.image, True, False) if not self.player.dirTowards else self.image

    # if player hits spike or enemy ge should get knockback (be pushed away from hit target)
    def pogo(self):
        if pygame.sprite.spritecollideany(self, spike_group) and self.active:
            self.player.dirX = self.player.hit_pogo_speed_x * (1 if self.dir == 'side' and not self.player.dirTowards
                                                               else -1 if self.dir == 'side' else self.player.dirX)
            self.player.speedY = self.player.hit_pogo_speed_y * (1 if self.dir == 'up'
                                                                 else (-1 if self.dir == 'down' else self.player.speedY))
            self.deactivate()
            if self.dir == 'down':
                self.animate_to_the_end = True

            # player abilities reset after pogo
            self.player.dash_enabled = True
            self.player.dash_CD = 0
            self.player.jump = 0 if self.dir == 'down' or self.dir == 'up' else self.player.jump


class Camera:
    def __init__(self):
        self.dy = 0
        self.dx = 0

        self.x_shift = 0
        self.y_shift = 0

        self.x_range = 300
        self.y_range = 200

        self.y_coef = 0
        self.x_coef = 0

    def update(self):
        self.dy = (height // 2 - player.rect.y - player.rect.height // 2)
        self.dx = (width // 2 - player.rect.x - player.rect.w // 2)

        # camera_shift_on_axis = -delta_on_axis * coefficient
        # coefficient = 1 - min(abs(delta_on_axis) / value, 1)
        # coefficient is needed in order for the camera would shift depending on the distance to the player
        # value - is the distance at which camera shift disappears (== 0)
        # If the distance is smaller, then the shift increases linearly proportional to it
        self.x_shift = -self.dx * (1 - min(abs(self.dx) / self.x_range, 1))
        self.y_shift = -self.dy * (1 - min(abs(self.dy) / self.y_range, 1))

    def apply(self, obj):
        obj.rect = obj.rect.move(self.dx + self.x_shift, self.dy + self.y_shift)


class Transition(pygame.sprite.Sprite):
    def __init__(self, next_level_ind, direction, x, y, wall_to):
        super().__init__(transition_group)
        self.next_level_ind = next_level_ind

        self.dir = direction

        # direction of neares to the transition wall (if player goes right to get in it is 'r', wall to the left - 'l'
        # up - 'u', down - 'd'
        self.wall_to = wall_to

        self.image = pygame.transform.scale(pygame.image.load('data/textures/transit.png'),
                                            (PIX_IN_M * 0.5 * (5 if direction == 'h' else 1),
                                             PIX_IN_M * 0.5 * (5 if direction == 'v' else 1)))

        # sprite coords (x, y - coordinates of the middle digit in transition definition in text file)
        # if transit is vertical we need to move it closer to the wall, so that it would touch it
        # if it is horizontal we need to move it to the right so that it also would touch right wall
        x_coord = (x + (1 if self.wall_to == 'r' else -1)) if direction == 'v' else x - 2
        y_coord = (y - (2 if direction == 'v' else 0))

        self.rect = pygame.rect.Rect(x_coord * 0.5 * PIX_IN_M, y_coord * 0.5 * PIX_IN_M, *self.image.get_size())


class Level:
    def __init__(self, start_level=0):
        self.current_level = start_level
        # list of level names in from 0 to more...
        self.level_names = ['data/levels/' + i for i in list(os.walk('data/levels/'))[0][2]]

        # index of a level that player left when he transitioned
        # None - if he didn't come from another lvl but was teleported or died and so on
        self.transitioning_from = None

    def load_level(self, index):
        self.unload_level()

        self.current_level = index
        with open(self.level_names[index]) as level:
            level_lines = [i.strip() for i in level.readlines()]
            for y, st in enumerate(level_lines):
                for x, elem in enumerate(st):

                    # create basic tile
                    # then change tile image according to its role (symbol)
                    tile = pygame.sprite.Sprite()
                    tile.rect = pygame.rect.Rect(x * 0.5 * PIX_IN_M, y * 0.5 * PIX_IN_M, 0.5 * PIX_IN_M, 0.5 * PIX_IN_M)

                    if elem == '@' and self.transitioning_from is None:
                        # if it is @ then we should create player sprite at these coordinates
                        # player spawn
                        global player
                        player.rect.x, player.rect.y = x * 0.5 * PIX_IN_M, y * 0.5 * PIX_IN_M
                        player.respawn_pos = (x * 0.5 * PIX_IN_M, y * 0.5 * PIX_IN_M)

                    elif elem in '-_|':
                        # creating platform. Floor if '-', ceiling if '_', side if '|'
                        tile.image = pygame.transform.scale(pygame.image.load('data/textures/grass_floor.png'),
                                                            (0.5 * PIX_IN_M, 0.5 * PIX_IN_M))

                        # rotate floor texture by 90, 270 if that is side, 180 if it is ceiling
                        tile.image = pygame.transform.rotate(tile.image, 0 if elem == '-' else (
                            180 if elem == '_' else (90 if level_lines[y][x + 1] == '#' else -90)))

                        platform_group.add(tile)

                    elif elem == '#':
                        # blocks at the center of a platform
                        tile.image = pygame.transform.scale(pygame.surface.Surface((x * 0.5 * PIX_IN_M,
                                                                                    y * 0.5 * PIX_IN_M)),
                                                            (0.5 * PIX_IN_M, 0.5 * PIX_IN_M))
                        tile.image.fill('black')

                        platform_group.add(tile)

                    elif elem == 's':
                        # spikes
                        tile.image = pygame.transform.scale(pygame.image.load('data/textures/spike.png'),
                                                            (0.5 * PIX_IN_M, 0.5 * PIX_IN_M))
                        if level_lines[y - 1][x] == '#':
                            tile.image = pygame.transform.rotate(tile.image, 180)

                        spike_group.add(tile)

                    elif elem.isdigit():
                        # transitions
                        # if we find digit it means we need to place transition
                        # transition is going to be defined with 3 symbols: direction letter and a number (from 0 to 99)
                        # direction letter - 'h' or 'v' (horizontal or vertical)

                        # number is the number of level where transition leads to
                        # (so index in self.level_names is number - 1)

                        # ex: h12 - horizontal transition to lvl 13 (index - 12), v02 - vertical transition to lvl 2

                        transit_def = st[x - 1:x + 2]

                        # if transit_def[0] is not v or h that means that in h12 the elem is not 1 but 2
                        # and transit_def in fact is 12. so transition was already created 1 iteration (step) before
                        if transit_def[0] in 'hv':
                            wall_to = ('u' if level_lines[y - 1][x] == '#' else 'd') \
                                if transit_def[0] == 'h' else ('r' if st[x + 2] == '#' else 'l')
                            tile = Transition(int(transit_def[1:]) - 1, transit_def[0], x, y, wall_to)
                            transition_group.add(tile)

            # if player was not teleported to spawn location because he transitioned from another lvl, we teleport him
            if self.transitioning_from is not None:
                transit_spr = [i for i in transition_group][list(map(lambda i: i.next_level_ind,
                                                                     transition_group)).index(self.transitioning_from)]
                self.transition_player(transit_spr)

    def transition_player(self, transit_spr):
        if transit_spr.dir == 'v':
            # put player to the side of transit
            p_x = transit_spr.rect.x + PIX_IN_M * (-1.5 if transit_spr.wall_to == 'r' else 1)
            # put player on the floor
            p_y = transit_spr.rect.y + 1 * PIX_IN_M
        else:
            if transit_spr.wall_to == 'u':
                p_x = transit_spr.rect.x + 1 * PIX_IN_M
                p_y = transit_spr.rect.y + 3 * PIX_IN_M
            else:
                p_x = transit_spr.rect.x + PIX_IN_M * (3.5 if player.dirTowards else -1)
                p_y = transit_spr.rect.y - 2 * PIX_IN_M

        player.rect.x, player.rect.y = p_x, p_y
        player.respawn_pos = (p_x, p_y)
        self.transitioning_from = None

    def unload_level(self):
        for i in [platform_group, spike_group, transition_group]:
            for j in i:
                j.kill()

    def get_current(self):
        return self.current_level


# this function takes an image and then cuts in tiles with tiles size (then the set of these tiles is returned)
def cut_the_frames(path, tile_w, tile_h):
    frame_set = pygame.image.load(path)
    frames = []
    for y in range(frame_set.get_height() // tile_h):
        for x in range(frame_set.get_width() // tile_w):
            frames.append(frame_set.subsurface(tile_w * x, tile_h * y, tile_w, tile_h))
    return frames


if __name__ == '__main__':
    pygame.init()

    # screen:
    size = width, height = 1280, 800
    pygame.display.set_caption('4-LEVEL GAME!!!!!!!!')
    # = height * 72 / 1080
    screen = pygame.display.set_mode(size)

    player_group = pygame.sprite.Group()

    platform_group = pygame.sprite.Group()
    spike_group = pygame.sprite.Group()
    transition_group = pygame.sprite.Group()
    hit_group = pygame.sprite.Group()

    player = Player(0, 0)
    the_level = Level()
    the_level.load_level(2)

    camera = Camera()

    clock = pygame.time.Clock()

    # text
    pygame.font.init()
    my_font = pygame.font.SysFont('Times New Roman', 25)
    text_surface = my_font.render('"←", "→" - move, "z" - jump', False, (0, 0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        hit_group.update()
        player_group.update()

        camera.update()
        for group in [platform_group, spike_group, transition_group]:
            for i in group:
                camera.apply(i)
        camera.apply(player)

        clock.tick(60)

        screen.fill((255, 255, 255))

        transition_group.draw(screen)
        platform_group.draw(screen)
        spike_group.draw(screen)
        player_group.draw(screen)
        hit_group.draw(screen)

        screen.blit(text_surface, (0, 0))

        pygame.display.flip()
