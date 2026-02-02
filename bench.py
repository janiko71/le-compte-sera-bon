#!/usr/bin/env python3
#
#  Bench rapide entre compte.py et compte_dp.py
#
#  - 3 cas aleatoires (seed fixe pour reproductibilite)
#  - timeout de 5 secondes par execution
#

import random
import statistics
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
SCRIPTS = ["compte.py", "compte_dp.py"]
CASES = 3
TIMEOUT_S = 5.0

PLAQUES = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 25, 50, 75, 100]


def tirage_aleatoire(n: int = 6) -> list[int]:
    plaques = PLAQUES[:]
    tirage = []
    for _ in range(n):
        i = random.randrange(0, len(plaques))
        tirage.append(plaques.pop(i))
    return tirage


def run_case(script: str, tirage_vals: list[int], cible: int) -> tuple[float, bool]:
    inp = " ".join(map(str, tirage_vals)) + "\n" + str(cible) + "\n"
    t0 = time.perf_counter()
    try:
        subprocess.run(
            ["python3", str(REPO / script)],
            input=inp.encode(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=TIMEOUT_S,
        )
        return time.perf_counter() - t0, False
    except subprocess.TimeoutExpired:
        return TIMEOUT_S, True


def main() -> None:
    random.seed(42)
    cibles = [random.randrange(100, 999) for _ in range(CASES)]
    tirages = [tirage_aleatoire(6) for _ in range(CASES)]

    results = {name: [] for name in SCRIPTS}

    for t, c in zip(tirages, cibles):
        for script in SCRIPTS:
            results[script].append(run_case(script, t, c))

    for script in SCRIPTS:
        times = [x[0] for x in results[script]]
        timeouts = sum(1 for _, to in results[script] if to)
        print(script)
        print("  mean:", statistics.mean(times))
        print("  min :", min(times))
        print("  max :", max(times))
        print("  timeouts:", f"{timeouts} / {len(times)}")


if __name__ == "__main__":
    main()
