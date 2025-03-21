import logging
import re

from graph import Graph, QuestLine
from enum import Enum


class Parser:

    @staticmethod
    def parse_file(file_path: str) -> (Graph, int, list[QuestLine]):
        graph = Graph()
        start_node_index = None
        quests: list[QuestLine] = []
        vertex_names_to_indexes: dict[str, int] = dict()
        vertex_indexes_to_names: dict[int, str] = dict()
        quest_names_to_indexes: dict[str, int] = dict()
        quest_indexes_to_names: dict[int, str] = dict()

        class State(Enum):
            VERTEX_COUNT = 0
            VERTEXES = 1
            EDGES = 2
            START = 3
            QUESTS = 4
            QUEST_NAMES = 5

        with open(file_path, 'r') as f:
            lines = f.readlines()
            state = None
            for line in lines:
                match line.strip():
                    case "Vertex Count:":
                        state = State.VERTEX_COUNT
                        logging.info("Vertex Count handling")
                    case "Vertexes:":
                        state = State.VERTEXES
                        logging.info("Names handling")
                    case "Edges:":
                        state = State.EDGES
                        logging.info("Edges handling")
                    case "Start:":
                        state = State.START
                        logging.info("Start handling")
                    case "Quests:":
                        state = State.QUESTS
                        logging.info("Quests handling")
                    case "Quest Names:":
                        state = State.QUEST_NAMES
                        logging.info("Quest Names handling")
                    case _:
                        match state:
                            case State.VERTEX_COUNT:
                                graph = Graph(int(line.strip()))
                            case State.VERTEXES:
                                match = re.match(r"^(\d+)\s+(.+)$", line.strip('\n\t'))
                                name_index, name = int(match.group(1)), match.group(2)
                                vertex_names_to_indexes[name] = name_index
                                vertex_indexes_to_names[name_index] = name
                            case State.EDGES:
                                args = list(line.strip().split())
                                from_node_index = int(args[0])
                                to_node_index = int(args[1])
                                weight = 1 if len(args) == 2 else float(args[2])
                                graph.adjacency_matrix[from_node_index][to_node_index] = weight
                            case State.START:
                                start_node_index = int(line.strip())
                            case State.QUESTS:
                                quests.append(QuestLine(list(map(int, line.strip().split()))))
                            case State.QUEST_NAMES:
                                match = re.match(r"^(\d+)\s+(.+)$", line.strip('\n\t'))
                                quest_index, quest_name = int(match.group(1)), match.group(2)
                                quest_names_to_indexes[quest_name] = quest_index
                                quest_indexes_to_names[quest_index] = quest_name
        logging.info(f"File {file_path} has parsed")
        return (graph, start_node_index, quests, vertex_indexes_to_names, vertex_names_to_indexes,
                quest_indexes_to_names, quest_names_to_indexes)
