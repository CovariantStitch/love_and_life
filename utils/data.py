import numpy as np
import pandas as pd

VETEMENTS = [
    "T-shirt",
    "Pull / Sweat",
    "Chemise",
    "Pantalon / Jeans",
    "Short",
    "Robe",
    "Jupe",
    "Sous-vêtements",
    "Soutien-gorge",
    "Chaussettes",
    "Chaussures",
    "Ceinture",
    "Veste / Manteau",
    "Accessoire (cravate, écharpe…)",
]

PRATIQUES = [
    "Baiser sur la bouche",
    "French kiss",
    "Caresses seins",
    "Caresses fesses",
    "Fellation",
    "Cunnilingus",
    "Doigtage",
    "Handjob",
    "Sexe vaginal",
    "Sexe anal",
    "69",
    "Masturbation mutuelle",
    "Jeu de rôle léger",
    "Fessée",
    "Léger bondage",
    "Exhibitionnisme soft",
    "Jouets (vibro, plug…)",
]

OBJETS = [
    "Appareil photo",
    "Chantilly",
    "Gode",
    "Plug",
    "Gode ceinture",
    "Huile",
    "Masque",
    "Menottes",

]


class Player:
    def __init__(self, name, gender, id_):
        self.id_: int = id_
        self.name: str = name
        self.gender: str = gender
        self.has_secret: bool = True
        self.avatar_emoji: str = "🧑" if gender == 'Garçon' else "👧"
        self.gender_emoji = gender_emoji = "♂️" if "Garçon" in self.gender else "♀️" if "Fille" in self.gender else "⚧️"

        self.clothes = ["Sous-vêtements", "Chaussettes",]
        self.clothes += ["Soutien-gorge"] if self.gender == "Fille" else []
        self.practices = []

        self.clothes_nb: int = len(self.clothes)
        self.practices_nb: int = 0

        self.process()

    def process(self):
        self.clothes_nb = len(self.clothes)
        self.practices_nb = len(self.practices)

    def __str__(self):
        return f"Joueur {self.name}, sexe {self.gender}, id {self.id_}"


def parse_player(row: pd.Series):
    return Player(id_=row["ID"], name=row["Name"], gender=row["Gender"])


# define the number of questions per level depending on the total time of the game, also define question/action ratio
# we consider that a question is ~0.5 minute, an action is between 2 to 5 minutes (actions in level 4/5 are longer)
# level one is soft, mainly question, ~10% of the game
# level two players start touching, fewer questions, ~15% of the game
# level three focuses on oral, fewer questions, ~25% of the game
# level four means serious things, but no orgasm her ! ~25% of the game
# level five means orgasm, here it is more up to the players to end the game, one action each
levels_configs = {
    1: {"n": lambda t: max(2, int(0.1 * t / 0.8)), "question_action_ratio": 0.8},
    # mean duration = 0.8*0.5+0.2*2=0.8 minutes
    2: {"n": lambda t: max(2, int(0.15 * t / 1.8)), "question_action_ratio": 0.4},
    3: {"n": lambda t: max(2, int(0.25 * t / 3.)), "question_action_ratio": 0.1},
    4: {"n": lambda t: max(2, int(0.25 * t / 3.)), "question_action_ratio": 0.1},
    5: {"n": lambda t: 2, "question_action_ratio": 0},
}


class Game:
    def __init__(self):
        self.intensity: int = 3
        self.duration: int = 30
        self.objects: list = []

        self.objects_nb: int = 0

        self.current_level: int = 1
        self.current_level_idx: int = 1
        self.current_player: str = ""
        self.current_receiver: str = ""
        self.current_player_idx: int = 0

        self.question_action = None
        self.current_action_question: list = []

        self.levels_configs = {}

    def process(self):
        self.objects_nb = len(self.objects)

    def start(self):
        self.levels_configs = {i_:
            {
                "n": levels_configs[i_]["n"](self.duration),
                "question_action_ratio": levels_configs[i_]["question_action_ratio"]
            }
            for i_ in range(1, 6)}

    def finish_step(self):
        self.current_level_idx += 1
        self.current_player_idx += 1

        if self.current_level_idx > self.levels_configs[self.current_level]["n"]:
            self.current_level_idx = 1
            self.current_level += 1


class GameQuestion:
    def __init__(self, title: str, text: str, possibilities: list[str], level: int, gender: str, id_: int):
        self.title: str = title
        self.text: str = text
        self.possibilities: list[str] = possibilities
        self.level: int = level
        self.gender: str = gender
        self.id_: int = id_


class GameAction:
    def __init__(self, title: str, text: str, level: int, practices: list[str], objects: list[str], gender: str,
                 id_: int, timer: str | None, repetitions: str | None):
        self.title: str = title
        self.text: str = text
        self.level: int = level
        self.practices: list[str] = practices
        self.objects: list[str] = objects
        self.gender: str = gender
        self.id_: int = id_
        self.timer: list[int] = [int(t) for t in timer.split("/")] if timer else None
        self.repetitions: list[int] = [int(t) for t in repetitions.split("/")] if repetitions else None


class GameData:
    def __init__(self, df: pd.DataFrame):
        df = df.replace(np.nan, None)
        self.df: pd.DataFrame = df
        self.questions: list[GameQuestion] = []
        self.actions: list[GameAction] = []

        self.questions_per_level: dict = {i_: [] for i_ in range(1, 6)}
        self.questions_per_id: dict = {}
        self.actions_per_level: dict = {i_: [] for i_ in range(1, 6)}
        self.actions_per_id: dict = {}

        self.parse_dataframe()

    def parse_dataframe(self):
        for id_, row in self.df.iterrows():
            if row["Type"] == "Question":
                question = self.parse_question(id_, row)
                self.questions.append(question)
                self.questions_per_level[question.level].append(question)
                self.questions_per_id[question.id_] = question
            elif row["Type"] == "Action":
                action = self.parse_action(id_, row)
                self.actions.append(action)
                self.actions_per_level[action.level].append(action)
                self.actions_per_id[action.id_] = action
            else:
                raise ValueError(f"Unknown question type: {row['Type']}")

    @staticmethod
    def parse_question(id_: int, row: pd.Series) -> GameQuestion:
        question: GameQuestion = GameQuestion(
            title=row["Title"],
            text=row["Text"],
            possibilities=row["Possibilities"].split("/"),
            level=row["Level"],
            id_=id_,
            gender=row["Gender"]
        )
        return question

    @staticmethod
    def parse_action(id_: int, row: pd.Series) -> GameAction:
        action: GameAction = GameAction(
            title=row["Title"],
            text=row["Text"],
            level=row["Level"],
            practices=row["Practices"],
            objects=row["Objects"],
            gender=row["Gender"],
            id_=id_,
            timer=row["Timer"],
            repetitions=row["Repetitions"]
        )
        return action

    def __str__(self):
        text = "QUESTIONS:\n"
        text += "*" * 50
        for question in self.questions:
            text += f"{question.text}\n"
        text += "\nACTIONS:\n"
        text += "*" * 50
        for action in self.actions:
            text += f"{action.text}\n"
        return text
