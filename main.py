import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group)
        self.size = (1 * PIX_IN_M, 1.5 * PIX_IN_M)
        self.image = pygame.transform.scale(pygame.image.load('data/playerDIR.png'), self.size)
        self.rect = self.image.get_rect()

        self.animation_dir = {'walk': [], 'jump': [], 'idle': [], 'fall': []}
        self.current_frame = 0
        self.animation_speed = 0.2
        for i in self.animation_dir.keys():
            self.cut_the_frames(i + '.png')
        # загрузить картинки с множеством кадров для каждой категории в animation_dir (.convert_alpha()!!!!!!!!)
        # поделить их на кадры и добавить в словарь
        # при надобности словарь можно дополнить нужными анимациями

        # sprite rect
        self.rect.x = x
        self.rect.y = y

        # constant speeds
        self.SPEED = 6
        self.G = 1
        self.JUMP_SPEED = -2
        self.xACC = 0.2

        # x direction of player
        self.dirX = 0

        # direction player is facing (True if he is facing to the right)
        self.dirTowards = True

        # player Y speed
        self.speedY = 0

        # current jump speed (JUMP_SPEED for convenience)
        self.jump = self.JUMP_SPEED

    def cut_the_frames(self, image_name):
        frame_set = pygame.image.load('data/' + image_name)
        self.animation_dir[image_name[:-4]] = []
        for x in range(frame_set.get_width() // self.rect.w):
            for y in range(frame_set.get_height() // self.rect.h):
                self.animation_dir[image_name[:-4]].append(frame_set.subsurface(self.rect.w * x, self.rect.h * y,
                                                                                self.rect.w, self.rect.h))
                print(self.animation_dir)

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
        if self.dirX > 0:
            self.dirTowards = True
        elif self.dirX < 0:
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
        if keys[pygame.K_a]:
            self.dirX -= self.xACC
            self.dirX = -1 if self.dirX < -1 else self.dirX
        elif keys[pygame.K_d]:
            self.dirX += self.xACC
            self.dirX = 1 if self.dirX > 1 else self.dirX
        else:
            if abs(self.dirX) - self.xACC < 0:
                self.dirX = 0
            else:
                self.dirX = (self.dirX // abs(self.dirX)) * (abs(self.dirX) - self.xACC)
        if keys[pygame.K_SPACE]:
            if self.jump:
                self.speedY = self.jump

    def update(self):
        self.animate()
        self.get_input()

        # jump change
        if self.jump < 0:
            self.jump -= 1
            self.jump = 0 if self.jump < -16 else self.jump
        if self.speedY > 1:
            self.jump = 0

        self.gravity()

        self.rect.y += self.speedY
        self.collision('y')
        self.rect.x += self.dirX * self.SPEED
        self.collision('x')

    def collision(self, axis):
        if pygame.sprite.spritecollide(self, platform_group, False):
            plat = pygame.sprite.spritecollide(self, platform_group, False)[0]
            if axis == 'y':
                self.rect.y = plat.rect.y - self.rect.h if self.speedY >= 0 else plat.rect.y + plat.rect.h
                self.speedY = 0
                if not pygame.key.get_pressed()[pygame.K_SPACE]:
                    self.jump = self.JUMP_SPEED
                else:
                    self.jump = 0
            else:
                self.rect.x = plat.rect.x - self.rect.w if self.dirX > 0 else plat.rect.x + plat.rect.w
                self.dirX = 0

    def gravity(self):
        self.speedY += self.G


class Camera:
    def __init__(self):
        self.dy = 0

    def update(self):
        self.dy = height // 2 - player.rect.y - player.rect.height // 2

    def apply(self, obj):
        obj.rect = obj.rect.move(0, self.dy)


class Level:
    def __init__(self, start_level=0):
        self.current_level = start_level
        self.level_names = ['data/' + lev_name for lev_name in ['lev.txt', 'lev2.txt']]

    def load_level(self, name):
        with open(name) as level:
            for y, st in enumerate(level.readlines()):
                for x, elem in enumerate(st):
                    if elem == '#':
                        a = pygame.sprite.Sprite(platform_group)
                        a.image = pygame.transform.scale(pygame.image.load('data/player.png'),
                                                         (0.5 * PIX_IN_M, 0.5 * PIX_IN_M))
                        a.rect = a.image.get_rect()
                        a.rect.x = x * 0.5 * PIX_IN_M
                        a.rect.y = y * 0.5 * PIX_IN_M

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
    player = Player(50, 180)

    platform_group = pygame.sprite.Group()

    camera = Camera()

    the_level = Level()
    the_level.load_another(0)
    the_level.load_another(1)

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
        camera.apply(player)

        clock.tick(60)

        screen.fill((255, 255, 255))
        platform_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
