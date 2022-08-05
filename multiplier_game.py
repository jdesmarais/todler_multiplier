#!python3

# This script merges two acquisition configuration files

import json
import argparse
import sys
import os
import shutil
import re

from colorama import Fore
import random


KEY_SCORE = "score"
KEY_LEVEL = "level"

DEFAULT_LEVEL = 1
DEFAULT_SCORE = 0

DEFAULT_MAX_SECOND_MULTIPLIER = 12
DEFAULT_TOTAL_NB_QUESTIONS = 20
DEFAULT_CORRECT_ANSWER_SCORE = 10
DEFAULT_INCORRECT_ANSWER_SCORE = 10

DEFAULT_CURRENT_TABLE_PROBABILITY = 0.7

DEFAULT_VERBOSE = False

DEFAULT_SAVE_FILEPATH = "save.json"
DEFAULT_MSG_COLOR = Fore.CYAN


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--only_square", help="only ask squares", action='store_true', default=False)

    parser.add_argument(
        "--max_second_multiplier", help="maximum multiplier", type=int, default=12)

    parser.add_argument(
        "--verbose", help="debugging messages", action='store_true', default=False)
    parser.add_argument(
        "--save", help="score file", type=str, default=DEFAULT_SAVE_FILEPATH)
    return parser.parse_args()


def print_message(msg: str, color: str):
    print(f"{color}{msg}{Fore.RESET}")


def print_score(score: int, color=Fore.CYAN):
    print(f"{color}[SCORE = {score}{Fore.RESET}]")


class PlayerData():
    def FromDict(self, dict_data: dict):
        self.level = dict_data.get(KEY_LEVEL, DEFAULT_LEVEL)
        self.score = dict_data.get(KEY_SCORE, DEFAULT_SCORE)

    def ToDict(self):
        return {
            KEY_LEVEL: self.level,
            KEY_SCORE: self.score
        }

    def __init__(self, json_data={}):
        self.FromDict(json_data)

    def Print(self):
        print(self.level)
        print(self.score)


class GameLoader():
    def __GetDefaultPlayer(self):
        i = 1
        player = f"Player{i}"
        while (player in self.players_data):
            i += 1
        return f"Player{i}"

    def __InputPlayer(self):
        print_message("Bienvenue dans le jeu des multiplications",
                      DEFAULT_MSG_COLOR)
        print_message("Comment t'appelles-tu ?", DEFAULT_MSG_COLOR)
        input_player = str(input())
        if input_player:
            self.player = input_player
        print()

    def __WelcomePlayer(self, color=DEFAULT_MSG_COLOR):
        print(f"{color}Bonjour {Fore.YELLOW}{self.player} {color}!{Fore.RESET}")
        print_message("Prêt à jouer avec moi ? C'est parti !\n", color)

    def __FillPlayerName(self):
        self.__InputPlayer()
        self.__WelcomePlayer()

    def __init__(self, save_filepath=DEFAULT_SAVE_FILEPATH):
        # load JSON data
        json_save_data = {}
        try:
            with open(save_filepath) as json_save_file:
                try:
                    json_save_data = json.loads(json_save_file.read())
                except:
                    print(f"Cannot load save file [{save_filepath}]")
        except:
            print(f"No save file provided")

        # turn JSON data into PLAYER DATA
        self.players_data = {}
        for player, player_json_data in json_save_data.items():
            self.players_data[player] = PlayerData(player_json_data)

        # set default player
        self.player = self.__GetDefaultPlayer()

        # fill player name
        self.__FillPlayerName()

        # load player data
        self.player_data = self.players_data.get(self.player, PlayerData())

    def GetPlayer(self):
        return self.player

    def GetScore(self):
        return self.player_data.score

    def GetLevel(self):
        return self.player_data.level

    def __UpdatePlayerData(self, player: str, player_data: PlayerData):
        self.players_data[player] = player_data

    def __Write(self, save_filepath=DEFAULT_SAVE_FILEPATH, verbose=DEFAULT_VERBOSE):
        if os.path.exists(save_filepath) & os.path.isfile(save_filepath):
            shutil.copyfile(save_filepath, f"{save_filepath}~")
            if verbose:
                print(
                    f"Existing save file successfully copied : {save_filepath} -> {save_filepath}~")

        with open(save_filepath, "w") as write_file:
            json_data = {}
            for player, player_data in self.players_data.items():
                json_data[player] = player_data.ToDict()

            json.dump(json_data, write_file, indent=4)

            if verbose:
                print(f"Player data successfully written to [{save_filepath}]")

    def Save(self, save_filepath, player: str, player_data: PlayerData, verbose=DEFAULT_VERBOSE):
        self.__UpdatePlayerData(player, player_data)
        self.__Write(save_filepath, verbose)

    def Print(self):
        print(f"---------------------------------")
        print(f"Game loader")
        print(f"---------------------------------")
        print(f"Player       : {self.GetPlayer()}")
        print(f"Player score : {self.GetScore()}")
        print(f"Level        : {self.GetLevel()}")
        print()


class Level():
    def __InitializeMandatoryQuestions(self, multiplier: int, max_second_multiplier: int):
        return [f"{multiplier}x{i}" for i in range(2, max(2, max_second_multiplier+1))]

    def __init__(self,
                 multiplier=1,
                 max_second_multiplier=DEFAULT_MAX_SECOND_MULTIPLIER,
                 correct_answer_score=DEFAULT_CORRECT_ANSWER_SCORE,
                 incorrect_answer_score=DEFAULT_INCORRECT_ANSWER_SCORE):
        self.multiplier = multiplier

        self.total_nb_questions = (max_second_multiplier-2+1)*2

        self.completed = False
        self.correct_answer_score = correct_answer_score
        self.incorrect_answer_score = incorrect_answer_score

        self.mandatory_questions = self.__InitializeMandatoryQuestions(
            self.multiplier, max_second_multiplier)

    def Print(self):
        print(f"---------------------------------")
        print(f"Level")
        print(f"---------------------------------")
        print(f"multiplier             : {self.multiplier}")
        print(f"total nb questions     : {self.total_nb_questions}")
        print(f"completed              : {self.completed}")
        print(f"correct_answer_score   : {self.correct_answer_score}")
        print(f"incorrect_answer_score : {self.incorrect_answer_score}")
        print(f"mandatory_questions    : {self.mandatory_questions}")
        print()


def main(args):
    try:
        game_loader = GameLoader(args.save)
        player = game_loader.GetPlayer()
        player_score = game_loader.GetScore()
        level_id = game_loader.GetLevel()

        if args.verbose:
            game_loader.Print()

        level = Level(multiplier=level_id,
                      max_second_multiplier=args.max_second_multiplier,
                      correct_answer_score=DEFAULT_CORRECT_ANSWER_SCORE,
                      incorrect_answer_score=DEFAULT_INCORRECT_ANSWER_SCORE)

        if args.verbose:
            level.Print()

        level_id += 1

        game_loader.Save(args.save,
                         player,
                         PlayerData({
                             KEY_LEVEL: level_id,
                             KEY_SCORE: player_score}),
                         args.verbose)

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
