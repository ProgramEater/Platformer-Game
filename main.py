import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group)
        self.rect = pygame.rect.Rect(x, y, 30, 40)
        self.image = pygame.image.load('data/player.png')
        self.speedX = 0
        self.speedY = 0

    def update(self):
        self.rect.x += self.speedX
        self.rect.y += self.speedY


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
            if event.type == pygame.KEYDOWN:
                if event.key == 97:
                    player.speedX = -1
                if event.key == 100:
                    player.speedX = 1
                if event.key == 32:
                    player.rect.y -= 1
                    player.speedY -= 3

            if event.type == pygame.KEYUP:
                keys = pygame.key.get_pressed()
                if keys[97] == 0 == keys[100]:
                    player.speedX = 0

            if event.type == PLAYER_MOVE:
                player_group.update()

            if event.type == GRAVITY:
                collide = pygame.sprite.spritecollide(player, platform_group, False)
                if collide:
                    for col in collide:
                        pass # adoka;ldma;ldma;Dmakmdak;ldmakl;mrfkarfkamfkamfkamf;kamf;amfkmkfmk;l
                else:
                    player.speedY += 0.05

        camera.update()
        for i in platform_group:
            camera.apply(i)
        camera.apply(player)

        clock.tick(60)

        screen.fill((255, 255, 255))
        platform_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
