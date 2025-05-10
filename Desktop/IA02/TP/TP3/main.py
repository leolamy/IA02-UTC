import itertools
from typing import List, Tuple, Optional
import subprocess

"""Les variables propositionnelles seront représentées par des entiers strictement postifs. Un
littéral est un entier positif ou négatif. Une clause est une liste de littéraux. Une base de
clauses sera vue comme une liste de listes d’entier. Un modèle sera vu comme une liste de
clauses."""

# aliases de type
Grid = List[List[int]]
PropositionnalVariable = int
Literal = int
Clause = List[Literal]
ClauseBase = List[Clause]
Model = List[Literal]

"""
Attention, les copies en python ne sont que des référencements de pointeurs (sur les objets non mutables).
Il faut utiliser list(variables), copy(variables) ou variables [i] pour vraiment copier
"""


def cell_to_variable(i: int, j: int, val: int) -> PropositionnalVariable:
    return i * 81 + j * 9 + (val - 1) + 1


def variable_to_cell(var: PropositionnalVariable) -> Tuple[int, int, int]:
    i = (var - 1) // (9 * 9)
    j = ((var - 1) // 9) % 9
    val = (var - 1) % 9
    return i, j, val


def model_to_grid(model: Model, nb_vals: int = 9) -> Grid:
    grid = [[0 for _ in range(9)] for _ in range(9)]
    for var in model:
        if var > 0:
            i, j, val = variable_to_cell(var)
            grid[i][j] = val + 1
    return grid


def pprint_grid(grid: Grid):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)
        row = ""
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row += "|"
            row += f" {grid[i][j]}" if grid[i][j] != 0 and grid[i][j] > 0 else "."
        print(row.strip())
    print()


def at_least_one(variables: List[PropositionnalVariable]) -> Clause:
    return variables.copy()  # crée une copie de la liste pour éviter toute modification accidentelle de l'originale.
    # et évite les problèmes de mutation (copy)


def unique(variables: List[PropositionnalVariable]) -> ClauseBase:
    """
       Étant donné une liste de variables propositionnelles, renvoie la base de clauses
       'unique' associée, qui garantit qu'exactement une seule des variables est vraie.
       """
    clauses = [at_least_one(variables)]
    for var1, var2 in itertools.combinations(variables, 2):
        clauses.append([-var1, -var2])
    return clauses


def create_cell_constraints() -> ClauseBase:
    """
      Renvoie une base de clauses représentant la contrainte d'unicité de valeur
      pour toutes les cases du Sudoku.

      Pour chaque cellule (i, j) du Sudoku, exactement une des variables
      var(i,j,1), var(i,j,2), ..., var(i,j,9) doit être vraie.

      Returns:
          Une base de clauses garantissant que chaque cellule contient exactement un chiffre
      """
    contraintes = []
    for i in range(9):
        for j in range(9):
            cell_vars = [cell_to_variable(i, j, k) for k in range(1, 10)]
            contraintes.extend(unique(cell_vars))
    return contraintes


def create_line_constraints() -> ClauseBase:
    contraintes = []
    for i in range(9):
        for k in range(1, 10):
            ligne_var = [cell_to_variable(i, j, k) for j in range(9)]
            contraintes.extend(unique(ligne_var))
    return contraintes


def create_column_constraints() -> ClauseBase:
    contraintes = []
    for j in range(9):
        for k in range(1, 10):
            colonne_var = [cell_to_variable(i, j, k) for i in range(9)]
            contraintes.extend(unique(colonne_var))
    return contraintes


def create_box_constraints() -> ClauseBase:
    contraintes = []
    for box_row in range(3):
        for box_columns in range(3):
            for k in range(1, 10):
                box_vars = []
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_columns * 3 + j
                        box_vars.append(cell_to_variable(row, col, k))
                contraintes.extend(unique(box_vars))
    return contraintes


def create_value_constraints(grid: Grid) -> ClauseBase:
    """
        Étant donné une grille de Sudoku, retourne une base de clauses représentant
        les contraintes induites par les valeurs inscrites dans la grille.

        Pour chaque cellule (i,j) de la grille contenant une valeur k non nulle,
        ajoute une clause unitaire [var(i,j,k)] qui force cette cellule à contenir
        la valeur k.

        Args:
            grid: Une grille de Sudoku 9x9 où les cases vides sont représentées par 0
                  et les cases remplies par leur valeur (1-9)

        Returns:
            Une base de clauses fixant les valeurs connues de la grille
        """
    contraintes = []
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                k = grid[i][j]
                contraintes.append([cell_to_variable(i, j, k)])  # append une clause unitaire
    return contraintes


def generate_problem(grid: Grid) -> ClauseBase:
    """
        Étant donné une grille de Sudoku, renvoie la base de clause associée à
        l'ensemble des contraintes associées à cette grille.

        Cette fonction combine toutes les contraintes nécessaires pour résoudre le Sudoku:
        1. Contraintes de cellule (chaque cellule contient exactement un chiffre)
        2. Contraintes de ligne (chaque ligne contient chaque chiffre une fois)
        3. Contraintes de colonne (chaque colonne contient chaque chiffre une fois)
        4. Contraintes de bloc (chaque bloc 3x3 contient chaque chiffre une fois)
        5. Contraintes de valeur (les cellules déjà remplies ont des valeurs fixées)

        Args:
            grid: Une grille de Sudoku 9x9 où les cases vides sont représentées par 0
                  et les cases remplies par leur valeur (1-9)

        Returns:
            Une base de clauses représentant toutes les contraintes du problème
        """
    contraintes_globale = []
    contraintes_globale.extend(create_cell_constraints())
    contraintes_globale.extend(create_line_constraints())
    contraintes_globale.extend(create_column_constraints())
    contraintes_globale.extend(create_box_constraints())
    contraintes_globale.extend(create_value_constraints(grid))
    return contraintes_globale


def clause_to_dimacs(clauses: ClauseBase, nb_vars: int) -> str:
    nb_clauses = len(clauses)
    header = f"p cnf {nb_vars} {nb_clauses}\n"
    clauses_lines = []
    for clause in clauses:
        clauses_str = " ".join(str(literal) for literal in clause) + " 0"  # fin de la ligne
        clauses_lines.append(clauses_str)
    dimacs_str = header + "\n".join(clauses_lines) + "\n"
    return dimacs_str


def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)


def exec_gophersat(
        filename: str, cmd: str = "gophersat", encoding: str = "utf8"
) -> Tuple[bool, List[int]]:
    result = subprocess.run(
        [cmd, filename], capture_output=True, check=True, encoding=encoding
    )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:-2].split(" ")

    return True, [int(x) for x in model]


def solve_sudoku(grid: Grid, cmd: str = "gophersat", filename: str = "sudoku.cnf") -> Tuple[bool, Optional[Grid]]:
    clauses = generate_problem(grid)
    nb_vars = 729
    dimacs_str = clause_to_dimacs(clauses, nb_vars)
    write_dimacs_file(dimacs_str, filename)

    print(f"\nExécution de : {cmd} {filename}")

    try:
        satisfiable, model = exec_gophersat(filename, cmd)
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")
        return False, None

    if satisfiable:
        return True, model_to_grid(model)
    else:
        print("Ce Sudoku n'a pas de solution.")
        return False, None


example: Grid = [
    [5, 3, 5, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

example2: Grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1]
]

example3: Grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]


def main():
    grid = example
    print("Grille initiale \n")
    pprint_grid(grid)

    # Essayer plusieurs chemins possibles pour Gophersat
    gophersat_paths = [
        "/usr/local/bin/gophersat"
    ]

    solution_found = False
    for cmd_path in gophersat_paths:
        try:
            ok, solution = solve_sudoku(grid, cmd=cmd_path)
            if ok:
                solution_found = True
                print("Grille résolue \n")
                pprint_grid(solution)
                break
        except:
            continue

    if not solution_found:
        print("Erreur : Gophersat n'a pas été trouvé ou le Sudoku n'a pas de solution.")


if __name__ == "__main__":
    main()
