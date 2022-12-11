import pygame

PIX_IN_M = 72


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group)
        self.image = pygame.transform.scale(pygame.image.load('data/player.png'), (1 * PIX_IN_M, 1.5 * PIX_IN_M))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.dirX = 0
        self.speedY = 0
        self.g = 0.7
        self.can_jump = 1

    def get_input(self):
        global jump_Event_callable
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.dirX = -1
        elif keys[pygame.K_d]:
            self.dirX = 1
        else:
            self.dirX = 0
        if keys[pygame.K_a] and keys[pygame.K_d]:
            self.dirX = 0
        if keys[pygame.K_SPACE]:
            if self.can_jump:
                self.speedY -= 1
                if jump_Event_callable:
                    pygame.time.set_timer(PLAYER_JUMP, 500)
                    jump_Event_callable = 0

    def update(self):
        self.get_input()
        self.gravity()

        self.rect.y += self.speedY
        self.collision('y')
        self.rect.x += self.dirX * self.speed
        self.collision('x')

    def collision(self, axis):
        if pygame.sprite.spritecollide(self, platform_group, False):
            plat = pygame.sprite.spritecollide(self, platform_group, False)[0]
            if axis == 'y':
                self.rect.y = plat.rect.y - self.rect.h if self.speedY >= 0 else plat.rect.y + plat.rect.h
                self.speedY = 0
                self.can_jump = 1
            else:
                self.rect.x = plat.rect.x - self.rect.w if self.dirX > 0 else plat.rect.x + plat.rect.w
                self.dirX = 0

    def gravity(self):
        self.speedY += self.g


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

    player_group = pygame.sprite.Group()
    player = Player(10, 180)

    platform_group = pygame.sprite.Group()

    camera = Camera()

    the_level = Level()
    the_level.load_another(0)
    the_level.load_another(1)
    # screen:
    size = width, height = 1920, 1080
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()

    PLAYER_JUMP = pygame.USEREVENT + 1
    pygame.time.set_timer(PLAYER_JUMP, 0)
    jump_Event_callable = 1

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == PLAYER_JUMP:
                player.can_jump = 0
                pygame.time.set_timer(PLAYER_JUMP, 0)
                jump_Event_callable = 1
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
