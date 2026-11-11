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
### C1
### C2
### C3
### C4

## Part D
### D1
### D2
### D3

## Part E
### Integration diagram
### Reflection (half page)

## Bonus
