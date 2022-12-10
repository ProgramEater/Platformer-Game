import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group)
        self.rect = pygame.rect.Rect(x, y, 30, 40)
        self.image = pygame.image.load('data/player.png')
        self.speed = 5
        self.dirX = 0
        self.speedY = 0
        self.g = 1
        self.can_jump = 1

    def get_input(self):
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
            # ДОДЕЛАТЬ ПРЫЖОК --------------------------------------------------------------
            self.speedY -= 2

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
                self.rect.y = plat.rect.y - self.rect.h if self.speedY >= 0 else plat.rect.y + plat.rect.h + 1
                self.speedY = 0
                self.can_jump = 1
            else:
                self.rect.x = plat.rect.x - self.rect.w - 1 if self.dirX > 0 else plat.rect.x + plat.rect.w + 1
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


def load_level(name):
    with open(name) as level:
        for y, st in enumerate(level.readlines()):
            for x, elem in enumerate(st):
                if elem == '#':
                    a = pygame.sprite.Sprite(platform_group)
                    a.image = pygame.transform.scale(pygame.image.load('data/player.png'), (20, 20))
                    a.rect = a.image.get_rect()
                    a.rect.x = x * 20 + 100
                    a.rect.y = y * 20


if __name__ == '__main__':
    pygame.init()

    player_group = pygame.sprite.Group()
    player = Player(200, 180)

    platform_group = pygame.sprite.Group()
    platform1 = pygame.sprite.Sprite(platform_group)
    platform1.rect = pygame.rect.Rect(100, 300, 300, 50)
    platform1.image = pygame.transform.scale(pygame.image.load('data/player.png'), (300, 50))

    load_level('data/lev.txt')

    camera = Camera()

    # screen:
    size = width, height = 1000, 800
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()

    PLAYER_MOVE = pygame.USEREVENT + 1
    pygame.time.set_timer(PLAYER_MOVE, 2)

    GRAVITY = pygame.USEREVENT + 2
    pygame.time.set_timer(GRAVITY, 2)

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
