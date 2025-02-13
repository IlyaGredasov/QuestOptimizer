from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy

INF = 10 ** 20


@dataclass
class QuestLine:
    quests: list[int]

    def append(self, node_index: int) -> None:
        self.quests.append(node_index)

    def pop(self, node_index: int) -> None:
        self.quests.pop(node_index)

    def __len__(self) -> int:
        return len(self.quests)

    def __getitem__(self, key) -> int:
        return self.quests[key]

    def __hash__(self) -> int:
        return hash(tuple(self.quests))

    def __repr__(self) -> str:
        return f"QuestLine({self.quests})"


@dataclass
class Path:
    path: list[int]
    length: float = 0.0

    def reverse(self) -> Path:
        new_path = deepcopy(self)
        new_path.path.reverse()
        return new_path

    def __repr__(self) -> str:
        return f"Path({self.path}, {self.length})"

    def __len__(self) -> int:
        return len(self.path)

    def __add__(self, other) -> Path:
        return Path(self.path + other.path, self.length + other.length)

    def __iadd__(self, other) -> Path:
        self.path += other.path
        self.length += other.length
        return self

    def __eq__(self, other) -> bool:
        return self.length == other.length

    def __lt__(self, other) -> bool:
        return self.length < other.length

    def __getitem__(self, key) -> int:
        return self.path[key]


@dataclass
class PathState:
    current_node_index: int
    path: Path
    quests: list[QuestLine]

    def count_of_quests(self) -> int:
        return sum(len(line) for line in self.quests)

    def __lt__(self, other) -> bool:
        return (self.count_of_quests() < other.count_of_quests() or
                (self.count_of_quests() == other.count_of_quests()) and (
                        self.path.length < other.path.length))

    def __eq__(self, other) -> bool:
        return (self.count_of_quests() == other.count_of_quests()) and (self.path.length == other.path.length)

    def __repr__(self) -> str:
        return f"GraphState(Current:({self.current_node_index}), {self.path}, {self.quests})"

    def __hash__(self):
        flattened_quests = []
        for line in self.quests:
            flattened_quests.extend(line.quests)
        return hash(tuple([self.current_node_index] + self.path.path + flattened_quests))


class Graph:
    def __init__(self, n: int = 0):
        self.adjacency_matrix = [[INF for _ in range(n)] for _ in range(n)]

    def __len__(self) -> int:
        return len(self.adjacency_matrix)

    def __getitem__(self, key) -> list[int]:
        return self.adjacency_matrix[key]
