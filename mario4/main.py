import sys
from turtledemo import clock
import pygame
import os


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # Если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    intro_text = ["Игра про человечка", "Нажмите что угодно чтобы начать",
                  "Правила игры",
                  "Используйте стрелки для перемещения",
                  "Всё"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    a = list(map(lambda x: x.ljust(max_width, '.'), level_map))
    return a


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y % 12][x % 12] == '.':
                Tile('grass', x, y)
            elif level[y % 12][x % 12] == '#':
                Tile('wall', x, y)
            elif level[y % 12][x % 12] == '@':
                Tile('grass', x, y)
                new_player = Player(x % 12, y % 12)
    # вернем игрока, а также размер поля в клетках
    return new_player, x % 12, y % 12


def repin(original_string, index, new_char):
    if index < 0 or index >= len(original_string):
        raise IndexError("Индекс находится вне допустимого диапазона")
    # Создаем новую строку с замененным символом
    new_string = original_string[:index] + new_char + original_string[index + 1:]
    return new_string


if __name__ == '__main__':
    filename = 'levelmap'
    file_path = os.path.join('data/', filename)
    if not os.path.isfile(file_path):
        print(f"Ошибка: Карта '{filename}' не существует.")
        sys.exit()

    maplist = load_level(filename)
    player = None
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    for i in range(len(maplist)):
        if '@' in maplist[i]:
            coordI = i
            coordJ = maplist[i].find('@')
            break
    pygame.init()
    FPS = 50
    clock = pygame.time.Clock()
    size = width, height = 550, 550
    screen = pygame.display.set_mode(size)
    start_screen()
    running = True
    tile_images = {
        'wall': load_image('box.png'),
        'grass': load_image('grass.png'),
        'black': load_image('black.png')
    }
    player_image = load_image('mar.png')
    tile_width = tile_height = 50
    player, level_x, level_y = generate_level(load_level(filename))
    camera = Camera()

    while running:
        for event in pygame.event.get():
            # При закрытии окна
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if maplist[coordI % 11][(coordJ - 1) % 11] == '.':
                        maplist[coordI] = repin(maplist[coordI % 11], coordJ % 11, '.')
                        maplist[coordI] = repin(maplist[coordI % 11], (coordJ - 1) % 11, '@')
                        coordJ -= 1

                elif event.key == pygame.K_RIGHT:
                    if maplist[coordI % 11][(coordJ + 1) % 11] == '.':
                        maplist[coordI] = repin(maplist[coordI % 11], coordJ % 11, '.')
                        maplist[coordI] = repin(maplist[coordI % 11], (coordJ + 1) % 11, '@')
                        coordJ += 1

                elif event.key == pygame.K_UP:
                    if maplist[(coordI - 1) % 11][coordJ % 11] == '.':
                        maplist[coordI] = repin(maplist[coordI % 11], coordJ % 11, '.')
                        maplist[coordI - 1] = repin(maplist[(coordI - 1) % 11], coordJ % 11, '@')
                        coordI -= 1

                elif event.key == pygame.K_DOWN:
                    if maplist[(coordI + 1) % 11][coordJ % 11] == '.':
                        maplist[coordI] = repin(maplist[coordI % 11], coordJ % 11, '.')
                        maplist[coordI + 1] = repin(maplist[(coordI + 1) % 11], coordJ % 11, '@')
                        coordI += 1

                player.rect.topleft = (coordJ % 11 * tile_width + 15, coordI % 11 * tile_height + 5)
                player, level_x, level_y = generate_level(maplist)
                pygame.display.flip()

                camera.update(player)
                for sprite in all_sprites:
                    camera.apply(sprite)

            pygame.display.flip()
            all_sprites.draw(screen)

    pygame.quit()