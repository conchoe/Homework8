Code Review Against SPEC.md
Here's my detailed analysis of the implementation against the acceptance criteria and specification:

Acceptance Criteria
[PASS] User can successfully create a username and password that persists after restarting the app

auth.py implements signup with proper hashing (PBKDF2-SHA256) and salt generation (line 63-71).
data_manager.py uses pickle for persistent binary storage in user_data.data (lines 113-118).
Credentials are validated and checked against existing users (auth.py line 59).
[PASS] ELO gains/losses based on quiz scores (100%, 90%, 70%, below 70%, 30%)

app.py lines 23-35: elo_delta_for_score() correctly implements:
100% = +50 ELO
≥90% (but not 100%) = +35 ELO
70-89% = +15 ELO
exactly 70% = 0 ELO
51-69% = -15 ELO
31-50% = -25 ELO
≤30% = -45 ELO
[PASS] User can view rank, quizzes taken, and overall correctness rate

view_stats() function (app.py lines 245-257) displays all three metrics correctly.
[PASS] Disliked questions should not appear again

collect_reaction() (app.py lines 269-290) adds disliked question IDs to disliked_ids set.
pick_quiz_questions() (app.py lines 111-144) filters out disliked questions (line 117).
[PASS] Bronze rank receives only Easy-Medium difficulty

allowed_difficulties_for_rank() (app.py lines 53-61): Bronze returns {"Easy", "Medium"}.
Questions are filtered by this function in pick_quiz_questions() line 117.
[PASS] Silver rank receives mostly Medium with some Easy and Hard

base_difficulty_weights() (app.py lines 38-48): Silver = 0.15 Easy, 0.55 Medium, 0.30 Hard.
allowed_difficulties_for_rank(): Silver allows all three difficulties.
[PASS] Gold rank receives mostly Medium and some Hard

base_difficulty_weights(): Gold = 0.0 Easy, 0.55 Medium, 0.45 Hard.
allowed_difficulties_for_rank(): Gold allows {"Medium", "Hard"}.
[PASS] Diamond rank receives mostly Hard questions

base_difficulty_weights(): Diamond = 0.0 Easy, 0.20 Medium, 0.80 Hard.
allowed_difficulties_for_rank(): Diamond allows {"Medium", "Hard"}.
Spec Requirements
[PASS] User greeting and login/signup on startup

main() (app.py line 391) prints welcome message and calls prompt_login_or_signup().
[PASS] Unique usernames and password complexity requirements

signup() (auth.py lines 54-60) checks for duplicates and enforces complexity.
password_meets_complexity() (auth.py lines 20-34) requires ≥8 chars, lowercase, uppercase, digit, special character.
[PASS] Simple hash function for passwords

Uses PBKDF2-SHA256 with 200,000 iterations and random salt (auth.py lines 12-18, 67-68).
Uses secrets.compare_digest() for timing-safe comparison (auth.py line 47).
[PASS] First-time proficiency assessment

prompt_first_proficiency() (app.py lines 227-244) asks user for proficiency level.
Sets baseline ELO via starting_elo_for_proficiency() (auth.py lines 36-42): Easy=250, Medium=750, Hard=1250.
[PASS] Main menu with Start Test, View Stats, Exit

main_menu() (app.py lines 377-388) implements all three options.
[PASS] Tests are 10 questions long

pick_quiz_questions() called with count=10 (app.py line 305).
[PASS] Mix of multiple choice, true/false, and short answer

questions.json contains all three types (verified in file).
No explicit weighting toward variety, but randomization handles it implicitly.
[PASS] Video-game ranking system (Bronze, Silver, Gold, Diamond)

rank_name() (app.py lines 11-16) and ELO ranges match spec:
Bronze: 0-500
Silver: 501-1000
Gold: 1001-1500
Diamond: 1501+
[PASS] ELO system with threshold at 70%

Implemented correctly in elo_delta_for_score() (app.py lines 23-35).
[PASS] Post-quiz difficulty feedback (Easy/Just Right/Too Hard)

Implemented (app.py lines 347-359).
apply_test_feedback() (app.py lines 63-77) adjusts weights correctly:
Too easy: reduces Easy, boosts Medium/Hard
Too hard: boosts Easy, reduces Hard
[PASS] Optional like/dislike reactions after each question

collect_reaction() (app.py lines 269-290) implements this.
Dislikes are persisted; likes provide session boost.
[PASS] Save data on exit

main_menu() (app.py line 388) calls save_users() on exit (choice 3).
run_quiz() calls save_users() multiple times (app.py lines 301, 322, 365).
Error Handling
[PASS] Duplicate username detection

signup() (auth.py line 59) checks and returns appropriate error message.
[PASS] Invalid input format for MC, T/F, short answer

parse_mc_answer() (app.py lines 190-198): validates number input.
parse_tf_answer() (app.py lines 201-206): validates true/false input.
Both return None if invalid, and main question handlers re-prompt (lines 217, 233).
[PASS] Invalid questions.json handling

load_question_bank() (data_manager.py lines 17-104) thoroughly validates:
File existence (line 21-23)
JSON format (line 25-30)
Required structure (line 32-36)
Field presence and types (lines 50-58)
Question type validation (line 64-67)
Difficulty validation (line 68-70)
Multiple choice options validation (lines 73-83)
True/false and short answer validation (lines 84-90)
All errors print descriptive messages and exit (per spec).
[PASS] Wrong password more than 3 times exits

prompt_login_or_signup() (auth.py lines 110-119) exits after 3 failed attempts with sys.exit(1).
Code Quality & Logic Issues
[WARN] Repeated ELO dictionary keys

{"Easy": 0, "Medium": 0, "Hard": 0} is defined multiple times:
auth.py line 45
app.py lines 263, 323
Should be a module-level constant to avoid repetition.
Files/Lines: auth.py:45, app.py:263, 323
[WARN] Possible silent failure in answer matching for MC questions

ask_multiple_choice() (app.py lines 208-224): If correct answer text doesn't match any option exactly (after strip), correct_idx remains None and defaults to 0 (line 221).
This could silently mark wrong answers as correct if options have formatting mismatches.
File/Lines: app.py:208-224
[WARN] Short answer matching may be too strict with special characters

normalize_short() (app.py lines 180-181) only normalizes whitespace and case.
If answer is "list.append" and user types "list append", they won't match.
File/Lines: app.py:180-181
[WARN] No validation of feedback choices in feedback loop

Feedback input validation (app.py lines 353-359) repeatedly prompts on invalid input.
However, the feedback values should be more robustly named ("too_easy" vs user typing "easy").
File/Lines: app.py:353-359
[WARN] Like boost for a single question is hardcoded to +0.08 max

apply_like_boost() (app.py line 88): w[d] += 0.08 * min(n, 5).
Capping at 5 likes is arbitrary and not explained. This limits the impact of user preferences.
File/Lines: app.py:88
[WARN] Potential division by zero in rate calculation

view_stats() (app.py line 251): rate = (100 * tot_c // tot_a) if tot_a else 0.
While guarded with if tot_a, the issue is handled. ✓ (Acceptable)
[WARN] Unclear variable names in pick_quiz_questions()

Variables like w0, w1, w2 (app.py lines 126-128) are not self-documenting.
Should be named base_weights, feedback_adjusted, like_boosted.
File/Lines: app.py:126-128
[WARN] Disliked IDs stored as list but treated as set inconsistently

disliked_ids is stored as a list in JSON (data_manager.py) but converted to a set for efficiency.
Line 300: dis = set(rec.get("disliked_ids", []))
Line 281: rec["disliked_ids"] = list(dis)
This works but is prone to bugs if the conversion is missed.
File/Lines: app.py:300, 281
[WARN] Loading users multiple times in main loop

main() (app.py lines 394, 397) reloads users before each menu action.
While safe for multi-process scenarios, this is inefficient and suggests potential race conditions were a concern but not fully addressed.
File/Lines: app.py:394, 397
Security Concerns
[PASS] Password hashing is secure

Uses PBKDF2-HMAC-SHA256 with 200,000 iterations (industry standard).
Random salt generated via os.urandom(16) for each user.
Timing-safe comparison with secrets.compare_digest().
[PASS] Pickle security is acceptable

While pickle can execute arbitrary code, it's only used for internal user data format.
File permissions are OS-dependent (not explicitly restricted in code).
Caveat: The spec calls for "non human readable" storage, which pickle provides. However, no explicit file permission setting (e.g., chmod 600) is implemented.
File/Lines: data_manager.py:114-118
[WARN] File path security: Using __file__ for script location

_script_dir() (data_manager.py lines 12-13) uses os.path.abspath(__file__) to locate data files.
This is safe but could be improved by using a dedicated config path or environment variable for file locations.
File/Lines: data_manager.py:12-13
Specification Compliance - Quiz Difficulty Distribution
[WARN] Bronze rank difficulty distribution unclear

Spec says: "a user who has easy difficulty should receive easy-medium difficulty questions"
Code implements: 40% Easy, 60% Medium (lines 39-40)
This matches the spec, but the term "baseline easy" suggests it should lean more toward easy.
Interpretation: Acceptable as specified, but could be 60% Easy / 40% Medium for better alignment with "baseline easy."
File/Lines: app.py:39-40
[WARN] Diamond rank hard question percentage

Spec says: "Diamond is also baseline hard, with more hard questions that gold"
Code implements: 80% Hard, 20% Medium (line 46)
Gold is: 45% Hard, 55% Medium (line 44)
This correctly gives Diamond more hard questions than Gold. ✓
Missing Features or Potential Issues
[WARN] Spec mentions "easy-medium" mix but code doesn't explicitly enforce variety

pick_quiz_questions() selects 10 questions weighted by difficulty.
There's no guarantee of variety (e.g., avoiding 9 Easy + 1 Medium for Bronze).
The spec doesn't explicitly require perfect distribution, so this is acceptable but worth noting.
File/Lines: app.py:111-144
[PASS] Total of 10 questions enforced

Spec compliant; if fewer questions available due to dislikes, user is notified (app.py lines 312-315).