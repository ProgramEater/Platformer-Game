import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group)
        self.size = (1 * PIX_IN_M, 1.5 * PIX_IN_M)
        self.image = pygame.transform.scale(pygame.image.load('data/playerDIR.png'), self.size)

        # sprite rect
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # set respawn position to first spawn position. When player interacts with respawn area
        # this position will be updated to the areas coords
        self.respawn_pos = (x, y)

        self.animation_dir = {'walk': [], 'jump': [], 'idle': [], 'fall': [], 'hit_player': []}
        self.current_frame = 0
        self.animation_speed = 0.15
        for j in self.animation_dir.keys():
            self.cut_the_frames(j + '.png')

        # hit animation
        self.animation_dir['hit_slash'] = []
        if True:
            image_name = 'hit_slash.png'
            frame_set = pygame.image.load('data/' + image_name)
            self.animation_dir[image_name[:-4]] = []
            for y in range(frame_set.get_height() // 72):
                for x in range(frame_set.get_width() // 72):
                    self.animation_dir[image_name[:-4]].append(frame_set.subsurface(72 * x, 72 * y,
                                                                                    72, 72))
        # загрузить картинки с множеством кадров для каждой категории в animation_dir (.convert_alpha()!!!!!!!!)
        # поделить их на кадры и добавить в словарь
        # при надобности словарь можно дополнить нужными анимациями

        # constant speeds and accelerations
        self.SPEED = 6
        self.G = 1.4

        self.JUMP_SPEED = -12.5
        self.MAX_JUMP_TIME = 15

        self.xACC = 0.2
        self.DASH_SPEED = 5.6
        self.DASH_CD_DEFAULT = 15
        self.DASH_ACC = 0.8
        self.HIT_CD_DEFAULT = 25

        # x direction of player
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

        # hit sprite
        self.hit = None
        # if player made a hit and didn't let go of hit button we don't allow hit
        # also can be used in friendly areas and so on
        self.allow_hit = True
        self.hit_CD = 0

    def cut_the_frames(self, image_name):
        frame_set = pygame.image.load('data/' + image_name)
        self.animation_dir[image_name[:-4]] = []
        for y in range(frame_set.get_height() // self.rect.h):
            for x in range(frame_set.get_width() // self.rect.w):
                self.animation_dir[image_name[:-4]].append(frame_set.subsurface(self.rect.w * x, self.rect.h * y,
                                                                                self.rect.w, self.rect.h))

    def animate(self):
        # в зависимости от статуса менять self.image (flip if self.dirTowards)
        # для трекинга кадра анимации: менять current_frame с 0 до количества кадров
        status = self.moving_status()
        self.current_frame += self.animation_speed
        self.current_frame = 0 if len(self.animation_dir[status]) <= self.current_frame else self.current_frame
        if status == 'hit_player':
            self.hit.animate(self.animation_dir['hit_slash'][int(self.current_frame)])
            if self.current_frame > len(self.animation_dir['hit_slash']) - self.animation_speed * 2:
                self.hit.kill()
                self.hit = None
                self.hit_CD = self.HIT_CD_DEFAULT
        self.image = self.animation_dir[status][int(self.current_frame)]
        if not self.dirTowards:
            self.image = pygame.transform.flip(pygame.transform.scale(self.image, self.size), True, False)

    def moving_status(self):
        if self.dirX > 0 and self.hit is None:
            self.dirTowards = True
        elif self.dirX < 0 and self.hit is None:
            self.dirTowards = False
        if self.hit is not None:
            return 'hit_player'
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
            if (not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]) or (keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]):
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

        # we create hit sprite if we can hit
        if keys[pygame.K_x] and self.allow_hit and self.hit is None:
            # hit direction
            status = 'side' if keys[pygame.K_UP] == keys[pygame.K_DOWN] else ('up' if keys[pygame.K_UP] else 'down')
            self.hit = Hit(status, self)
            self.allow_hit = False
            # hit cooldown will be started as soon as hit is KILLED
        elif not keys[pygame.K_x] and not self.hit_CD:
            self.allow_hit = True
        # print(self.hit_CD, keys[pygame.K_x], self.hit, self.allow_hit)

    def update(self):
        self.animate()
        self.get_input()

        if self.current_jump_time != self.MAX_JUMP_TIME:
            self.current_jump_time += 1
        else:
            self.jump = 0
        if self.speedY > 0:
            self.jump = 0

        # dash change and stopping
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
        if self.hit_CD:
            self.hit_CD -= 1

        self.gravity()

        self.rect.y += self.speedY
        self.collision('y')
        self.rect.x += self.dirX * self.SPEED
        self.collision('x')

        # we need to move respawn position with camera movement so that will remain in place
        global camera
        self.respawn_pos = (self.respawn_pos[0] + camera.dx, self.respawn_pos[1] + camera.dy)
        if pygame.sprite.spritecollideany(self, spike_group):
            self.respawn()

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
        pygame.time.delay(300)
        self.rect.x, self.rect.y = self.respawn_pos

    def gravity(self):
        self.speedY += self.G
        self.speedY = 30 if self.speedY > 30 else self.speedY


class Hit(pygame.sprite.Sprite):
    def __init__(self, status, player_obj):
        super().__init__(player_group)
        self.parent = player_obj
        self.image = pygame.transform.flip(self.parent.animation_dir['hit_slash'][0],
                                           False if self.parent.dirTowards else True, False)
        self.rect = self.image.get_rect()
        self.mask = self.image.get_masks()
        self.rect.x, self.rect.y = {'side': (self.parent.rect.x + (self.parent.rect.w if self.parent.dirTowards
                                                                   else -self.rect.w), self.parent.rect.y),
                                    'up': (self.parent.rect.x, self.parent.rect.y - self.rect.h),
                                    'down': (self.parent.rect.x, self.parent.rect.y + self.parent.rect.h)}[status]

    def animate(self, img):
        self.image = img
        if not self.parent.dirTowards:
            self.image = pygame.transform.flip(self.image, True, False)


class Camera:
    def __init__(self):
        self.dy = 0
        self.dx = 0

    def update(self):
        self.dy = height // 2 - player.rect.y - player.rect.height // 2
        self.dx = width // 2 - player.rect.x - player.rect.w // 2

    def apply(self, obj):
        obj.rect = obj.rect.move(self.dx, self.dy)


class Level:
    def __init__(self, start_level=0):
        self.current_level = start_level
        self.level_names = ['data/' + lev_name for lev_name in ['lev.txt', 'lev2.txt']]

    def load_level(self, name):
        with open(name) as level:
            level_lines = level.readlines()
            for y, st in enumerate(level_lines):
                for x, elem in enumerate(st):
                    if elem in '-_|':
                        # creating platform. Floor if '-', ceiling if '_', side if '|'
                        a = pygame.sprite.Sprite(platform_group)
                        a.image = pygame.transform.scale(pygame.image.load('data/grass_floor.png'),
                                                         (0.5 * PIX_IN_M, 0.5 * PIX_IN_M))
                        # rotate floor texture by 90, 270 if that is side, 180 if it is ceiling
                        a.image = pygame.transform.rotate(a.image, 0 if elem == '-' else (180 if elem == '_' else
                                                                                          (90 if
                                                                                           level_lines[y][x + 1] == '#'
                                                                                           else -90)))
                        a.rect = a.image.get_rect()
                        a.rect.x = x * 0.5 * PIX_IN_M
                        a.rect.y = y * 0.5 * PIX_IN_M
                    elif elem == '#':
                        # blocks at the center of a platform
                        a = pygame.sprite.Sprite(platform_group)
                        a.image = pygame.transform.scale(pygame.surface.Surface((x * 0.5 * PIX_IN_M,
                                                                                 y * 0.5 * PIX_IN_M)),
                                                         (0.5 * PIX_IN_M, 0.5 * PIX_IN_M))
                        a.image.fill('black')
                        a.rect = a.image.get_rect()
                        a.rect.x = x * 0.5 * PIX_IN_M
                        a.rect.y = y * 0.5 * PIX_IN_M
                    elif elem == '@':
                        # player spawn
                        global player
                        player = Player(x * 0.5 * PIX_IN_M, y * 0.5 * PIX_IN_M)
                    elif elem == 's':
                        a = pygame.sprite.Sprite(spike_group)
                        a.image = pygame.transform.scale(pygame.image.load('data/spike.png'),
                                                         (0.5 * PIX_IN_M, 0.5 * PIX_IN_M))
                        a.rect = a.image.get_rect()
                        a.rect.x, a.rect.y = 0.5 * PIX_IN_M * x, 0.5 * PIX_IN_M * y

    def load_another(self, next_prev):
        self.load_level(self.level_names[self.current_level + next_prev])
        self.current_level += next_prev


if __name__ == '__main__':
    pygame.init()

    # screen:
    size = width, height = 1280, 800
    PIX_IN_M = 72
    # = height * 72 / 1080
    screen = pygame.display.set_mode(size)

    player_group = pygame.sprite.Group()

    platform_group = pygame.sprite.Group()
    spike_group = pygame.sprite.Group()

    the_level = Level()
    the_level.load_another(1)

    camera = Camera()

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player_group.update()

        camera.update()
        for i in platform_group:
            camera.apply(i)
        for i in spike_group:
            camera.apply(i)
        camera.apply(player)

        clock.tick(60)

        screen.fill((255, 255, 255))
        platform_group.draw(screen)
        spike_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
