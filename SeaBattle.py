from random import randint


class BoardException(Exception):  # common class of exceptions to catch mistakes
    pass


class BoardOutException(BoardException):  # exception to out-of-range shot
    def __str__(self):
        return "Внимание! Вы нанесли удар за границу доски!"


class BoardCellException(BoardException):  # exception to used cell shot
    def __str__(self):
        return "Внимание! Вы уже стреляли по этим координатам!"


class BoardWrongShipException(BoardException):  # exception to check ship allocation, hidden from user
    pass


class Dot:                     # class for coordinates of dots on game field
    def __init__(self, x, y):  # attributes 
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
        
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, direction):  # attributes of ship instance
        self.bow = bow               # starting point of ship instance (by fact, instance of Dot-class)
        self.length = length         # quantity of dots representing ship instance on board
        self.direction = direction   # orientation of ship instance on board, horizontal/vertical
        self.lives = length
    
    @property                  # use of decorator @property to hid inner structure of method
    def dots(self):
        ship_dots = []
        for i in range(self.length):  # setting orientation of ship instance on board
            cur_x = self.bow.x        # attribute x of Dot-class instance
            cur_y = self.bow.y        # attribute y of Dot-class instance
            
            if self.direction == 0:   # vertical orientation by adding ship length  
                cur_x += i            # to bow x-coordinate
                
            elif self.direction == 1:  # horizontal orientation by adding ship length
                cur_y += i             # to bow y-coordinate
                
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def struck(self, strike):        # method to show whether we hit a ship or not
        return strike in self.dots


class Board:
    def __init__(self, hid=False, size=9):
        self.size = size
        self.hid = hid
        
        self.count = 0      # quantity of struck ships
        self.field = [[" "] * size for _ in range(size)]  # attribute of two-dimensional array
                
        self.busy_dots = []  # list of occupied dots in field, whether by ships or hits made
        self.ships = []      # list of all ships in field
        
    def __str__(self):
        res = ""
        res += "    1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |"
        res += "\n   ——— ——— ——— ——— ——— ——— ——— ——— ———"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
            res += "\n   ——— ——— ——— ——— ——— ——— ——— ——— ———"
                    
        if self.hid:
            res = res.replace("▲", " ")
        return res
    
    def out(self, dot):  # method to define if dot is out of field range
        return not((0 <= dot.x < self.size) and (0 <= dot.y < self.size))
    
    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (0, -1),
            (-1, 1), (0, 0), (0, 1),
            (1, 0), (1, 1), (1, -1)   
        ]
        for dot in ship.dots:
            for dx, dy in around:
                cur = Dot(dot.x + dx, dot.y + dy)
                if not(self.out(cur)) and cur not in self.busy_dots:
                    if verb:       # method puts '.' around ship to show busy cells
                        self.field[cur.x][cur.y] = "."
                    self.busy_dots.append(cur)
                                      
    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy_dots:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "▲"
            self.busy_dots.append(dot)
            
        self.ships.append(ship)
        self.contour(ship)
        
    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
            
        if dot in self.busy_dots:
            raise BoardCellException()
            
        self.busy_dots.append(dot)
    
        for ship in self.ships:
            if ship.struck(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "V"
        print("Мимо!")
        return False
    
    def begin(self):
        self.busy_dots = []
        
    def defeat(self):
        return self.count == len(self.ships)


class Player:  # Parent class for all players
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
        
    def ask(self):  # Method should be defined in derived classes of players. Now it's an error.
        raise NotImplementedError
        
    def move(self):
        while True:  # Endless cycle for making moves
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)
                
                
class AI(Player):  # Child class of computer enemy
    def ask(self):
        move = Dot(randint(0, 8), randint(0, 8))
        print(f"Ход компьютера: {move.x + 1} {move.y + 1}")
        return move


class User(Player):  # Child class of user
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            
            if len(cords) != 2:  # Checking if player enters 2 coordinates
                print("Введите 2 координаты!")
                continue
                
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):  # Checking if player enters numbers
                print("Введите числа!")
                continue
                
            x, y = int(x), int(y)
            
            return Dot((x - 1), (y - 1))


class Game:  # Main class of the game defining players, boards and methods of their interaction
    def __init__(self, size=9):
        self.ship_nums = [3, 3, 2, 2, 2, 1, 1, 1, 1]  # Setting numbers of ships and their size on the board
        self.size = size
        player = self.random_board()
        comp = self.random_board()
        comp.hid = True
        
        self.ai = AI(comp, player)
        self.pl = User(player, comp)
        
    def try_board(self):  # Method to create random board and set ships on it
        board = Board(size=self.size)
        attempts = 0  # Counting attempts to create board
        for length in self.ship_nums:
            while True:
                attempts += 1
                if attempts > 2000:  # If attempts exceed some number of tries the board should be recreated
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    @staticmethod
    def greet():
        print("+++++++++++++++++++++++++++++++++++++++++++++")
        print('   Приветствуем Вас в игре "Морской Бой"!    ')
        print("+++++++++++++++++++++++++++++++++++++++++++++")
        print(" Выполняйте ходы по очереди с AI-соперником. ")
        print("     Ход состоит из ввода 2-х координат:     ")
        print("     Х - номер строки, У - номер столбца.    ")
        print("Необходимо уничтожить все корабли противника.")
        print("             Желаем Вам удачи!!!             ")
        print("+++++++++++++++++++++++++++++++++++++++++++++")

    @staticmethod
    def print_boards(first, second):              # Method outputs two boards next to each other
        ai_board_list = first.split("\n")         # Splitting arrays into strings
        pl_board_list = second.split("\n")
        max_width = max(map(len, ai_board_list))  # Defining max size of string
        max_len = max(len(ai_board_list), len(pl_board_list))   # Max size of two split arrays
        ai_board_list += [""] * (max_len - len(ai_board_list))  #
        pl_board_list += [""] * (max_len - len(pl_board_list))
        two_boards = []
        for ai, pl in zip(ai_board_list, pl_board_list):
            two_boards.append(f" {ai:{max_width}}   |:|   {pl:{max_width}}")

        return '\n'.join(two_boards)

    def loop(self):
        num = 0
        while True:
            print("-" * 88)
            user_board = "Доска пользователя:\n\n" + str(self.pl.board)
            ai_board = "Доска компьютера:\n\n" + str(self.ai.board)
            print(self.print_boards(user_board, ai_board))
            if num % 2 == 0:
                print("Ходит игрок")
                repeat = self.pl.move()
            else:
                print("Ходит компьютер")
                repeat = self.ai.move()
                    
            if repeat:
                num -= 1
                    
            if self.ai.board.defeat():
                self.print_boards(user_board, ai_board)
                print("-" * 88)
                print("Выиграл игрок")
                break

            if self.pl.board.defeat():
                self.print_boards(user_board, ai_board)
                print("-" * 88)
                print("Выиграл компьютер")
                break
            num += 1
                
    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
