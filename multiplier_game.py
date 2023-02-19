#!python3

# This script merges two acquisition configuration files

import json
import argparse
import sys
import os
import shutil
import re
import emoji

from colorama import Fore
import random


KEY_SCORE = "score"
KEY_LEVEL = "level"

DEFAULT_LEVEL = 1
DEFAULT_SCORE = 0

DEFAULT_LEVEL_COLOR = Fore.GREEN

DEFAULT_MAX_SECOND_MULTIPLIER = 12
DEFAULT_TOTAL_NB_QUESTIONS = 20
DEFAULT_CORRECT_ANSWER_SCORE = 10
DEFAULT_INCORRECT_ANSWER_SCORE = 10

DEFAULT_CURRENT_TABLE_PROBABILITY = 0.7

DEFAULT_VERBOSE = False

DEFAULT_SAVE_FILEPATH = "save.json"
DEFAULT_MSG_COLOR = Fore.CYAN

KEY_VALID = "is_player_answer_valid"
KEY_PLAYER_ANSWER = "player_answer"
KEY_N = "n"
KEY_M = "m"

DEFAULT_LEVEL_ICONS = {
    1: emoji.emojize(":melon:"),
    2: emoji.emojize(":strawberry:"),
    3: emoji.emojize(":pineapple:"),
    4: emoji.emojize(":lemon:"),
    5: emoji.emojize(":tangerine:"),
    6: emoji.emojize(":grapes:"),
    7: emoji.emojize(":red_apple:"),
    8: emoji.emojize(":cherries:"),
    9: emoji.emojize(":kiwi_fruit:"),
    10: emoji.emojize(":watermelon:"),
    11: emoji.emojize(":coconut:"),
    12: emoji.emojize(":crown:"),
}

DEFAULT_WON_LEVEL_ICON = emoji.emojize(":trophy:")
DEFAULT_EXTRA_QUESTION_PRICE = emoji.emojize(":red_apple:")
DEFAULT_POINT_ICON = emoji.emojize(":green_apple:")


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
            player = f"Player{i}"
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
        return [i for i in range(2, max(2, max_second_multiplier+1))]

    def __init__(self,
                 multiplier=1,
                 max_second_multiplier=DEFAULT_MAX_SECOND_MULTIPLIER,
                 correct_answer_score=DEFAULT_CORRECT_ANSWER_SCORE,
                 incorrect_answer_score=DEFAULT_INCORRECT_ANSWER_SCORE):
        self.multiplier = multiplier
        self.max_second_multiplier = max_second_multiplier

        self.nb_asked_questions = 0

        self.total_nb_questions = (
            max_second_multiplier-2+1)*2 if multiplier > 2 else max_second_multiplier

        self.correct_answer_score = correct_answer_score
        self.incorrect_answer_score = incorrect_answer_score

        self.mandatory_questions = self.__InitializeMandatoryQuestions(
            self.multiplier, max_second_multiplier)

        self.answer_log = []

        self.current_level_question_threshold = DEFAULT_CURRENT_TABLE_PROBABILITY if not multiplier == 1 else 1.

    def IsComplete(self):
        return self.nb_asked_questions >= self.total_nb_questions

    def __GetLevelScore(self):
        nb_valid_answer = 0

        for answer_log in self.answer_log:
            if answer_log[KEY_VALID]:
                nb_valid_answer += 1

        return float(nb_valid_answer)/float(self.total_nb_questions)

    def IsValidated(self):
        all_questions_answered = self.IsComplete()
        all_mandatory_questions_validated = len(self.mandatory_questions) == 0
        good_overall_score = self.__GetLevelScore() > 0.90

        return (all_questions_answered and
                all_mandatory_questions_validated and
                good_overall_score)

    def __PrepareMultipliers(self):
        # we ask a question from the mandatory question of this level only if there are some left
        current_level_question = random.random(
        ) < self.current_level_question_threshold if len(self.mandatory_questions) > 0 else False

        n = self.multiplier
        m = self.multiplier

        if current_level_question:
            m = self.mandatory_questions[random.randint(
                0, len(self.mandatory_questions)-1)]
        else:
            n = random.randint(2, self.multiplier -
                               1) if self.multiplier > 2 else 2

            m = random.randint(2, self.max_second_multiplier+1)

            self.current_level_question_threshold += 0.1
            self.current_level_question_threshold = min(
                self.current_level_question_threshold, 1.0)

        return n, m

    def __PrintQuestion(self):
        n, m = self.__PrepareMultipliers()
        multiplier_str = f"{Fore.YELLOW}{n}x{m}{DEFAULT_MSG_COLOR}"
        print(f"{DEFAULT_MSG_COLOR}Combien font {multiplier_str} ?{Fore.RESET}")
        return n, m

    def __HandleUserInput(self):
        MAX_WRONG_INPUT = 3
        SCORE_DECREASE = 5

        # parse the answer
        answer_int = 0
        penalty = 0

        cannot_parse_input = True
        cannot_parse_input_i = 0

        while cannot_parse_input:
            answer = input()
            try:
                answer_int = int(answer)
                cannot_parse_input = False
            except:
                cannot_parse_input_i += 1
                print(
                    f"Je n'ai pas compris [{answer}], je ne comprends que les chiffres, recommence s'il te plaît")

                if cannot_parse_input_i > MAX_WRONG_INPUT:
                    penalty += SCORE_DECREASE
                    print(
                        f"Attention à ta réponse, ce n'est pas un nombre, c'est déjà la {cannot_parse_input_i}ème fois, je t'enlève {SCORE_DECREASE} points")

        return answer_int, penalty

    def __ComputeScore(self, n: int, m: int, player_answer: int, player_malus: int):
        score = -player_malus

        # check the answer
        correct_answer = player_answer == n*m
        if correct_answer:
            score += self.correct_answer_score
            print(f"BRAVO")
        else:
            print(
                f"Ce n'était pas la bonne réponse, {Fore.YELLOW}{n}x{m} = {n*m}{Fore.RESET}")

        # if this was a mandatory question, it is discarded
        if correct_answer and n == self.multiplier:
            if m in self.mandatory_questions:
                self.mandatory_questions.remove(m)

        return correct_answer, score

    def __LogAnswer(self,
                    is_player_answer_valid: bool,
                    player_answer: int,
                    n: int,
                    m: int):
        self.answer_log.append(
            {
                KEY_VALID: is_player_answer_valid,
                KEY_PLAYER_ANSWER: player_answer,
                KEY_N: n,
                KEY_M: m
            }
        )

    # def PrintLog(self):
    #     for answer_log in self.answer_log:
    #         msg = f"{"[-]" if answer_log.KEY_VALID else "[X]"}"
    #         print(f"")

    def AskQuestion(self):
        self.nb_asked_questions += 1
        n, m = self.__PrintQuestion()
        player_answer, player_penalty = self.__HandleUserInput()
        is_player_answer_valid, incremental_score = self.__ComputeScore(
            n, m, player_answer, player_penalty)
        self.__LogAnswer(is_player_answer_valid, player_answer, n, m)

        return is_player_answer_valid, incremental_score

    def Print(self):
        print(f"---------------------------------")
        print(f"Level")
        print(f"---------------------------------")
        print(f"multiplier             : {self.multiplier}")
        print(f"total nb questions     : {self.total_nb_questions}")
        print(f"correct_answer_score   : {self.correct_answer_score}")
        print(f"incorrect_answer_score : {self.incorrect_answer_score}")
        print(f"mandatory_questions    : {self.mandatory_questions}")
        print()


def main(args):

    # for key, value in DEFAULT_LEVEL_ICONS.items():
    #     print(f"{key} : {value}")

    # print(f"DEFAULT_WON_LEVEL_ICON: {DEFAULT_WON_LEVEL_ICON}")
    # print(f"DEFAULT_EXTRA_QUESTION_PRICE: {DEFAULT_EXTRA_QUESTION_PRICE}")
    # print(f"DEFAULT_POINT_ICON: {DEFAULT_POINT_ICON}")

    try:
        game_loader = GameLoader(args.save)
        player = game_loader.GetPlayer()
        player_score = game_loader.GetScore()
        level_id = game_loader.GetLevel()

        if args.verbose:
            game_loader.Print()

        print(
            f"Ton score actuel est de {Fore.LIGHTMAGENTA_EX}{player_score}{Fore.RESET} x {emoji.emojize(DEFAULT_POINT_ICON)}")

        while level_id <= args.max_second_multiplier:
            level = Level(multiplier=level_id,
                          max_second_multiplier=args.max_second_multiplier,
                          correct_answer_score=DEFAULT_CORRECT_ANSWER_SCORE,
                          incorrect_answer_score=DEFAULT_INCORRECT_ANSWER_SCORE)

            if args.verbose:
                level.Print()

            print(f"{DEFAULT_LEVEL_COLOR}")
            print(f"{DEFAULT_LEVEL_ICONS[level_id]}"*11)
            print(f"       Niveau {level_id}")
            print(f"{DEFAULT_LEVEL_ICONS[level_id]}"*11)
            print(f"{Fore.RESET}")

            # consecutive_good_answers = 0
            while not level.IsComplete():
                correct_answer, incremental_score = level.AskQuestion()
                player_score += incremental_score
                if correct_answer:
                    print(
                        f"Score : {Fore.LIGHTMAGENTA_EX}{player_score}{Fore.RESET} x {emoji.emojize(DEFAULT_POINT_ICON)}")

                print()

                # if correct_answer:
                #     consecutive_good_answers += 1
                # else:
                #     consecutive_good_answers = 0

            if level.IsValidated():
                print(
                    f"{Fore.LIGHTMAGENTA_EX}BRAVO ! Le niveau {Fore.YELLOW}{level_id}{Fore.LIGHTMAGENTA_EX} est validé ! Tu passes au prochain niveau !{Fore.RESET}")
                level_id += 1
            else:
                print(
                    f"{Fore.LIGHTMAGENTA_EX} Le niveau n'est pas validé, voici tes réponses:")
                # level.PrintLog()
                print(
                    f"{Fore.LIGHTMAGENTA_EX} Le niveau n'est pas validé, est-ce que tu veux essayer à nouveau ?")
            print()

            game_loader.Save(args.save,
                             player,
                             PlayerData({
                                 KEY_LEVEL: level_id,
                                 KEY_SCORE: player_score}),
                             args.verbose)

            print(
                f"{Fore.LIGHTMAGENTA_EX }Est-ce que tu veux continuer ? (O/N) {Fore.RESET}")
            should_continue_is_valid = False
            while not should_continue_is_valid:
                should_continue = input()
                if should_continue == "O":
                    should_continue_is_valid = True
                elif should_continue == "N":
                    should_continue_is_valid = True
                    level_id = args.max_second_multiplier+1
                else:
                    print("Je n'ai pas compris, réponds par O (OUI) ou N (NON) stp")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == '__main__':
    flags = get_args()
    main(flags)
