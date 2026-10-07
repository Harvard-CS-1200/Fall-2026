from typing import OrderedDict, Callable, Any
import random

# import the student code
from ps4 import HashTable, DeterministicHash, RandomHash

# -------------------------
# Pretty printing colors
# -------------------------
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# -------------------------
# Helpers
# -------------------------
def make_table(m=101, family="deterministic", lazing=False, U=10_000_000, seed=42):
    """Create a HashTable with the chosen hash family and optimize flag."""
    if family == "deterministic":
        hf = DeterministicHash(U, m)
    elif family == "random":
        hf = RandomHash(U, m, seed=seed)
    else:
        raise ValueError("family must be 'deterministic' or 'random'")
    return HashTable(U, m, hf, lazing)

def assert_true(label: str, predicate: Callable[[], bool], show_expectation: bool = True):
    ok = False
    try:
        ok = bool(predicate())
    except Exception as e:
        print(color.RED + color.BOLD + f"✗ {label}: Exception raised: {e}" + color.END)
        return False
    if ok:
        print(color.GREEN + color.BOLD + f"✓ {label}: Passed" + color.END)
    else:
        print(color.RED + color.BOLD + f"✗ {label}: Failed" + color.END)
    return ok

# -------------------------
# Tests
# -------------------------
def test_search_delete_opt_false():
    tests = OrderedDict()

    # Group 1: basic lookups (unique keys)
    def group_basic_unique(family):
        T = make_table(m=101, family=family, lazing=False)
        pairs = [(10, 100), (20, 200), (30, 300), (40, 400)]
        for k, v in pairs:
            T.insert(k, v)

        return [
            {
                "label": f"[{family}] Search miss returns None",
                "pred": lambda: (T.search(999) is None)
            },
            *[
                {
                    "label": f"[{family}] Search hit {k} returns inserted value",
                    "pred": (lambda k=k, v=v: T.search(k) == v)
                }
                for (k, v) in pairs
            ],
            {
                "label": f"[{family}] Delete miss returns False (nonexistent key)",
                "pred": lambda: (T.delete(999) is False)
            },
        ]

    # Group 2: duplicate-key semantics (must accept either LIFO nodes or update-in-place)
    def group_duplicate_key(family):
        T = make_table(m=103, family=family, lazing=False)
        k = 12345
        vals = ["A", "B", "C"]  # inserted in order
        for v in vals:
            T.insert(k, v)

        def after_one_delete_ok():
            """After one delete(k), either:
            - update-in-place: search(k) is None, OR
            - multi-node LIFO: search(k) is "B" and delete returned True.
            """
            res = T.delete(k)
            if not res:
                return False
            s = T.search(k)
            return (s is None) or (s == "B")

        def delete_all_then_none():
            """Repeated deletes eventually remove key k completely."""
            # We already deleted once in previous test. Do up to 3 more deletes.
            c = 0
            while T.delete(k):
                c += 1
                if c > 3:
                    break
            return T.search(k) is None

        return [
            {
                "label": f"[{family}] Search(k) after inserts returns one of inserted values",
                "pred": lambda: T.search(k) in set(vals)
            },
            {
                "label": f"[{family}] Delete(k) removes one matching pair (any semantics acceptable)",
                "pred": after_one_delete_ok
            },
            {
                "label": f"[{family}] After deleting remaining copies, search(k) is None",
                "pred": delete_all_then_none
            },
        ]

    # Group 3: interactions with other keys
    def group_isolation(family):
        T = make_table(m=100, family=family, lazing=False)
        # two different keys that *may* collide depending on family/m, but correctness should hold
        T.insert(150, "X1")
        T.insert(250, "Y1")
        T.insert(150, "X2")  # second insert for 150

        return [
            {
                "label": f"[{family}] Search other key unaffected",
                "pred": lambda: T.search(250) == "Y1"
            },
            {
                "label": f"[{family}] Delete(150) returns True",
                "pred": lambda: T.delete(150) is True
            },
            {
                "label": f"[{family}] After deleting 150 once, 250 still present",
                "pred": lambda: T.search(250) == "Y1"
            },
        ]

    # Build test list
    tests["opt=False with DeterministicHash"] = (
        group_basic_unique("deterministic")
        + group_duplicate_key("deterministic")
        + group_isolation("deterministic")
    )
    tests["opt=False with RandomHash"] = (
        group_basic_unique("random")
        + group_duplicate_key("random")
        + group_isolation("random")
    )

    # Run
    total = 0
    passed = 0
    for section, items in tests.items():
        print("\n" + color.BOLD + section + color.END)
        for t in items:
            total += 1
            if assert_true(t["label"], t["pred"]):
                passed += 1

    col = color.GREEN if passed == total else color.RED
    print(color.BOLD + f"\nTests Passed {col}{passed}/{total}" + color.END)

def test_opt_flag_is_respected():
    """
    Sanity check that lazing=True behaves differently from lazing=False for a colliding key.
    We don't require a *specific* wrong value here—just that opt=True can return a value when
    the key is absent, which would never happen with opt=False.
    """
    print("\n" + color.BOLD + "opt flag sanity check" + color.END)

    # Build two tables with the same contents
    m = 10
    U = 10_000_000
    hf_d = DeterministicHash(U, m)
    T_false = HashTable(U, m, hf_d, lazing=False)
    T_true  = HashTable(U, m, hf_d, lazing=True)

    # Insert a key that hashes to the same bucket as 999 (very likely with small m)
    # But don't insert key 999 itself.
    for k in [9, 19, 29, 39]:
        T_false.insert(k, f"v{k}")
        T_true.insert(k, f"v{k}")

    absent_key = 999  # unlikely to be present
    def opt_false_never_returns_value_for_absent_key():
        return T_false.search(absent_key) is None

    def opt_true_may_return_head_value_even_when_absent():
        # Depending on collisions, this is often non-None for lazing=True
        return T_true.search(absent_key) is not None

    p1 = assert_true("[deterministic] opt=False returns None for absent key", opt_false_never_returns_value_for_absent_key)
    p2 = assert_true("[deterministic] opt=True can return a (wrong) value for absent key", opt_true_may_return_head_value_even_when_absent)

    col = color.GREEN if (p1 and p2) else color.RED
    print(color.BOLD + f"opt flag check {col}{'passed' if (p1 and p2) else 'failed'}" + color.END)

def test():
    # Core tests for students' opt=False implementations
    test_search_delete_opt_false()
    # Optional: quick sanity that lazing flag changes behavior
    test_opt_flag_is_respected()

if __name__ == "__main__":
    test()
