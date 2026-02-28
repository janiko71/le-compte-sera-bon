#!/usr/bin/env python3
#
#  ----------
#
#  Recherche de solution pour "le compte est bon" (version optimisee)
#
#  Idees principales :
#
#  - DP sur sous-ensembles (bitmask) : chaque etat = un sous-ensemble des plaques
#  - Memoisation des resultats par sous-ensemble pour ne pas recalculer les memes choses
#  - Reductions de symetrie (commutativite, partitions en double)
#  - Limite optionnelle sur les valeurs intermediaires (heuristique)
#
#  ----------
#

import random
import re
import signal
import sys
import time
from typing import Dict, Set, List, Tuple, Optional

# --------------------------------------------------------------
#  Liste officielle des 24 plaques (1..10 en double + 25/50/75/100 en simple)
# --------------------------------------------------------------
PLAQUES = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 25, 50, 75, 100]


# --------------------------------------------------------------
def tirage_aleatoire(n: int = 6) -> List[int]:
# --------------------------------------------------------------

    """
        Tirage aleatoire de n plaques sans remise.
    """

    plaques = PLAQUES[:]
    tirage = []
    for _ in range(n):
        rg = random.randrange(0, len(plaques))
        tirage.append(plaques[rg])
        plaques.remove(plaques[rg])
    return tirage


# --------------------------------------------------------------
def _ajoute_resultat(
    results: Dict[int, Set[str]],
    value: int,
    exprs: Set[str],
    cap: Optional[int],
) -> None:
# --------------------------------------------------------------

    """
        Ajoute un resultat possible a un etat de DP.

        - "results" est un dict: valeur -> set(expressions)
        - "cap" est une limite optionnelle (heuristique). Si None, pas de limite.
    """

    if cap is not None and value > cap:
        return
    if value not in results:
        results[value] = set()
    results[value].update(exprs)


# --------------------------------------------------------------
def _combine_expressions(a: int, b: int, ea: Set[str], eb: Set[str]) -> Dict[int, Set[str]]:
# --------------------------------------------------------------

    """
        Combine toutes les expressions de "a" avec celles de "b" via les 4 operations.

        Retourne un dict: valeur -> set(expressions).

        IMPORTANT: cette fonction suppose que les reductions de symetrie
        (a <= b pour les operations commutatives) ont deja ete gerees par l'appelant.
    """

    out: Dict[int, Set[str]] = {}

    # Addition (commutative)

    val = a + b
    if val != a and val != b:
        exprs = {f"({xa} + {xb})" for xa in ea for xb in eb}
        out[val] = exprs

    # Multiplication (commutative)

    if a != 1 and b != 1:
        val = a * b
        if val != a and val != b:
            exprs = {f"({xa} x {xb})" for xa in ea for xb in eb}
            out[val] = exprs

    # Soustraction (resultat positif)

    if a > b:
        val = a - b
        if val != a and val != b:
            exprs = {f"({xa} - {xb})" for xa in ea for xb in eb}
            out[val] = exprs

    # Division entiere (resultat entier positif)
    
    if b > 1 and a % b == 0:
        val = a // b
        if val != a and val != b:
            exprs = {f"({xa} : {xb})" for xa in ea for xb in eb}
            out[val] = exprs

    return out


# --------------------------------------------------------------
def solve_compte(
    tirage: List[int],
    cible: int,
    cap: Optional[int] = None,
) -> Tuple[Set[str], Optional[Tuple[int, str]], int, Optional[Tuple[str, float]]]:
# --------------------------------------------------------------

    """
        Fonction principale de resolution.

        - "tirage" est la liste des plaques
        - "cible" est le nombre a atteindre
        - "cap" limite (optionnellement) les valeurs intermediaires

        Retour:

        - toutes les solutions exactes (set d'expressions)
        - la meilleure solution approchee (valeur, expression) si pas d'exacte
        - le nombre de combinaisons testees
        - la premiere solution exacte trouvee (expression, duree) si elle existe
    """

    n = len(tirage)
    if n == 0:
        return set(), None, 0

    # dp[mask] -> dict: valeur -> set(expressions)
    #
    # "mask" est un bitmask representant un sous-ensemble de plaques:
    #
    # - bit i a 1 => la plaque i est incluse dans le sous-ensemble
    # - exemple pour n=4, mask=0b1011 => plaques 0,1,3
    dp: List[Dict[int, Set[str]]] = [dict() for _ in range(1 << n)]

    # Initialisation des singletons
    #
    # Un seul nombre = une seule expression possible

    for i, val in enumerate(tirage):
        dp[1 << i][val] = {str(val)}

    # Variables de suivi de la meilleure solution (approchee ou exacte)

    best_distance = None
    best_value = None
    best_expr = None
    solutions: Set[str] = set()
    first_solution = None
    combinaisons_testees = 0
    t0 = time.time()
    ts = None

# --------------------------------------------------------------
    def affiche_etat() -> None:
# --------------------------------------------------------------

        """
            Affichage en temps reel, sur la meme ligne.
        """

        str_nb = "{:,}".format(combinaisons_testees).replace(",", " ")
        if len(solutions) == 0:
            msg = "Meilleure solution trouvee : {}, nombre de combinaisons testees : {}".format(
                best_expr if best_expr is not None else "None",
                str_nb,
            )
        else:
            duree = (ts - t0) if ts is not None else 0.0
            msg = "Premiere solution trouvee : {} en {:.2f} sec, nombre de combinaisons testees : {}".format(
                best_expr,
                duree,
                str_nb,
            )
        # On ajoute des espaces pour effacer une eventuelle ligne plus longue precedente
        print(msg + (" " * 20), end="\r", flush=True)

# --------------------------------------------------------------
    def maj_best(value: int, expr: str) -> None:
# --------------------------------------------------------------

        """
            Met a jour la meilleure solution globale si on se rapproche de la cible.
        """

        nonlocal best_distance, best_value, best_expr
        dist = abs(value - cible)
        if best_distance is None or dist < best_distance:
            best_distance = dist
            best_value = value
            best_expr = expr
            affiche_etat()

    # Parcours de tous les masques (tous les sous-ensembles de plaques)

    for mask in range(1, 1 << n):

        # Cas des singletons
        #
        # Aucun calcul a faire, on a deja la valeur

        if mask & (mask - 1) == 0:
            val = next(iter(dp[mask].keys()))
            expr = next(iter(dp[mask][val]))
            maj_best(val, expr)
            if val == cible:
                solutions.add(expr)
                if ts is None:
                    ts = time.time()
                if first_solution is None:
                    first_solution = (expr, ts - t0)
                affiche_etat()
            continue

        # Cas general:
        #
        # On partitionne "mask" en deux sous-masques non vides,
        # puis on combine toutes les valeurs possibles de ces deux sous-ensembles.

        submask = (mask - 1) & mask
        while submask:
            other = mask ^ submask
            if submask < other:  # evite les doubles partitions (A|B et B|A)
                left = dp[submask]
                right = dp[other]
                for a, ea in left.items():
                    for b, eb in right.items():
                        a_cur = a
                        b_cur = b
                        ea_cur = ea
                        eb_cur = eb
                        # Pour operations commutatives, on force a <= b
                        #
                        # On elimine ainsi les symetries a+b et b+a, a*b et b*a.
                        if a_cur > b_cur:
                            a_cur, b_cur = b_cur, a_cur
                            ea_cur, eb_cur = eb_cur, ea_cur
                        combined = _combine_expressions(a_cur, b_cur, ea_cur, eb_cur)
                        for val, exprs in combined.items():
                            # On compte les combinaisons testees
                            #
                            # (approximation du travail fait, utile pour comparer)
                            combinaisons_testees += 1
                            _ajoute_resultat(dp[mask], val, exprs, cap)
                            for expr in exprs:
                                maj_best(val, expr)
                                if val == cible:
                                    solutions.add(expr)
                                    if ts is None:
                                        ts = time.time()
                                    if first_solution is None:
                                        first_solution = (expr, ts - t0)
                                    affiche_etat()
            submask = (submask - 1) & mask

    # Formate la meilleure solution (approchee si pas d'exacte)

    best = None

    if best_value is not None and best_expr is not None:
        best = (best_value, best_expr)

    return solutions, best, combinaisons_testees, first_solution


# --------------------------------------------------------------
def main() -> None:
# --------------------------------------------------------------

    """
        Entree utilisateur, lancement du calcul, puis affichage des resultats.
    """

    c = input("Entrez les 6 nombres du tirage (plaques) : ")
    if c.strip() == "":
        # Si vide, on genere un tirage aleatoire
        tirage = tirage_aleatoire(6)
    else:
        # Separation souple (espaces, virgules, points-virgules, etc.)
        tirage = [int(s) for s in re.split(r"[, :;/]", c.strip()) if s != ""]

    d = input("Entrez le nombre a trouver : ")
    if d.strip() == "":
        # Si vide, on genere une cible aleatoire entre 100 et 999
        cible = random.randrange(100, 999)
    else:
        cible = int(d)

    # Optionnel: limite des valeurs intermediaires
    #
    # - None => pas de limite (exact)
    # - un entier => coupe certains chemins pour accelerer (heuristique)

    cap = None

    print("\nNombre a trouver : {}".format(cible))
    print("Tirage : {}".format(" ".join(str(x) for x in tirage)))
    print()

    # Mesure du temps de calcul

    t0 = time.time()
    solutions, best, nbc, first_solution = solve_compte(tirage, cible, cap=cap)
    t1 = time.time()

    # Termine l'affichage en temps reel sur une ligne propre

    print()

    if solutions:
        # Cas solution exacte
        #
        # On affiche d'abord la premiere solution trouvee, puis toutes les solutions exactes
        if first_solution is not None:
            expr, duree = first_solution
            print("Premiere solution trouvee : {} = {} (en {:.2f} sec)".format(cible, expr, duree))
            print()
            print("Toutes les solutions exactes :")
        for expr in sorted(solutions):
            print(f"{cible} = {expr}")
    else:
        # Sinon on affiche la meilleure valeur approchee
        if best is None:
            print("Aucune solution.")
        else:
            print("Solution la plus proche trouvee : {} = {}".format(best[0], best[1]))

    # Affichage du nombre de combinaisons et du temps total
    str_nb = "{:,}".format(nbc).replace(",", " ")
    print("\nDuree de la recherche : {:.2f} sec, avec {} combinaisons testees.\n".format(t1 - t0, str_nb))


if __name__ == "__main__":

# --------------------------------------------------------------
    def signal_handler(sig, frame):
# --------------------------------------------------------------

        """
            Fonction a executer lorsque CTRL+C est presse.
        """

        print("\nSignal d'interruption capte, arret du programme.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        main()
    except KeyboardInterrupt:
        print("\nSignal d'interruption capte, arret du programme.")
        sys.exit(0)
