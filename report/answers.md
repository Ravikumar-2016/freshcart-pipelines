# Report answers (numbered as in the assignment)

Write answers in your own words. Predictions (B4, D1) must be written BEFORE running.

## Part A
### A1
Repository: https://github.com/Ravikumar-2016/freshcart-pipelines (currently private; share with instructor or make public before submission)

`git log --oneline` (update again before final submission):
```
0c83c3e fix: restore correct 80/20 train test split
b038cf1 test: demonstrate failing CI for incorrect split
6d86300 ci: add GitHub Actions workflow
4d1e80a feat: add Iris data transformer and tests
4ef2ad1 chore: initial repository structure and .gitignore
```

### A2
> DRAFT drafted by the assistant: rephrase the last column in your own words before submitting
> (the assignment requires your own wording).

| Command | Where the change happens | What exactly happens? |
|---|---|---|
| `git init` | Working folder / local repository | Creates a hidden `.git` folder, turning the current folder into an empty local repository. |
| `git add train.py` | Working folder → staging area | Marks the current contents of `train.py` to be included in the next commit. |
| `git commit -m "msg"` | Staging area → local repository | Saves the staged snapshot as a new commit with an id and the message "msg", on my laptop only. |
| `git remote add origin URL` | Local repository (config only) | Stores the short name `origin` for the GitHub URL; nothing is uploaded or downloaded. |
| `git push -u origin main` | Local repository → remote (GitHub) | Uploads my local `main` commits to GitHub and links local `main` to `origin/main` so later a plain `git push` works. |
| `git pull origin main` | Remote (GitHub) → local repository and working folder | Downloads new commits from `origin/main` and merges them into my local `main` and files. |

**After `git commit`, can a teammate see my code on GitHub?** No. A commit is saved only in my
local repository on my laptop. GitHub (the remote) only receives it after `git push`.
(Evidence from this project: the first commit existed locally, and `git ls-remote` showed
nothing on GitHub until I pushed.)

### A3
- Test: `tests/test_prepare_data.py` asserts 120 train and 30 test rows.
- Block: `iris_project/transformers/prepare_data.py` uses `train_test_split(test_size=0.2, random_state=42)`.
  Decorators are imported only if missing, with a no-op fallback when `mage_ai` is absent (CI).
- Workflow: `.github/workflows/ci.yml` runs on every push: checkout, Python 3.12, `pip install -r requirements.txt`, `python -m pytest`.

Evidence:
| Run | Commit | Result | Evidence |
|---|---|---|---|
| CI #1 | 6d86300 "ci: add GitHub Actions workflow" | green (29s) | `screenshots/A/A3_green.png` |
| CI #2 | b038cf1 "test: demonstrate failing CI for incorrect split" (`test_size=0.3`) | red (27s) | `screenshots/A/A3_red.png` |
| CI #3 | 0c83c3e "fix: restore correct 80/20 train test split" | green (23s) | `screenshots/A/A3_final_green.png` (shows #1 green, #2 red, #3 green) |

Local pytest with `test_size=0.3`: `assert np.int64(105) == 120` (105 train rows) -> FAILED.
Local pytest after the fix: `1 passed`.

## Part B
### B1
### B2
### B3
### B4
### B5

## Part C
> Reference-notebook note: the Mage Iris reference notebook was NOT available. Everything below
> follows only what the assignment text states. My own choices (not from the reference): the
> accuracy gate threshold `MIN_ACCURACY = 0.90` in `train_model`, the block output shapes, and
> `random_state=42`. If the reference uses another threshold, the pass/fail column of C2 may differ.

### C1
Project: `iris_project/` (Mage 0.9.80, Python 3.12.6, native Windows). Pipeline `iris_classifier`,
wired in `iris_project/pipelines/iris_classifier/metadata.yaml`.

Final graph (C1 base blocks + C3 branch + C4 block; see also the real UI capture in C3):
```
load_iris (data_loader, @test: 150 rows, target column)
   |
validate_data (transformer, C4, @test x2: no missing values, exactly 3 classes)
   |
prepare_data (transformer, @test: split column, train/test)      [pytest also tests the 120/30 split]
   |
train_model (transformer, @test test_accuracy >= 0.90, 30 test rows)
   |------------------------------\
save_results (data_exporter,       evaluate_model (transformer, C3,
 @test: CSV exists, 30 rows)        @test: 3 class rows, support sum 30)
```
(Redraw this by hand or in a tool if you want your own diagram.)

Run: `mage run iris_project iris_classifier --test` (default max_depth=3), evidence
`screenshots/C/C1_mage_run_test.txt`. That run used the original 4 blocks: every block printed
`1/1 tests passed.`, `max_depth=3 test_accuracy=1.0000`, `Saved 30 rows to ...iris_predictions.csv`,
`Pipeline run completed.` (exit 0). The 6-block final run is in `C4_full_pipeline_run.txt`.

### C2
Command per depth (CSV deleted before each run): `mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": N}'`
(run with the original 4-block pipeline). Evidence: `screenshots/C/C2_depth_N.txt`, `C2_summary.txt`.

| max_depth | Test accuracy | test_accuracy passed? | iris_predictions.csv created? |
|---|---|---|---|
| 1 | 0.6333 | NO (0.6333 < 0.90 gate, exit 1) | NO |
| 2 | 0.9667 | yes | yes |
| 3 | 1.0000 | yes | yes |
| 4 | 1.0000 | yes | yes |
| 5 | 1.0000 | yes | yes |

At depth 1 the log ends with `FAIL: test_accuracy (block: train_model)`, `AssertionError: test accuracy
0.6333 is below the 0.9 gate`, `0/1 tests passed.`, and contains no `Saved ...` line (verified by grep:
0 matches); with all 6 blocks (`C4_depth1_gate.txt`) `evaluate_model` also did not run (no confusion matrix).

> DRAFT explanation (assistant-written; rewrite in your own words): With `--test`, Mage runs each
> block's `@test` functions right after the block. If an assertion fails, the block is marked failed
> and the run stops with a non-zero exit code, so blocks that depend on `train_model` (here
> `save_results`, and `evaluate_model` in C3) are never started. That is better than saving first and
> checking afterwards because a bad model's file never exists to be picked up by anything else, and
> the failure is visible immediately in the run instead of being hidden in a file nobody re-checks.

### C3
`train_model` now has two downstream blocks: `save_results` and `evaluate_model`
(`downstream_blocks` of `train_model` in `iris_project/pipelines/iris_classifier/metadata.yaml`).
Run at max_depth=2 (the informative case, one error); evidence `screenshots/C/C3_eval_depth_2.txt`
(depth 3 in `C3_eval_depth_3.txt`).

Confusion matrix (rows = actual, columns = predicted), max_depth=2:
```
                   pred_setosa  pred_versicolor  pred_virginica
actual_setosa               10                0               0
actual_versicolor            0                8               1
actual_virginica             0                0              11
```
Metrics table:
```
       class  precision  recall  f1-score  support
      setosa     1.0000  1.0000    1.0000  10.0000
  versicolor     1.0000  0.8889    0.9412   9.0000
   virginica     0.9167  1.0000    0.9565  11.0000
    accuracy     0.9667  0.9667    0.9667   0.9667
   macro avg     0.9722  0.9630    0.9659  30.0000
weighted avg     0.9694  0.9667    0.9664  30.0000
```
UI screenshot: `screenshots/C/C3_mage_ui_pipeline_graph.png` (real capture of
`http://localhost:6789/pipelines/iris_classifier/edit`, Mage v0.9.80) showing the tree
load_iris -> validate_data -> prepare_data -> train_model -> {save_results, evaluate_model}.
It was captured with headless Edge against a local server started with `REQUIRE_USER_AUTHENTICATION=0`
(otherwise Mage shows a sign-in page).

Cloudflare tunnel: NOT used, and I do not claim it satisfies the requirement. Why the assignment
mentions it (my reading, unverified against the course material): in Colab the Mage server runs on
a remote VM, so a tunnel is needed to open the UI in your own browser. Here Mage runs on the same
Windows machine, so `http://localhost:6789` is directly reachable. `cloudflared` is not installed.
If your instructor requires an actual tunnel URL: install cloudflared and run
`cloudflared tunnel --url http://localhost:6789` while `mage start iris_project` is running, but note
this publishes your Mage server to the internet (keep authentication ON, close it afterwards).
Ask the instructor whether a localhost screenshot is acceptable.

### C4
New block: `validate_data` (transformer, `iris_project/transformers/validate_data.py`) between
`load_iris` and `prepare_data`, with two `@test` functions: `test_no_missing_values` and
`test_three_classes`. Full 6-block run: `screenshots/C/C4_full_pipeline_run.txt` (exit 0,
`validate_data: 150 rows, 0 missing values, 3 classes`, `2/2 tests passed.`).
Negative check (tests fail when data is bad; run directly in Python): with one NaN ->
`FAIL: Found 1 missing values`; with only 2 classes -> `FAIL: Expected exactly 3 classes, got [0, 1]`.
Mage dependencies are in `requirements-mage.txt` (not installed by CI). pytest (CI test) still passes locally.

## Part D
### D1
### D2
### D3

## Part E
### Integration diagram
### Reflection (half page)

## Bonus
