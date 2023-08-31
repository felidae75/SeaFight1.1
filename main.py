import random
from random import randint
import prettytable
from prettytable import PrettyTable  # Модуль таблиц. Чтобы игровые поля стояли рядом


# Классы исключений
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Клетка уже поражена"


# Сие исключение используется в расстановке кораблей
class BoardWrongShipException(BoardException):
    # def __str__(self):
    #     return "test"
    pass


class Dots:  # Класс ячеек
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):     # Эта фигня для сравнения ячеек без обращения к координатам
        return self.x == other.x and self.y == other.y

    # def status_square(self, ships_dots, shot_dots):
    #     if Dots(self.x, self.y) in ships_dots:
    #         # print(self.x, self.y)
    #         return 1
    #         # Корабль
    #     elif Dots(self.x, self.y) in shot_dots:
    #         return 2
    #         # Стрельнул в уже отстрелянную
    #     else:
    #         return -1
    #         # Промах
    # Оно работало, конечно. Но ему для этого надо скармливать списки координат из игрового поля

    def is_dot_in_area(self, size):  # Проверка. Точка внутри игрового поля
        return 0 <= self.x < size and 0 <= self.y < size

    def __repr__(self):
        return f"Координаты: ({self.x}, {self.y})"

    def __str__(self):
        return f"Координаты: ({self.x}, {self.y})"

# a = Dots(1, 2)
# b = Dots(1, 3)
# c = Dots(1, 2)
# list = [Dots(1, 2), Dots(2, 3)]
#
# print(a, b, c)
# print(a == b, a == c)
# print(a in list, b in list)


class Ship:  # Класс корабля
    def __init__(self, len_ship, bow, direct):
        self.len_ship = len_ship     # Длина корабля
        self.bow = bow               # Координаты носа корабля
        self.direct = direct         # Направление корабля. Задаётся параметром 1 или 0
        self.lives = self.dots_ship  # Жизни корабля в виде клеток

    @property
    def dots_ship(self):  # Список координат корабля
        dots_ship_list = [self.bow]
        if self.len_ship > 1:
            for i in range(1, self.len_ship):
                cur_x = self.bow.x
                cur_y = self.bow.y
                if self.direct == 0:    # От носа по вертикали
                    cur_x += i
                elif self.direct == 1:  # От носа по горизонтали
                    cur_y += i
                dots_ship_list += [Dots(cur_x, cur_y)]
        return dots_ship_list

    @property
    def ship_contour(self):    # Координаты вокруг корабля
        near_ship = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        # Список "сдвигов", чтобы определить координаты
        contour = []
        for coord in self.dots_ship:
            for d_x, d_y in near_ship:
                cur = Dots(coord.x + d_x, coord.y + d_y)
                if cur not in self.dots_ship and cur.x >= 0 and cur.y >= 0:
                    contour.append(cur)
        # print(contur)
        # field = [["_"]*9 for _ in range(9)]
        # for coord in contur:
        #     field[coord.x][coord.y] = '+'
        # for i in range(len((field))):
        #     print(*field[i])
        return contour


class ShipsList:  # Класс для списка кораблей
    def __init__(self, ships_lens_list, size=6):
        self.ships_lens_list = ships_lens_list     # Список длин кораблей
        self.size = size                           # Размер игрового поля

    def try_make_ships_list(self):
        ships_list = []
        dots_all_ships = []
        contours_list = []
        # Список кораблей (класс Ship), список координат кораблей, список контуров кораблей

        def try_add_ship(dot_ship):  # Проверка, не задевает ли координата корабля другие корабли и контуры
            if dot_ship in dots_all_ships:
                # print("ship")
                raise BoardWrongShipException
            if dot_ship in contours_list:
                # print('contour')
                raise BoardWrongShipException

        count = 0  # Счётчик для неудачных попыток

        for len_ship in self.ships_lens_list:
            while True:
                ship = Ship(len_ship=len_ship, bow=Dots(randint(0, self.size-1), randint(0, self.size-1)), direct=randint(0, 1))
                contour = ship.ship_contour  # Координаты вокруг корабля
                try:
                    for dot in ship.dots_ship:
                        # Проверка, что координата внутри игрового поля
                        if not dot.is_dot_in_area(size=self.size):
                            raise BoardWrongShipException
                        try_add_ship(dot)  # Проверка, что корабли не задевают друг друга
                        dots_all_ships += [dot]
                        contours_list += contour
                    ships_list.append(ship)
                    count -= 1
                    break
                except BoardException:
                    count += 1
                    if count > 100:
                        return None
                    continue
        return ships_list

    @property
    def random_add_ships(self):
        # Функция, чтобы перезапускать расстановку кораблей
        # Да, такой декоратор. Но мне влом ставить скобки к ней, она ж всё равно работает и как свойство
        ships_list = None
        dots_all_ships = []
        while ships_list is None:
            ships_list = self.try_make_ships_list()
        for ship in ships_list:
            dots_all_ships += ship.dots_ship
        # print(dots_all_ships)
        return ships_list, dots_all_ships
        # Список кораблей класса Ship, список координат кораблей отдельно от класса


# list1 = [2, 1, 1]
# ships = ShipsList(ships_lens_list=list1)
# ships.random_add_ships
# print(ships)


class Board:        # Класс игровой доски
    def __init__(self, lens_ships, size=6):
        self.size = size                 # Размер доски
        self.lens_ships = lens_ships     # Список длин кораблей

        self.ships_list, self.dots_all_ships = ShipsList(size=self.size, ships_lens_list=lens_ships).random_add_ships
        # Список кораблей, уже красиво расставленных, и их координат

        self.shot_dots = []  # Список для отстрелянных клеток

        self.field = [["_"] * self.size for _ in range(self.size)]
        # Список списков для игрового поля
        self.count_ships = 0    # Счётчик потопленных кораблей для красивой статистики

    def __str__(self):     # Печать игрового поля
        print_field = " "
        simbols = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'
        simbols = simbols.split()
        for i in range(self.size):
            print_field += " | " + simbols[i]  # Чтобы были красивые буковки наверху
        print_field += " |\n"
        for i in range(self.size):
            print_field += f"\n {'%2d' % (i + 1)}   | " + " | ".join(self.field[i]) + " |    "
        return print_field

    def get_status(self, dot):          # Быстрый статус точки
        if dot in self.dots_all_ships:
            return 1
        elif dot in self.shot_dots:
            return False
        else:
            return -1
        # 1 - попал, -1 - мимо, False - сенсей, не туда

    def add_ship(self):               # Печать корабля на поле
        for dot in self.dots_all_ships:
            if self.field[dot.x][dot.y] == "_":  # Это if для итогов игры, чтобы показать, где неподбитые
                self.field[dot.x][dot.y] = "0"

    def make_contour_visible(self, ship):
        for dot in ship.ship_contour:
            if dot.x < self.size and dot.y < self.size:
                self.shot_dots.append(dot)
                self.field[dot.x][dot.y] = "+"

    def shot(self, dot):
        if self.get_status(dot) == 1:        # Попал
            self.field[dot.x][dot.y] = "X"
            self.shot_dots.append(dot)
            self.dots_all_ships.remove(dot)
            for ship in self.ships_list:
                if dot in ship.lives:       # Убираем жизни-клетки
                    ship.lives.remove(dot)
                    # print(ship.lives)
                    # print(ship.dots_ship)
                    if ship.lives:
                        print("\nКорабль подбит\n")
                        return True
                    else:
                        self.make_contour_visible(ship)
                        self.count_ships += 1
                        print("\nКорабль потоплен\n")
                        return False
        elif self.get_status(dot) == -1:     # Мимо
            self.field[dot.x][dot.y] = "+"
            self.shot_dots.append(dot)
            print("\nПромах\n")
            # print('miss')
            # print(dot)
            # print(self.shot_dots)
            return False

    def defeat(self):        # Поражение. Я - Кэп
        if not self.dots_all_ships:
            return True

    def stat(self):          # Большой нудный метод для красивой статистики
        stat = ''            # Запись статистики сразу в строку
        count = 0            # Счётчик количества кораблей
        for i in range(1, len(self.lens_ships)):
            if self.lens_ships[i] == self.lens_ships[i-1]:
                count += 1
                if self.lens_ships[i] == 1:
                    stat += f"{self.lens_ships[i]}-палубных: {len(self.lens_ships[i-1:])} цели\n"
                    break
            elif self.lens_ships[i] != self.lens_ships[i-1]:
                stat += f'{self.lens_ships[i-1]}-палубных: {count+1} целей/цели\n'
                count = 0
        return f"\nКоличество кораблей на поле:\n{stat}\nИз них потоплено: {self.count_ships}"


# lens_ship = [3, 2, 2, 1]
# board = Board(lens_ship)
# board.add_ship()
# print(board)
# x = int(input("x"))
# y = int(input("y"))
# d = Dots(x, y)
# board.shot(d)
# print(board)
# Божечки, оно работает так, как мне надо


class Player:               # Первому игроку приготовиться. Объявлен класс игрока
    def __init__(self, board, enemy, size=6):
        self.size = size    # Размер игрового поля
        self.board = board  # Своя доска
        self.enemy = enemy  # Доска противника

    def ask(self):
        # Я хер знает, зачем это нужно. Работает и просто объявление метода с pass
        # Метод переопределяется у игрока и бота
        raise NotImplementedError()

    def move(self):    # Ход. Через ask принимает координаты у игрока или бота
        while True:
            try:
                shot = self.ask()
                repeat = self.enemy.shot(shot)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):    # Клас бота
    list_shot = []   # Список попаданий для поиска соседних палуб

    @staticmethod
    def simbols_func(y):  # Перевод координат из букв. Чисто для принта статистики
        simbols = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'
        simbols = simbols.split()
        return simbols[y]

    def ask(self):
        while True:
            shot = Dots(randint(0, self.size - 1), randint(0, self.size - 1))
            if not self.enemy.get_status(shot):
                # Если случайный shot в уже отстрелянных клетках
                print("Компьютер думает...")
                continue
            elif self.list_shot and self.ai_want_win(self.list_shot):
                shot = self.ai_want_win(self.list_shot)
                # Эта весьма оригинальная функция и координаты достаёт, и проверяет, есть ли вообще, куда стрелять
                break
            else:
                break

        if self.enemy.get_status(shot) == 1:   # Если попал, координаты выстрела запоминаются
            self.list_shot.append(shot)

        print(f'Ход компьютера: {self.simbols_func(shot.y)} {shot.x + 1}')
        return shot

    def ai_want_win(self, list_shot):
        # Бот рандомно выбирает клетки рядом с поражённым бортом
        near_ship_ai = [
            (-1, 0),
            (0, -1), (0, 1),
            (1, 0)
        ]
        # Список "сдвигов" вокруг искомой точки
        near_shot_ai = []
        for doty in list_shot:
            for d_x, d_y in near_ship_ai:
                cur = Dots(doty.x + d_x, doty.y + d_y)
                if cur.is_dot_in_area(size=self.size) and self.enemy.get_status(cur):
                    near_shot_ai.append(cur)
                    # Проверка, есть ли вокруг клетки, куда можно выстрелить
        if not near_shot_ai:
            # Ежели доступных клеток нет, значит, кораблик присоединился к рыбам
            self.list_shot.clear()
            return False
        shot = random.choice(near_shot_ai)
        return shot


class User(Player):                 # Класс пользователя
    @staticmethod
    def simbols_func(y, simbols):   # Перевод координат в буквы
        for i in range(len(simbols)):
            if simbols[i] == y:
                return i

    def ask(self):
        simbols = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'
        simbols = simbols.split()
        while True:  # Запрос и проверка координат на вменяемость
            cords = input("Введите две координаты, начиная с латинской буквы, через пробел: ").lower()
            cords = cords.split()
            # print(cords)
            if len(cords) != 2:
                print("Введите две координаты через пробел")
                continue
            if cords[0] not in simbols or not (cords[1].isdigit()):
                print("Введите латинскую букву и число")
                continue
            x = int(cords[1]) - 1
            y = self.simbols_func(cords[0], simbols)  # Перевод буквы в число
            shot = Dots(x, y)
            if not shot.is_dot_in_area(size=self.size):
                raise BoardOutException
            elif not self.enemy.get_status(shot):
                raise BoardUsedException
                # Если прострелил прострелянное или выстрелил слишком далеко
            else:
                return shot


class Game:                  # Класс игры
    def __init__(self):
        self.lens_ship = None               # Длины кораблей
        self.size = self.greet_and_size()   # Размер игрового поля. Берётся из опроса пользователя
        player = self.go_go_board(is_visible=True)
        ai_player = self.go_go_board()

        # Игровые поля для игрока и бота. Отправляем все игроку и боту
        # is_visible - это видит ли пользователь свои корабли

        self.ai = AI(board=ai_player, enemy=player, size=self.size)
        self.us = User(board=player, enemy=ai_player, size=self.size)

    @staticmethod
    def greet_and_size():  # Приветствие и запрос размера
        size_input = None  # Переменная для размера

        print('\nПриветствуем в игре "Морской бой"!\n')
        print('Вы можете выбрать размер игрового поля\n')
        print("На доске 6-9 - семь кораблей\nНа дске 10-15 - десять кораблей\nНа доске 16-20 - шестнадцать кораблей\n")

        while True:
            try:
                size_input = int(input("Введите желаемый размер доски (число от 6 до 20): "))
                if not 5 < size_input < 21:
                    print("Не то число")
                    continue
            except ValueError:
                print("Это не число")
                continue
            break
        print("\nLet's mortal combat begin!\n")
        return size_input

    def go_go_board(self, is_visible=False):   # Создать игровое поле из класса игрового поля
        if self.size <= 9:                     # Разное количество кораблей для разных досок
            self.lens_ship = [3, 2, 2, 2, 1, 1]
        elif 9 < self.size < 15:
            self.lens_ship = [4, 4, 3, 3, 2, 2, 2, 1, 1]
        else:
            self.lens_ship = [5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1]

        board = Board(lens_ships=self.lens_ship, size=self.size)

        if is_visible:          # Для игрока его корабли будут видимыми
            board.add_ship()
        return board

    def print_arena(self):     # Печать игровых полей в виде таблицы. Используется модуль prettytable
        th = ["Доска компьютера:", "Доска пользователя:"]
        td = ["", "", self.ai.board, self.us.board, "", ""]  # Распределяется по количеству колонок в th
        columns = len(th)
        table = PrettyTable(th)
        td_data = td[:]
        while td_data:
            table.add_row(td_data[:columns])
            td_data = td_data[columns:]
        print(table, "\n")

    def loop_game(self):        # Игровой процесс
        print(f'На поле по {len(self.lens_ship)} кораблей\n')
        print("*"*10, "\n")
        count = 0           # Счётчик чёт-нечёт для очерёдности ходов
        while True:
            if count % 2 == 0:
                print(f"Статистика компьютера:\n{self.ai.board.stat()}\n")
                self.print_arena()
                print("Ходит пользователь\n")
                repeat = self.us.move()
                print('*'*20, "\n")
            else:
                print("Ходит компьютер\n")
                repeat = self.ai.move()
                print(f"Статистика пользователя:\n{self.us.board.stat()}\n")
                self.print_arena()
                print('*'*20, "\n")

            if repeat:
                count -= 1
                print("Повторный ход\n")

            if self.ai.board.defeat():
                print(f"\nСтатистика компьютера:\n{self.ai.board.stat()}\n")
                print(f"\nСтатистика пользователя:\n{self.us.board.stat()}\n")
                self.print_arena()
                print("\nПользователь выиграл\n")
                break

            if self.us.board.defeat():
                print(f"\nСтатистика компьютера:\n{self.ai.board.stat()}\n")
                print(f"\nСтатистика пользователя:\n{self.us.board.stat()}\n")
                self.ai.board.add_ship()     # add_ship - Показать оставшиеся у бота корабли
                self.print_arena()
                print("\nКомпьютер выиграл\n")
                break
            count += 1

    def start(self):
        self.loop_game()
        if input("\nЕсли хотите сыграть ещё, введите 'y': ").lower() == "y":
            game = Game()
            game.start()


game = Game()
game.start()


