import random
import itertools
import time
import tracemalloc
import csv, os

universe_size = int(input("Podaj rozmiar przestrzeni elementów - U: " ))
subset_num = int(input("Podaj liczbę podzbiorów: " ))

repeats = int(input("Podaj liczbę powtórzeń (np. 5): "))
base_seed = 42

#4a

# generator danych - przestrzeń elementów U i podzbiory

def universe_and_subsets(universe_size, subsets_num, set_size_min=None, set_size_max=None):
    universe = set(range(1, universe_size+1))

# zabezpieczenie dla małych wartości n, gdy min mogłoby wyjść wieksze niz max
    if set_size_max is None:
        set_size_max = max(2, universe_size // 2)
    if set_size_min is None:
        set_size_min = max(1, universe_size // 10)    

    subsets = []
    not_covered = set(universe)

# utworzenie zbiorów gwarantujących pokrycie pełni przestrzeni elementów U
    while not_covered:  
        size_ov_set = random.randint(set_size_min, set_size_max)
        created_subset = set(random.sample(list(not_covered), min(size_ov_set, len(not_covered))))
        subsets.append(created_subset)
        not_covered = not_covered - created_subset

    # losowe przykłady (sample) z przestrzeni elementów
    for i in range(subsets_num - len(subsets)):
        size_ov_set = random.randint(set_size_min, set_size_max)
        created_subset = set(random.sample(list(universe), size_ov_set))               
        subsets.append(created_subset)
        not_covered = not_covered - created_subset

# dodawanie podzbiorów losowych aż po osiąnięcie ich zadanej liczby
    for i in range(subsets_num - len(subsets)):
        size_ov_set = random.randint(set_size_min, set_size_max)
        created_subset = set(random.sample(list(universe), size_ov_set))
        subsets.append(created_subset)

    return universe, subsets

def set_cover_bruteforce(universe, sets):
    n = len(sets)

    for i in range(1, n + 1):
        if i % 5 == 0:
            print("Sprawdzam rozwiązania z", i, "podzbiorami...")

        for subset in itertools.combinations(sets, i):
            if set.union(*subset) == universe:
                return subset

    return None

# 4b

def set_cover_greedy(universe, sets):
    not_covered = set(universe)
    subsets = []
    remaining = list(sets)

    while not_covered:
        # wybierz podzbiór pokrywający jak najwięcej niepokrytych jeszcze elementów
        best_set = None
        best_size = -1

        for s in remaining:
            size = len(s & not_covered)

            if size > best_size:
                best_size = size
                best_set = s

        if len(best_set & not_covered) == 0:
            # żaden pozostały podzbiór nie pokrywa niczego nowego
            break

        subsets.append(best_set)
        not_covered = not_covered - best_set
        remaining.remove(best_set)

    return subsets, len(not_covered) == 0  # zwracamy też informację, czy udało się pokryć całość

for rep in range(repeats):
    random.seed(base_seed + rep)

    universe, subsets = universe_and_subsets(universe_size, subset_num)

    print(f"\n=== Powtórzenie {rep + 1}/{repeats}  (seed={base_seed + rep}) ===")
    print("\nPrzestrzeń elementów U: ")
    print(universe)
    print("\nPodzbiory:")
    for i in subsets:
        print(i)


# użycie z pomiarem czasu i pamięci

### Algorytm Dokładny ###
EXACT_THRESHOLD = 20 # przetestuj

if subset_num <= EXACT_THRESHOLD:
    tracemalloc.start()
    start = time.perf_counter()

    solution = set_cover_bruteforce(universe, subsets)

    exact_elapsed = time.perf_counter() - start
    exact_current, exact_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\nAlgorytm dokładny")
    for i in subsets:
        print(i)
    print(solution)
    print("Maksymalna ilość podzbiorów: ")
    print(len(solution))
    print("Czy suma wszystkich podzbiorów znajdujących się w rozwiązaniu jest dokładnie równa zbiorowi przestrzeni elementów?")
    print(set.union(*solution) == universe)
    print(f"Czas wykonania obliczeń: {exact_elapsed:.6f} s")
    print(f"Szczytowe zużycie pamięci: {exact_peak} B")
    print("\n")


### Algorytm Zachłanny ###

    tracemalloc.start()
    start = time.perf_counter()

    solution_greedy, is_full_cover = set_cover_greedy(universe, subsets)

    greedy_elapsed = time.perf_counter() - start
    greedy_current, greedy_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("Algorytm zachłanny:")
    for s in solution_greedy:
        print(s)

    print("Maksymalna ilość podzbiorów: ")
    print(len(solution_greedy))
    print("Czy pokrycie jest pełne?", is_full_cover)
    print(f"Czas wykonania: {greedy_elapsed:.6f} s")
    print(f"Szczytowe zużycie pamięci: {greedy_peak} B")
    print("\n")

   # ocena jakości: porównanie z rozwiązaniem dokładnym
    ratio = None
    if solution_greedy and solution:
        ratio = len(solution_greedy) / len(solution)
        print(f"Stosunek liczby podzbiorów (greedy/optymalne): {ratio:.2f}")

    
    row = {
        "n": universe_size,
        "m": len(subsets),
        "m_requested": subset_num,
        "seed": base_seed + rep,
        "exact_time": exact_elapsed if solution else "",
        "exact_peak": exact_peak if solution else "",
        "exact_size": len(solution) if solution else "",
        "greedy_time": greedy_elapsed,
        "greedy_peak": greedy_peak,
        "greedy_size": len(solution_greedy),
        "ratio": ratio if ratio is not None else "",
    }

    file_exists = os.path.isfile("wyniki.csv")
    with open("wyniki.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
