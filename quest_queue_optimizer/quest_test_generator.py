from faker import Faker
from os import linesep
from random import randint

with open("../example.txt", "w", newline='') as f:
    v = 100
    f.write(f"Vertex Count:{linesep}")
    f.write(f"\t{v}{linesep}")

    f.write(f"Vertexes:{linesep}")
    fake = Faker()
    for i in range(v):
        f.write(f"\t{i} {fake.city()}{linesep}")

    e = randint(1, int(v ** 1.5))
    edges = set()
    while len(edges) < e:
        a, b = randint(0, v - 1), randint(0, v - 1)
        if a != b:
            edges.add((a, b))
    f.write(f"Edges:{linesep}")
    for edge in edges:
        f.write(f"\t{edge[0]} {edge[1]}{linesep}")

    s = randint(0, v - 1)
    f.write(f"Start:{linesep}")
    f.write(f"\t{s}{linesep}")

    q = 100

    f.write(f"Quests:{linesep}")
    quests = [[randint(0, v - 1) for _ in range(randint(1, 5))] for _ in range(q)]
    for quest_line in quests:
        f.write("\t")
        f.write(" ".join(map(str, quest_line)))
        f.write(linesep)
    f.write(f"Quest Names:{linesep}")
    for i in range(q):
        f.write(f"\t{i} {fake.job()}{linesep}")
