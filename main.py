import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group)
        self.rect = pygame.rect.Rect(x, y, 30, 40)
        self.image = pygame.image.load('data/player.png')


if __name__ == '__main__':
    pygame.init()

    player_group = pygame.sprite.Group()
    player = Player(200, 200)
    player_speed_X = 0
    player_speed_Y = 0

    platform_group = pygame.sprite.Group()
    platform1 = pygame.sprite.Sprite(platform_group)
    platform1.rect = pygame.rect.Rect(100, 300, 300, 50)
    platform1.image = pygame.transform.scale(pygame.image.load('data/player.png'), (300, 50))
    # screen:
    size = width, height = 500, 400
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    PLAYER_MOVE = pygame.USEREVENT + 1
    pygame.time.set_timer(PLAYER_MOVE, 2)
    GRAVITY = pygame.USEREVENT + 2
    pygame.time.set_timer(GRAVITY, 1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                # a
                if keys[97]:
                    player_speed_X = -1
                # s
                if keys[100]:
                    player_speed_X = 1
                # both
                if keys[100] and keys[97]:
                    player_speed_X = 0
                # space
                if keys[32] and pygame.sprite.spritecollideany(player, platform_group):
                    player.rect = player.rect.move(0, -2)
                    player_speed_Y = -4

            if event.type == pygame.KEYUP:
                keys = pygame.key.get_pressed()
                if not keys[97] and not player_speed_Y:
                    player_speed_X = 0
                if not keys[100] and not player_speed_Y:
                    player_speed_X = 0

            if event.type == PLAYER_MOVE:
                player.rect = player.rect.move(player_speed_X, player_speed_Y)

            if event.type == GRAVITY:
                col = pygame.sprite.spritecollide(player, platform_group, False)
                if col:
                    player.rect = player.rect.move(0, col[0].rect.y - player.rect.y - player.rect.height + 1)
                    player_speed_Y = 0
                else:
                    player_speed_Y += 0.05
        screen.fill((255, 255, 255))
        platform_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
