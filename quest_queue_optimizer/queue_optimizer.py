import logging
import threading
from collections import defaultdict
from copy import deepcopy
from random import randint

from graph import QuestLine, Path, PathState, Graph, INF
from parser import Parser
from sortedcontainers import SortedSet

logging.basicConfig(level=logging.INFO)


class QuestOptimizer:
    def floyd(self) -> list[list[Path]]:
        if self.fast_travel:
            return [[Path([i, j], 1) if i != j else Path([i], 0) for i in
                     range(len(self.graph))] for j in range(len(self.graph))]
        path_matrix = deepcopy(self.graph.adjacency_matrix)
        next_node = [[i for i in range(len(self.graph))] for _ in range(len(self.graph))]
        for i2 in range(len(path_matrix)):
            for i1 in range(len(path_matrix)):
                for i3 in range(len(path_matrix)):
                    if path_matrix[i1][i2] + path_matrix[i2][i3] < path_matrix[i1][i3]:
                        path_matrix[i1][i3] = path_matrix[i1][i2] + path_matrix[i2][i3]
                        next_node[i1][i3] = next_node[i1][i2]
        ways = [[Path(path=[], length=INF) for _ in range(len(self.graph))] for _ in range(len(self.graph))]
        for i1 in range(len(path_matrix)):
            for i2 in range(len(path_matrix)):
                way = Path(path=[], length=0)
                if path_matrix[i1][i2] != INF:
                    current = i1
                    while current != i2:
                        way += Path([current], path_matrix[current][i2])
                        current = next_node[current][i2]
                    way.path.append(current)
                    ways[i1][i2] = way
        return ways

    def __init__(self,
                 graph: Graph,
                 quests: list[QuestLine],
                 vertex_indexes_to_names: dict[int, str],
                 vertex_names_to_indexes: dict[str, int],
                 quest_indexes_to_names: dict[int, str],
                 quest_names_to_indexes: dict[str, int],
                 start: int = None,
                 fast_travel: bool = False,
                 bidirectional: bool = True,
                 depth_of_search: int = 1,
                 error_afford: float = INF,
                 num_threads: int = 1,
                 max_queue_size: int = 1000):
        self.graph = graph
        self.quests = deepcopy(quests)
        self.vertex_indexes_to_names = vertex_indexes_to_names
        self.vertex_names_to_indexes = vertex_names_to_indexes
        self.quest_indexes_to_names = quest_indexes_to_names
        self.quest_names_to_indexes = quest_names_to_indexes
        self.minimum_quest_count: int = sum(len(line) for line in quests)
        self.start = start
        self.fast_travel = fast_travel
        if bidirectional:
            self.make_bidirectional()
        self.depth_of_search = depth_of_search
        self.error_afford = min(error_afford, self.minimum_quest_count)
        self.num_threads = num_threads
        self.max_queue_size = max_queue_size

        self.queue: SortedSet[PathState] = SortedSet()
        self.best_path: Path = Path([], INF)
        self.best_path_for_start: defaultdict[int, Path] = defaultdict(Path)
        self.best_paths_count = 0
        self.stop_event: threading.Event = threading.Event()

    def make_bidirectional(self):
        for i in range(len(self.graph)):
            for j in range(len(self.graph)):
                self.graph[i][j] = min(self.graph[i][j], self.graph[j][i])

    def optimize_step(self) -> None:
        current_state: PathState = self.queue.pop(randint(0, len(self.queue) - 1))
        current_state.path += Path([current_state.current_node_index], 0)
        if current_state.count_of_quests() <= max(self.minimum_quest_count, 1) * self.error_afford:
            logging.info(f"{self.minimum_quest_count}, {len(self.queue)}")
            with threading.Lock():
                for quest_line in current_state.quests:
                    if quest_line[0] == current_state.current_node_index:
                        quest_line.pop(0)
                current_state.quests = [quest_line for quest_line in current_state.quests if len(quest_line) > 0]
                if len(current_state.quests) == 0:
                    if (current_state.path[0] not in self.best_path_for_start.keys()
                            or self.best_path_for_start[current_state.path[0]].length
                            > current_state.path.length):
                        self.best_path_for_start.update(
                            {current_state.path[0]: current_state.path}
                        )
                    self.best_paths_count += 1
                elif self.fast_travel:
                    for quest_line in current_state.quests:
                        new_state: PathState = deepcopy(current_state)
                        new_state.current_node_index = quest_line[0]
                        new_state.path.length += 1
                        self.queue.add(new_state)
                else:
                    for j in range(len(self.graph)):
                        if self.graph[current_state.current_node_index][j] != INF:
                            new_state: PathState = deepcopy(current_state)
                            new_state.current_node_index = j
                            new_state.path.length += self.graph[current_state.current_node_index][j]
                            if len(self.queue) == self.max_queue_size:
                                self.queue.pop(randint(0, self.max_queue_size - 1))
                            self.queue.add(new_state)
                self.minimum_quest_count = min(self.minimum_quest_count, current_state.count_of_quests())

    def optimize_cycle(self):
        while self.best_paths_count < self.depth_of_search and not self.stop_event.is_set():
            self.optimize_step()

    def floyd_optimize(self) -> None:
        floyd_path_matrix: list[list[Path]] = self.floyd()
        is_updated = True
        while is_updated:
            is_updated = False
            new_best_path_for_start = deepcopy(self.best_path_for_start)
            for floyd_start in range(len(self.graph)):
                for start, path in self.best_path_for_start.items():
                    if (floyd_start not in new_best_path_for_start.keys() or
                            floyd_path_matrix[floyd_start][start].length + path.length <
                            new_best_path_for_start[floyd_start].length):
                        is_updated = True
                        new_best_path_for_start.update(
                            {floyd_start: floyd_path_matrix[floyd_start][start].reverse() + Path(path.path[1:],
                                                                                                 path.length)}
                        )
            self.best_path_for_start = deepcopy(new_best_path_for_start)

    def optimize(self) -> None:
        if len(self.quests) <= self.max_queue_size:
            for quest_line in self.quests:
                if len(self.queue) == len(self.graph):
                    break
                with threading.Lock():
                    self.queue.add(PathState(quest_line[0], Path([]), deepcopy(self.quests)))
        else:
            self.queue.add(PathState(self.start, Path([]), deepcopy(self.quests)))
        threads = []
        logging.info("Queue has loaded")
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.optimize_cycle)
            thread.start()
            threads.append(thread)
            self.stop_event.set()
        for i in range(self.num_threads):
            threads[i].join()
        self.floyd_optimize()
        if self.start is None:
            self.best_path = min((path for path in self.best_path_for_start.values()),
                                 key=lambda path: path.length)
        else:
            self.best_path = deepcopy(self.best_path_for_start[self.start])

    # to-do
    def print_quests_on_path(self):
        quests_dict = {i: quest_line for i, quest_line in enumerate(self.quests)}
        for node_index in self.best_path:
            print(node_index, self.vertex_indexes_to_names[node_index], end=' ')
            for i, quest_line in quests_dict.items():
                while len(quest_line) > 0 and quest_line[0] == node_index:
                    print(i, end=' ')
                    quest_line.pop(0)
            quests_dict = {k: v for k, v in quests_dict.items() if len(v) > 0}
            print()


(graph, start_node_index, quests, vertex_indexes_to_names, vertex_names_to_indexes,
 quest_indexes_to_names, quest_names_to_indexes) = Parser.parse_file("test.qo")
optimizer = QuestOptimizer(
    graph=graph,
    quests=quests,
    vertex_indexes_to_names=vertex_indexes_to_names,
    vertex_names_to_indexes=vertex_names_to_indexes,
    quest_indexes_to_names=quest_indexes_to_names,
    quest_names_to_indexes=quest_names_to_indexes,
    start=start_node_index,
    error_afford=1.1,
    fast_travel=False,
    num_threads=128,
    max_queue_size=200000
)
optimizer.optimize()
print(optimizer.best_path)
#optimizer.print_quests_on_path()
