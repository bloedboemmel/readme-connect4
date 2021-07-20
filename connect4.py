import pickle
from datetime import datetime


class connect4():
    def __init__(self):
        self.grid, self.is_finished, self.plays = self.load_lastgame()

    def save_currentgame(self):
        pickle.dump({'grid': self.grid, 'is_finished': self.is_finished, 'plays': self.plays},
                    open("games/current.p", "wb"))

    def load_lastgame(self):
        try:
            game = pickle.load(open("games/current.p", "rb"))
            grid = game['grid']
            is_finished = game['is_finished']
            plays = game['plays']
            return grid, is_finished, plays
        except:
            return self.create_newgame()

    def wongame(self):

        pickle.dump({'grid': self.grid, 'is_finished': self.is_finished, 'plays': self.plays},
                    open("games/" + datetime.now().strftime("%m_%d_%Y-%H_%M_%S") + ".p",
                         "wb"))
        return self.create_newgame()

    def create_newgame(self):
        self.grid = [[0 for col in range(7)] for row in range(6)]
        self.is_finished = False
        self.plays = 2
        self.save_currentgame()

    def iswonornot(self):
        for row in self.grid:
            count = 0
            for col in row:
                if col == color:
                    count += 1
                else:
                    count = 0
                if count == 4:
                    print('True1')
                    return True
        for j in range(len(self.grid[0])):
            count = 0
            for i in range(len(self.grid)):
                if self.grid[i][j] == color:
                    count += 1
                else:
                    count = 0
                if count == 4:
                    print('True2')
                    return True

        saver = []
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):
                if self.grid[row][col] == color:
                    if self.recur_checker(self.grid, True, row + 1, col - 1, color, 3) | self.recur_checker(self.grid, False, row + 1, col + 1, color, 3):
                        print('True3')
                        return True

        return False

    def recur_checker(self, grid, down, row, col, color, howmanyleft):
        if howmanyleft == 0:
            return True
        if (row >= len(grid)) | (col >= len(grid[0])) | (row < 0) | (col < 0):
            return False

        if grid[row][col] != color:
            return False
        if grid[row][col] == color:
            if down:
                return self.recur_checker(grid, down, row + 1, col - 1, color, howmanyleft - 1)
            else:
                return self.recur_checker(grid, down, row + 1, col + 1, color, howmanyleft - 1)
        return False

    def has_space_left(self):
        for row in self.grid:
            for col in row:
                if col == 0:
                    return True
        return False

    def whosturn(self):
        self.load_lastgame()
        Can_Play = []
        for i in range(len(self.grid[0])):
            if self.grid[-1][i] == 0:
                Can_Play.append(i + 1)
        return self.plays, Can_Play

    def move(self,x):
        x -= 1
        if (x >= len(self.grid[0])) | (x < 0):
            return self.whosturn()

        Found = False
        for row in self.grid:
            if row[x] == 0:
                self.grid[self.grid.index(row)][x] = self.plays
                Found = True
                break

        if not Found:
            self.plays += 1
            print("Can't put it there")

        self.plays = (self.plays % 2) + 1

        if self.iswonornot():
            for row in reversed(self.grid):
                print(row)
            self.wongame()
        elif not self.has_space_left():
            for row in reversed(self.grid):
                print(row)
            self.wongame()

        else:
            self.save_currentgame()

        for row in reversed(self.grid):
            print(row)

        Can_Play = []
        for i in range(len(self.grid[0])):
            if self.grid[-1][i] == 0:
                Can_Play.append(i + 1)

        return self.plays, Can_Play




if __name__ == '__main__':
    Conn = connect4()
    Conn.create_newgame()
    color, Can_Play = Conn.whosturn()

    while True:
        x = int(input(f'X for {color}, possible {Can_Play}::'))
        color, Can_Play = Conn.move(x)

        # color = (color % 2) + 1
        # x = int(input(f"X for {color}"))
        # Found = False
        # for row in grid:
        #     if row[x] == 0:
        #         grid[grid.index(row)][x] = color
        #         Found = True
        #         break
        # if not Found:
        #     color += 1
        #     print("Can't put it there")
        # for row in reversed(grid):
        #     print(row)

    print(f"{color} won")
