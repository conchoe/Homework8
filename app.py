"""Command-line Python quiz with local auth, ELO ranks, and adaptive difficulty."""

import random
import sys
from typing import Any, Dict, List, Optional, Tuple

from auth import prompt_login_or_signup, starting_elo_for_proficiency
from data_manager import load_question_bank, load_users, save_users


def rank_name(elo: int) -> str:
    if elo <= 500:
        return "Bronze"
    if elo <= 1000:
        return "Silver"
    if elo <= 1500:
        return "Gold"
    return "Diamond"


def elo_delta_for_score(correct: int, total: int) -> int:
    if total == 0:
        return 0
    pct = (correct * 100) // total
    if pct > 70:
        if correct == total:
            return 50
        if pct >= 90:
            return 35
        return 15
    if pct == 70:
        return 0
    if pct <= 30:
        return -45
    if pct <= 50:
        return -25
    return -15


def base_difficulty_weights(elo: int) -> Dict[str, float]:
    """Rank-driven pool (acceptance criteria)."""
    r = rank_name(elo)
    if r == "Bronze":
        return {"Easy": 0.7, "Medium": 0.3, "Hard": 0.0}
    if r == "Silver":
        return {"Easy": 0.15, "Medium": 0.55, "Hard": 0.30}
    if r == "Gold":
        return {"Easy": 0.0, "Medium": 0.55, "Hard": 0.45}
    return {"Easy": 0.0, "Medium": 0.20, "Hard": 0.80}


def allowed_difficulties_for_rank(elo: int) -> set:
    """Restrict which difficulties can appear (acceptance criteria)."""
    r = rank_name(elo)
    if r == "Bronze":
        return {"Easy", "Medium"}
    if r == "Silver":
        return {"Easy", "Medium", "Hard"}
    if r == "Gold":
        return {"Medium", "Hard"}
    return {"Medium", "Hard"}


def apply_test_feedback(
    weights: Dict[str, float], feedback: Optional[str]
) -> Dict[str, float]:
    w = dict(weights)
    if feedback == "too_easy":
        w["Easy"] = w.get("Easy", 0) * 0.65
        w["Medium"] = w.get("Medium", 0) * 1.05
        w["Hard"] = w.get("Hard", 0) * 1.35
    elif feedback == "too_hard":
        w["Easy"] = w.get("Easy", 0) * 1.35
        w["Medium"] = w.get("Medium", 0) * 1.1
        w["Hard"] = w.get("Hard", 0) * 0.55
    for k in list(w):
        if w[k] <= 0:
            del w[k]
    s = sum(w.values())
    if s <= 0:
        return dict(weights)
    return {k: v / s for k, v in w.items()}


def apply_like_boost(weights: Dict[str, float], boost: Dict[str, int]) -> Dict[str, float]:
    w = {k: max(0.0, v) for k, v in weights.items()}
    for d, n in boost.items():
        if n and d in w:
            w[d] += 0.08 * min(n, 5)
    s = sum(w.values())
    if s <= 0:
        return weights
    return {k: v / s for k, v in w.items()}


def pick_quiz_questions(
    bank: List[Dict[str, Any]],
    disliked: set,
    elo: int,
    feedback: Optional[str],
    like_boost: Dict[str, int],
    count: int = 10,
) -> List[Dict[str, Any]]:
    allowed = allowed_difficulties_for_rank(elo)
    pool = [
        q
        for q in bank
        if q["_id"] not in disliked and q["difficulty"] in allowed
    ]
    w0 = base_difficulty_weights(elo)
    w1 = apply_test_feedback(w0, feedback)
    w2 = apply_like_boost(w1, like_boost)

    def weight_for(q: Dict[str, Any]) -> float:
        return max(0.0, w2.get(q["difficulty"], 0.0))

    picked: List[Dict[str, Any]] = []
    candidates = list(pool)
    for _ in range(count):
        if not candidates:
            break
        ws = [weight_for(q) for q in candidates]
        total = sum(ws)
        if total <= 0:
            choice = random.choice(candidates)
        else:
            r = random.uniform(0, total)
            acc = 0.0
            choice = candidates[0]
            for q, wt in zip(candidates, ws):
                acc += wt
                if r <= acc:
                    choice = q
                    break
        picked.append(choice)
        candidates.remove(choice)
    return picked


def normalize_short(s: str) -> str:
    return " ".join(s.strip().lower().split())


def answers_match_short(expected: str, given: str) -> bool:
    return normalize_short(given) == normalize_short(expected)


def parse_mc_answer(raw: str, n_options: int) -> Optional[int]:
    t = raw.strip()
    if not t:
        return None
    if t.isdigit():
        idx = int(t) - 1
        if 0 <= idx < n_options:
            return idx
        return None
    return None


def parse_tf_answer(raw: str) -> Optional[str]:
    t = raw.strip().lower()
    if t in ("true", "t"):
        return "true"
    if t in ("false", "f"):
        return "false"
    return None


def ask_multiple_choice(q: Dict[str, Any]) -> bool:
    opts = q["options"]
    for i, o in enumerate(opts, start=1):
        print(f"  {i}. {o}")
    correct_text = q["answer"]
    correct_idx = None
    for i, o in enumerate(opts):
        if o.strip() == correct_text.strip():
            correct_idx = i
            break
    if correct_idx is None:
        correct_idx = 0

    while True:
        print("Enter the number of your answer: ", end="")
        line = input()
        idx = parse_mc_answer(line, len(opts))
        if idx is None:
            print(
                "Your answer format was invalid. Please enter a number matching one of the choices."
            )
            continue
        return idx == correct_idx


def ask_true_false(q: Dict[str, Any]) -> bool:
    while True:
        print("Answer True or False: ", end="")
        line = input()
        parsed = parse_tf_answer(line)
        if parsed is None:
            print(
                "Your answer format was invalid. Please answer with the words True or False (or T or F), not a number."
            )
            continue
        expected = q["answer"].strip().lower()
        return parsed == expected


def ask_short_answer(q: Dict[str, Any]) -> bool:
    print("Your answer (one or two words): ", end="")
    line = input()
    return answers_match_short(q["answer"], line)


def run_question(q: Dict[str, Any]) -> bool:
    print()
    print(q["question"])
    t = q["type"]
    if t == "multiple_choice":
        return ask_multiple_choice(q)
    if t == "true_false":
        return ask_true_false(q)
    return ask_short_answer(q)


def prompt_first_proficiency(users: Dict, username: str) -> None:
    rec = users[username]
    if rec.get("proficiency"):
        return
    print()
    print("First time here — what is your Python proficiency?")
    print("  (1) Easy   (2) Medium   (3) Hard")
    while True:
        print("Choose 1, 2, or 3: ", end="")
        c = input().strip()
        if c == "1":
            rec["proficiency"] = "easy"
            break
        if c == "2":
            rec["proficiency"] = "medium"
            break
        if c == "3":
            rec["proficiency"] = "hard"
            break
        print("Please enter 1, 2, or 3.")
    rec["elo"] = starting_elo_for_proficiency(rec["proficiency"])
    save_users(users)


def view_stats(users: Dict, username: str) -> None:
    rec = users[username]
    elo = rec.get("elo", 0)
    taken = rec.get("quizzes_taken", 0)
    tot_c = rec.get("total_correct", 0)
    tot_a = rec.get("total_answered", 0)
    rate = (100 * tot_c // tot_a) if tot_a else 0
    prof = rec.get("proficiency") or "—"
    print()
    print("— Stats —")
    print(f"  Rank: {rank_name(elo)} (ELO {elo})")
    print(f"  Baseline proficiency: {prof}")
    print(f"  Quizzes taken: {taken}")
    print(f"  Overall correct rate: {rate}% ({tot_c}/{tot_a})")
    print()


def collect_reaction(users: Dict, username: str, q: Dict[str, Any]) -> Dict[str, int]:
    """Returns session like deltas for this question."""
    print("Optional: (L)ike this question, (D)islike, or press Enter to skip: ", end="")
    c = input().strip().lower()
    rec = users[username]
    dis = set(rec.get("disliked_ids", []))
    likes = {"Easy": 0, "Medium": 0, "Hard": 0}
    if c == "d":
        qid = q["_id"]
        if qid not in dis:
            dis.add(qid)
            rec["disliked_ids"] = list(dis)
            save_users(users)
            print("We will not show that question again.")
    elif c == "l":
        d = q["difficulty"]
        if d in likes:
            likes[d] = 1
        print("Noted — more like this next quiz.")
    return likes


def merge_like_boost(rec: Dict, delta: Dict[str, int]) -> None:
    lb = rec.setdefault("like_boost", {"Easy": 0, "Medium": 0, "Hard": 0})
    for k in ("Easy", "Medium", "Hard"):
        lb[k] = lb.get(k, 0) + delta.get(k, 0)


def run_quiz(users: Dict, username: str, bank: List[Dict[str, Any]]) -> None:
    rec = users[username]
    dis = set(rec.get("disliked_ids", []))
    feedback = rec.get("next_quiz_feedback")
    boost = dict(rec.get("like_boost") or {"Easy": 0, "Medium": 0, "Hard": 0})
    rec["like_boost"] = {"Easy": 0, "Medium": 0, "Hard": 0}
    save_users(users)

    questions = pick_quiz_questions(
        bank, dis, rec.get("elo", 0), feedback, boost, count=10
    )
    if len(questions) < 10:
        print(
            f"Note: only {len(questions)} question(s) available after excluding disliked items."
        )
    if not questions:
        print("No questions available.")
        return

    correct = 0
    session_likes = {"Easy": 0, "Medium": 0, "Hard": 0}
    for q in questions:
        ok = run_question(q)
        if ok:
            correct += 1
            print("Correct.")
        else:
            print(f"Incorrect. Expected: {q['answer']}")
        ld = collect_reaction(users, username, q)
        for k in session_likes:
            session_likes[k] += ld.get(k, 0)

    total = len(questions)
    pct = (correct * 100) // total if total else 0
    print()
    print(f"Score: {correct}/{total} ({pct}%)")

    delta = elo_delta_for_score(correct, total)
    rec["elo"] = max(0, rec.get("elo", 0) + delta)
    rec["quizzes_taken"] = rec.get("quizzes_taken", 0) + 1
    rec["total_correct"] = rec.get("total_correct", 0) + correct
    rec["total_answered"] = rec.get("total_answered", 0) + total
    if delta > 0:
        print(f"ELO +{delta} (now {rec['elo']}).")
    elif delta < 0:
        print(f"ELO {delta} (now {rec['elo']}).")
    else:
        print(f"ELO unchanged ({rec['elo']}).")

    merge_like_boost(rec, session_likes)

    print()
    print("Was this test (E)asy, (J)ust right, or (T)oo hard? ", end="")
    while True:
        c = input().strip().lower()
        if c in ("e", "easy"):
            rec["next_quiz_feedback"] = "too_easy"
            break
        if c in ("j", "just", "just right", "r", "right"):
            rec["next_quiz_feedback"] = "just_right"
            break
        if c in ("t", "hard", "too hard"):
            rec["next_quiz_feedback"] = "too_hard"
            break
        print("Please answer E (too easy), J (just right), or T (too hard).")
    save_users(users)


def main_menu(users: Dict, username: str, bank: List[Dict[str, Any]]) -> bool:
    print()
    print("Main menu:")
    print("  1) Start Test")
    print("  2) View Stats")
    print("  3) Exit")
    print("Choice: ", end="")
    c = input().strip()
    if c == "1":
        run_quiz(users, username, bank)
        return True
    if c == "2":
        view_stats(users, username)
        return True
    if c == "3":
        save_users(users)
        print("Goodbye.")
        return False
    print("Please choose 1, 2, or 3.")
    return True


def main() -> None:
    print("Welcome to the Python Quiz.")
    bank = load_question_bank()
    username = prompt_login_or_signup()
    users = load_users()
    if username not in users:
        print("Session error.")
        sys.exit(1)
    prompt_first_proficiency(users, username)
    users = load_users()

    while True:
        users = load_users()
        if username not in users:
            print("Session error.")
            sys.exit(1)
        if not main_menu(users, username, bank):
            break


if __name__ == "__main__":
    main()
