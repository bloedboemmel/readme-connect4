import pickle
from datetime import datetime


def save_currentgame(grid, is_finished, plays):
    pickle.dump({'grid': grid, 'is_finished': is_finished, 'plays': plays}, open("games/current.p", "wb"))


def load_lastgame():
    try:
        game = pickle.load(open("games/current.p", "rb"))
        grid = game['grid']
        is_finished = game['is_finished']
        plays = game['plays']
        return grid, is_finished, plays
    except:
        return create_newgame()


def wongame(grid, is_finished, plays):

    pickle.dump({'grid': grid, 'is_finished': is_finished, 'plays': plays},
                                 open("games/" + datetime.now().strftime("%m_%d_%Y-%H_%M_%S") + ".p",
                                      "wb"))
    return create_newgame()


def create_newgame():
    grid = [[0 for col in range(7)] for row in range(6)]
    is_finished = False
    plays = 2
    save_currentgame(grid, is_finished, plays)
    return grid, is_finished, plays


def iswonornot(grid, color):
    for row in grid:
        count = 0
        for col in row:
            if col == color:
                count += 1
            else:
                count = 0
            if count == 4:
                print('True1')
                return True
    for j in range(len(grid[0])):
        count = 0
        for i in range(len(grid)):
            if grid[i][j] == color:
                count += 1
            else:
                count = 0
            if count == 4:
                print('True2')
                return True

    saver = []
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == color:
                if recur_checker(grid, True, row + 1, col - 1, color, 3) | recur_checker(grid, False, row + 1, col + 1, color, 3):
                    print('True3')
                    return True

    return False


def recur_checker(grid, down, row, col, color, howmanyleft):
    if howmanyleft == 0:
        return True
    if (row >= len(grid)) | (col >= len(grid[0])) | (row < 0) | (col < 0):
        return False

    if grid[row][col] != color:
        return False
    if grid[row][col] == color:
        if down:
            return recur_checker(grid, down, row + 1, col - 1, color, howmanyleft - 1)
        else:
            return recur_checker(grid, down, row + 1, col + 1, color, howmanyleft - 1)
    return False


def has_space_left(grid):
    for row in grid:
        for col in row:
            if col == 0:
                return True
    return False

def main(x):
    x -= 1
    grid, is_finished, plays = load_lastgame()
    if (x >= len(grid[0]))| (x < 0):
        return whosturn()



    Found = False
    for row in grid:
        if row[x] == 0:
            grid[grid.index(row)][x] = plays
            Found = True
            break

    if not Found:
        plays += 1
        print("Can't put it there")

    plays = (plays % 2) + 1

    if iswonornot(grid, plays) :
        for row in reversed(grid):
            print(row)
        grid, is_finished, plays = wongame(grid, is_finished, plays)
    elif not has_space_left(grid):
        for row in reversed(grid):
            print(row)
        grid, is_finished, plays = wongame(grid, is_finished, plays)

    else:
        save_currentgame(grid, is_finished, plays)

    for row in reversed(grid):
        print(row)

    Can_Play = []
    for i in range(len(grid[0])):
        if grid[-1][i] == 0:
            Can_Play.append(i+1)


    return plays, Can_Play
def whosturn():
    grid, is_finished, play = load_lastgame()
    Can_Play = []
    for i in range(len(grid[0])):
        if grid[-1][i] == 0:
            Can_Play.append(i + 1)
    return play, Can_Play
if __name__ == '__main__':
    color, Can_Play = whosturn()
    while True:
        x = int(input(f'X for {color}, possible {Can_Play}::'))
        color, Can_Play = main(x)
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
