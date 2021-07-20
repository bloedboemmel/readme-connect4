import re
import os
import os.path
import sys
import ast
from enum import Enum
from datetime import datetime
from connect4 import connect4
import yaml
from github import Github

import src.markdown as markdown
import src.selftest as selftest
import src.mockGithub as mockGithub

RED = 1
YELLOW  = 2

class Action(Enum):
    UNKNOWN = 0
    MOVE = 1
    NEW_GAME = 2


def update_top_moves(user):
    """Adds the given user to the top moves file"""
    with open('data/top_moves.txt', 'r') as file:
        contents = file.read()
        dictionary = ast.literal_eval(contents)

    if user not in dictionary:
        dictionary[user] = 1 # First move
    else:
        dictionary[user] += 1

    with open('data/top_moves.txt', 'w') as file:
        file.write(str(dictionary))


def update_last_moves(line):
    """Adds the given line to the last moves file"""
    with open('data/last_moves.txt', 'r+') as last_moves:
        content = last_moves.read()
        last_moves.seek(0, 0)
        last_moves.write(line.rstrip('\r\n') + '\n' + content)


def replace_text_between(original_text, marker, replacement_text):
    """Replace text between `marker['begin']` and `marker['end']` with `replacement`"""
    delimiter_a = marker['begin']
    delimiter_b = marker['end']

    if original_text.find(delimiter_a) == -1 or original_text.find(delimiter_b) == -1:
        return original_text

    leading_text = original_text.split(delimiter_a)[0]
    trailing_text = original_text.split(delimiter_b)[1]

    return leading_text + delimiter_a + replacement_text + delimiter_b + trailing_text


def parse_issue(title):
    """Parse issue title and return a tuple with (action, <move>)"""
    if title.lower() == 'connect4: start new game':
        return (Action.NEW_GAME, None)

    if 'connect4: put' in title.lower():
        match_obj = re.match('Connect4: Put ([1-8])', title, re.I)

        source = match_obj.group(1)

        return (Action.MOVE, int(source))

    return (Action.UNKNOWN, title)


def main(issue, issue_author, repo_owner):
    action = parse_issue(issue.title)
    print(action)
    Conn = connect4()

    with open('data/settings.yaml', 'r') as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)

    if action[0] == Action.NEW_GAME:
        if os.path.exists('games/current.p') and issue_author != repo_owner:
            issue.create_comment(settings['comments']['invalid_new_game'].format(author=issue_author))
            issue.edit(state='closed')
            return False, 'ERROR: A current game is in progress. Only the repo owner can start a new game'

        issue.create_comment(settings['comments']['successful_new_game'].format(author=issue_author))
        issue.edit(state='closed')

        with open('data/last_moves.txt', 'w') as last_moves:
            last_moves.write('Start game: ' + issue_author)

        # Create new game
        Conn.create_newgame()
        #game.headers['Event'] = repo_owner + '\'s Online Open Connect4 Tournament'
        #game.headers['Site'] = 'https://github.com/' + os.environ['GITHUB_REPOSITORY']
        #game.headers['Date'] = datetime.now().strftime('%Y.%m.%d')
        #game.headers['Round'] = '1'

    elif action[0] == Action.MOVE:
        if not os.path.exists('games/current.p'):
            return False, 'ERROR: There is no game in progress! Start a new game first'

        # Load game from "games/current.pgn"
        Conn = connect4()
        Valid_Moves = Conn.valid_moves()
        with open('data/last_moves.txt') as moves:
            line = moves.readline()
            last_player = line.split(':')[1].strip()
            last_move   = line.split(':')[0].strip()



        # Check if player is moving twice in a row
        if last_player == issue_author and 'Start game' not in last_move:
            issue.create_comment(settings['comments']['consecutive_moves'].format(author=issue_author))
            issue.edit(state='closed', labels=['Invalid'])
            return False, 'ERROR: Two moves in a row!'
        move = action[1]
        # Check if move is valid
        if move not in Valid_Moves:
            issue.create_comment(settings['comments']['invalid_move'].format(author=issue_author, move=action[1]))
            issue.edit(state='closed', labels=['Invalid'])
            return False, f'ERROR: Move "{move}" is invalid!'

        # Check if board is valid
        if not Conn.has_space_left():
            issue.create_comment(settings['comments']['invalid_board'].format(author=issue_author))
            issue.edit(state='closed', labels=['Invalid'])
            return False, 'ERROR: Board is invalid!'


        issue_labels = ['Red' if RED == Conn.whosturn() else 'Yellow']
        issue.create_comment(settings['comments']['successful_move'].format(author=issue_author, move=action[1]))
        issue.edit(state='closed', labels=issue_labels)

        update_last_moves(action[1] + ': ' + issue_author)
        update_top_moves(issue_author)

        # Perform move
        Conn.move(move)


    elif action[0] == Action.UNKNOWN:
        issue.create_comment(settings['comments']['unknown_command'].format(author=issue_author))
        issue.edit(state='closed', labels=['Invalid'])
        return False, f'ERROR: "{action[1]}" Unknown action'



    with open('README.md', 'r') as file:
        readme = file.read()
        readme = replace_text_between(readme, settings['markers']['board'], '{chess_board}')
        readme = replace_text_between(readme, settings['markers']['moves'], '{moves_list}')
        readme = replace_text_between(readme, settings['markers']['turn'],  '{turn}')
        readme = replace_text_between(readme, settings['markers']['last_moves'], '{last_moves}')
        readme = replace_text_between(readme, settings['markers']['top_moves'], '{top_moves}')

    with open('README.md', 'w') as file:
        # Write new board & list of movements
        file.write(readme.format(
            chess_board=markdown.board_to_markdown(Conn.grid),
            moves_list=markdown.generate_moves_list(Conn.grid),
            turn=('red' if Conn.whosturn() == RED else 'yellow'),
            last_moves=last_moves,
            top_moves=markdown.generate_top_moves()))

    return True, ''


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--self-test':
        selftest.run(main)
        sys.exit(0)
    else:
        repo = Github(os.environ['GITHUB_TOKEN']).get_repo(os.environ['GITHUB_REPOSITORY'])
        issue = repo.get_issue(number=int(os.environ['ISSUE_NUMBER']))
        issue_author = '@' + issue.user.login
        repo_owner = '@' + os.environ['REPOSITORY_OWNER']

    ret, reason = main(issue, issue_author, repo_owner)

    if ret == False:
        sys.exit(reason)
