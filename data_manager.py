"""Read/write question bank JSON and persisted user records (binary)."""

import hashlib
import json
import os
import pickle
from typing import Any, Dict, List, Optional

USER_DATA_FILENAME = "user_data.data"
QUESTIONS_FILENAME = "questions.json"


def _script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def user_data_path() -> str:
    return os.path.join(_script_dir(), USER_DATA_FILENAME)


def questions_path() -> str:
    return os.path.join(_script_dir(), QUESTIONS_FILENAME)


def _question_id(question_text: str) -> str:
    return hashlib.sha256(question_text.strip().encode("utf-8")).hexdigest()[:16]


def load_question_bank() -> List[Dict[str, Any]]:
    """
    Load and validate questions.json. Exits the process on invalid/missing bank.
    """
    path = questions_path()
    if not os.path.isfile(path):
        print("missing question bank")
        raise SystemExit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        print("incorrect formatting")
        raise SystemExit(1)

    if not isinstance(raw, dict) or "questions" not in raw:
        print("incorrect formatting and/or missing question bank")
        raise SystemExit(1)

    bank = raw["questions"]
    if not isinstance(bank, list) or len(bank) == 0:
        print("incorrect formatting and/or missing question bank")
        raise SystemExit(1)

    normalized: List[Dict[str, Any]] = []
    for i, q in enumerate(bank):
        if not isinstance(q, dict):
            print("incorrect formatting")
            raise SystemExit(1)
        text = q.get("question")
        qtype = q.get("type")
        answer = q.get("answer")
        category = q.get("category")
        difficulty = q.get("difficulty")
        if not all(
            isinstance(x, str) and x.strip()
            for x in (text, qtype, answer, category, difficulty)
        ):
            print("incorrect formatting")
            raise SystemExit(1)

        qtype = qtype.strip()
        difficulty = difficulty.strip()
        if qtype not in ("multiple_choice", "true_false", "short_answer"):
            print("incorrect formatting")
            raise SystemExit(1)
        if difficulty not in ("Easy", "Medium", "Hard"):
            print("incorrect formatting")
            raise SystemExit(1)

        entry: Dict[str, Any] = {
            "_id": _question_id(text),
            "question": text.strip(),
            "type": qtype,
            "answer": answer.strip(),
            "category": category.strip(),
            "difficulty": difficulty,
        }

        if qtype == "multiple_choice":
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) < 2:
                print("incorrect formatting")
                raise SystemExit(1)
            if not all(isinstance(o, str) and o.strip() for o in opts):
                print("incorrect formatting")
                raise SystemExit(1)
            entry["options"] = [o.strip() for o in opts]
        elif qtype == "true_false":
            if q.get("options") is not None:
                print("incorrect formatting")
                raise SystemExit(1)
        else:
            if q.get("options") is not None:
                print("incorrect formatting")
                raise SystemExit(1)

        normalized.append(entry)

    return normalized


def load_users() -> Dict[str, Dict[str, Any]]:
    path = user_data_path()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
    except (pickle.UnpicklingError, EOFError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save_users(users: Dict[str, Dict[str, Any]]) -> None:
    path = user_data_path()
    with open(path, "wb") as f:
        pickle.dump(users, f)
