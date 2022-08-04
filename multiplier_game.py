#!python3

# This script merges two acquisition configuration files

import json
import argparse
import sys
import os
import re

from colorama import Fore
import random

KEY_SCORE = "score"
KEY_LEVEL = "level"

DEFAULT_LEVEL = 1
DEFAULT_SCORE = 0

DEFAULT_SAVE_FILEPATH = "save.json"
DEFAULT_MSG_COLOR = Fore.CYAN


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only_square", help="only ask squares", action='store_true', default=False)
    parser.add_argument(
        "--save", help="score file", type=str, default=DEFAULT_SAVE_FILEPATH)
    return parser.parse_args()


def print_message(msg: str, color: str):
    print(f"{color}{msg}{Fore.RESET}")


def print_score(score: int, color=Fore.CYAN):
    print(f"{color}[SCORE = {score}{Fore.RESET}]")


class PlayerData():
    def __init__(self, level=DEFAULT_LEVEL, score=DEFAULT_SCORE):
        self.level = level
        self.score = score

    def __init__(self, json_data={}):
        self.level = json_data.get(KEY_LEVEL, DEFAULT_LEVEL)
        self.score = json_data.get(KEY_SCORE, DEFAULT_SCORE)

    def Print(self):
        print(self.level)
        print(self.score)


class GameLoader():
    def GetDefaultPlayer(self):
        i = 1
        player = f"Player{i}"
        while (player in self.players_data):
            i += 1
        return f"Player{i}"

    def InputPlayer(self):
        print_message("Bienvenue dans le jeu des multiplications",
                      DEFAULT_MSG_COLOR)
        print_message("Comment t'appelles-tu ?", DEFAULT_MSG_COLOR)
        input_player = str(input())
        if input_player:
            self.player = input_player
        print()

    def WelcomePlayer(self, color=DEFAULT_MSG_COLOR):
        print(f"{color}Bonjour {Fore.YELLOW}{self.player} {color}!{Fore.RESET}")
        print_message("Prêt à jouer avec moi ? C'est parti !\n", color)

    def FillPlayerName(self):
        self.InputPlayer()
        self.WelcomePlayer()

    def __init__(self, save_filepath=DEFAULT_SAVE_FILEPATH):
        # load JSON data
        json_save_data = {}
        try:
            with open(save_filepath) as json_save_file:
                try:
                    json_save_data = json.loads(json_save_file)
                except:
                    print(f"Cannot load save file [{save_filepath}]")
        except:
            print(f"No save file provided")

        # turn JSON data into PLAYER DATA
        self.players_data = {}
        for player, player_json_data in json_save_data.items():
            self.players_data[player] = PlayerData(player_json_data)

        # set default player
        self.player = self.GetDefaultPlayer()

        # fill player name
        self.FillPlayerName()

        # load player data
        self.player_data = self.players_data.get(self.player, PlayerData())


def fill_player_name(color: str):
    input_str = str(input())
    msg = "Bonjour "+input_str+" !"
    print_message(msg, color)

    print_message("Prêt à jouer avec moi ? C'est parti !", color)


# class Level:
#     def __init__(self, multiplier=1, completed=False, score=0):
#         self.completed = completed
#         self.multiplier = multiplier
#         self.score = score


def main(args):
    try:
        GameLoader(args.save)

        # fill_player_name(DEFAULT_MSG_COLOR)

        # score = load_save_file(player)

        # current_score = 360  # 180

        # for i in range(1, 10):

        #     n = random.randint(1, 10)
        #     m = n if args.only_square else random.randint(1, 3)

        #     print(f"Combien fait {n}x{m} ?")
        #     no_answer = True
        #     answer_int = 0
        #     while (no_answer):
        #         answer = input()
        #         try:
        #             answer_int = int(answer)
        #             no_answer = False
        #         except:
        #             current_score -= 1
        #             print(
        #                 f"Je n'ai pas compris [{answer}], je ne comprends que les chiffres, recommence s'il te plaît")
        #             print_score(current_score)
        #             print()
        #             continue

        #     if answer_int == n*m:
        #         print("BRAVO")
        #         # print("\U0001F923")
        #         current_score += 10
        #         print_score(current_score)
        #         print()
        #     else:
        #         print(f"ce n'était pas la bonne réponse, {n}x{m} = {n*m}")
        #         current_score -= 10
        #         print_score(current_score)
        #         print()

        # while (current_score > 0):
        #     print("level")

        #     print("ask_question")
        #     print("get answer")
        #     print("check if good")
        #     add_score or decrease score depending on answer

        #     if level.completed then
        #     print

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == '__main__':
    flags = get_args()
    main(flags)
