"""Local signup/login with hashed passwords and complexity rules."""

import hashlib
import os
import secrets
from typing import Dict, Tuple

from data_manager import load_users, save_users

MIN_PASSWORD_LEN = 8


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    ).hex()


def password_meets_complexity(password: str) -> Tuple[bool, str]:
    if len(password) < MIN_PASSWORD_LEN:
        return False, f"Password must be at least {MIN_PASSWORD_LEN} characters."
    if not any(c.islower() for c in password):
        return False, "Password must include a lowercase letter."
    if not any(c.isupper() for c in password):
        return False, "Password must include an uppercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must include a digit."
    specials = set("!@#$%^&*()_+-=[]{}|;:,.<>?")
    if not any(c in specials for c in password):
        return False, "Password must include a special character (!@#$%^&* etc.)."
    return True, ""


def _new_user_record() -> Dict:
    return {
        "salt_hex": "",
        "password_hash": "",
        "proficiency": None,
        "elo": 0,
        "quizzes_taken": 0,
        "total_correct": 0,
        "total_answered": 0,
        "disliked_ids": [],
        "next_quiz_feedback": None,
        "like_boost": {"Easy": 0, "Medium": 0, "Hard": 0},
    }


def starting_elo_for_proficiency(proficiency: str) -> int:
    if proficiency == "easy":
        return 250
    if proficiency == "medium":
        return 750
    if proficiency == "hard":
        return 1250
    return 250


def signup(users: Dict, username: str, password: str) -> Tuple[bool, str]:
    key = username.strip()
    if not key:
        return False, "Username cannot be empty."
    if key in users:
        return False, "That username is already taken. Please choose another."
    ok, msg = password_meets_complexity(password)
    if not ok:
        return False, msg
    salt = os.urandom(16)
    rec = _new_user_record()
    rec["salt_hex"] = salt.hex()
    rec["password_hash"] = _hash_password(password, salt)
    rec["elo"] = 0
    users[key] = rec
    save_users(users)
    return True, ""


def verify_password(rec: Dict, password: str) -> bool:
    salt = bytes.fromhex(rec["salt_hex"])
    return secrets.compare_digest(
        rec["password_hash"],
        _hash_password(password, salt),
    )


def prompt_login_or_signup() -> str:
    """
    Returns authenticated username. Exits process after 3 wrong passwords.
    """
    users = load_users()

    while True:
        print("Log in (L) or sign up (S)? ", end="")
        choice = input().strip().lower()
        if choice == "s":
            while True:
                print("Choose a username: ", end="")
                uname = input().strip()
                print("Choose a password: ", end="")
                pw = input()
                ok, err = signup(users, uname, pw)
                if ok:
                    users = load_users()
                    print("Account created. You're signed in.")
                    return uname
                print(err)
                if "already taken" in err:
                    continue
        elif choice == "l":
            print("Username: ", end="")
            uname = input().strip()
            if uname not in users:
                print("Unknown username.")
                continue
            wrong_attempts = 0
            while wrong_attempts < 3:
                print("Password: ", end="")
                pw = input()
                if verify_password(users[uname], pw):
                    return uname
                wrong_attempts += 1
                remaining = 3 - wrong_attempts
                if wrong_attempts >= 3:
                    print("Too many incorrect passwords. Goodbye.")
                    raise SystemExit(1)
                print(
                    f"Invalid password. {remaining} attempt(s) remaining before exit."
                )
        else:
            print("Please enter L or S.")
