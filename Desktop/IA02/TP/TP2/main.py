import itertools as it
import networkx as N


def generate_dimacs_cnf(graph, num_colors=3) -> None:
    # clause : nombre d'arrêtes * nombre de couleurs variables = nb couleurs * nb sommets
    couleurs = ["R", "G", "B"]
    couleurs_to_int = {"R":1,"G":2,"B":3}
    couleurs_int = [couleurs_to_int[c] for c in couleurs]
    sommets = list(graph.nodes)
    edges = list(graph.edges)
    variables = len(sommets) * len(couleurs)
    c = len(sommets) * len(couleurs) + len(edges) * len(couleurs) + len(sommets)
    clauses = []

    for j in sommets:
        clause = [(j * len(couleurs) + i) for i in couleurs_int]
        clauses.append(' '.join(map(str, clause)) + ' 0\n')

    for j in sommets:
        for pair in it.combinations(couleurs_int, 2):
            clause = [-((j * len(couleurs)) + pair[0]), -((j * len(couleurs)) + pair[1])]
            clauses.append(' '.join(map(str, clause)) + ' 0\n')

    for u, v in edges:
        for i in couleurs_int:
            clause = [-((u * len(couleurs)) + i), -((v * len(couleurs)) + i)]
            clauses.append(' '.join(map(str, clause)) + ' 0\n')

    with open('graph.cnf', 'w') as f:
        f.write('p cnf {} {}\n'.format(variables, c))
        for clause in clauses:
            f.write(clause)

def main():
    graph = N.petersen_graph()
    generate_dimacs_cnf(graph, 3)


if __name__ == '__main__':
    main()
