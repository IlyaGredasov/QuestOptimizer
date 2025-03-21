from faker import Faker
from os import linesep
from random import randint
import argparse

parser = argparse.ArgumentParser(description="Test quest generator")

parser.add_argument('-q', '--q', type=int, help='Number of quests', required=False, default=50)
parser.add_argument('-v', '--v', type=int, help='Number of vertexes', required=False, default=50)
parser.add_argument('-e', '--e', type=int, help='Number of edges', required=False, default=-1)
parser.add_argument('-s', '--s', type=int, help='Start vertex', required=False)

args = parser.parse_args()

with open("example.txt", "w", newline='') as f:
    f.write(f"Vertex Count:{linesep}")
    f.write(f"\t{args.v}{linesep}")

    f.write(f"Vertexes:{linesep}")
    fake = Faker()
    for i in range(args.v):
        f.write(f"\t{i} {fake.city()}{linesep}")

    args.e = randint(1, int(args.v ** 1.5)) if args.e == -1 else args.e
    edges = set()
    while len(edges) < args.e:
        a, b = randint(0, args.v - 1), randint(0, args.v - 1)
        if a != b:
            edges.add((a, b))
    f.write(f"Edges:{linesep}")
    for edge in edges:
        f.write(f"\t{edge[0]} {edge[1]}{linesep}")

    if args.s:
        f.write(f"Start:{linesep}")
        f.write(f"\t{args.s}{linesep}")

    f.write(f"Quests:{linesep}")
    quests = [[randint(0, args.v - 1) for _ in range(randint(1, 5))] for _ in range(args.q)]
    for quest_line in quests:
        f.write("\t")
        f.write(" ".join(map(str, quest_line)))
        f.write(linesep)
    f.write(f"Quest Names:{linesep}")
    for i in range(args.q):
        f.write(f"\t{i} {fake.job()}{linesep}")
