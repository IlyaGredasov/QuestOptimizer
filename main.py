from parser import Parser
from quest_optimizer import QuestOptimizer
import faulthandler

faulthandler.enable()

(graph, start_node_index, quests, vertex_indexes_to_names, vertex_names_to_indexes,
 quest_indexes_to_names, quest_names_to_indexes) = Parser.parse_file("example.txt")
optimizer = QuestOptimizer(
    graph=graph,
    quests=quests,
    vertex_indexes_to_names=vertex_indexes_to_names,
    vertex_names_to_indexes=vertex_names_to_indexes,
    quest_indexes_to_names=quest_indexes_to_names,
    quest_names_to_indexes=quest_names_to_indexes,
    start=start_node_index,
    error_afford=1,
    fast_travel=True,
    bidirectional=True,
    num_threads=4,
    max_queue_size=100000
)
optimizer.optimize()
print(optimizer.best_path)
optimizer.print_quests_on_path()
print(faulthandler.dump_traceback(all_threads=True))
