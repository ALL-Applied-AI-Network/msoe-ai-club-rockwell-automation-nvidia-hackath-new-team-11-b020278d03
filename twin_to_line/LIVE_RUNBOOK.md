# Live runbook: `live_inspect.py`
Draft for the Sunday dry run (plan §2.5 R9). The software is **not frozen yet**. The CSI camera resolution and how
image files reach the laptop are **not confirmed yet** (§6). All commands run on Noor's Mac in
`~/code/ignite/twin_to_line`.

**What it does:** it reads image files from a folder. Each time the fixture is still for 4 s with the arm away, it
gives all 30 holes (G01–G30) a state and logs every image it saw. It connects to no PLC, robot or plant network, and it
never writes into the image folder (R10).

| Colour on screen | State | Meaning |
|---|---|---|
| green | PASS | vial with a seated cap |
| red | DEFECT | cap problem seen |
| magenta | MISSED | empty hole before the last filled hole |
| grey | WAITING | empty hole after the last filled hole (not filled yet) |
| orange | UNSURE | can't tell (displaced or partial cap, or a hole read empty that was filled before); goes to a person |

**Inspector** (`--inspector`, chosen at the freeze, step 9):
- `rule` (default): the rule baseline. Its `rule_thresholds.json` was fitted on DEV draft labels (a placeholder).
- `resnet`: the synthetic-only ResNet-18 v1 at the D038 threshold (`--threshold preregistered` gives the
  pre-registered one). **G3 on DEV runs 1–3 was NO-GO** (87.7 % false alarms), so per the plan the rule baseline runs
  live and the ResNet is scored offline as arm A (§5). Needs `results/train/resnet18_v1/` (gitignored, never
  committed) and torch in `.venv`.

## 0. Before the session (Sunday dry run, then again Monday morning)
1. **Version.** `git -C ~/code/ignite log -1 --oneline` should show the frozen commit/tag. After the freeze:
   `shasum -a 256 -c FREEZE.sha256` → every line `OK` (R11; that file is written at the freeze).
2. **Tests.**
   `IGNITE_TWIN=~/Downloads/csi_digital_twin/csi_digital_twin_v1 ../.venv/bin/python -m pytest tests -q`
   → `125 passed` (or the count in the freeze record).
3. **Replay folder** (once; 569 MB, stays in `results/`, never committed):
   `../.venv/bin/python live_inspect.py --export-replay 1 --out results/live/replay_run1`
   → `run 1: 1123 frames (video) -> results/live/replay_run1`
4. **Dry run on DEV run 1:**
   ```bash
   ../.venv/bin/python live_inspect.py --source replay:results/live/replay_run1 \
       --labels labels/dev_labels.csv --out results/live/dryrun_$(date +%Y%m%d_%H%M) --note "dry run"
   ```
   Expect `inspector rule_yellow_seat  rule_thresholds.json 322c29ec2ea9`, then 18 lines from
   `event  1       cap_seal_video_1.mp4@t0000.0 K= 0 delay   4.0s  WAITING=30` to
   `event 18       cap_seal_video_1.mp4@t1050.0 K=17 delay   4.0s  MISSED=1 PASS=10 UNSURE=7 WAITING=12`, then
   `1123 frames, 18 events, {'settling': 75, 'scored': 18, 'unchanged': 964, 'arm': 66} -> results/live/dryrun_…`
5. **Outputs readable:** `../.venv/bin/python eval_metrics.py <dryrun dir>/predictions.csv --labels labels/dev_labels.csv`
   → first line `joined 523 labeled rows; 17 prediction rows have no label; 60 labels have no prediction`, no error.
   This is a plumbing check only (draft, in-sample labels), not a result.
6. **Folder rehearsal:**
   - Start step 1 below on an empty test folder, then copy a few `results/live/replay_run1` frames into it, one every
     second or two.
   - Each copied file should get a trial-log line within ~1 s. Ctrl-C should stop it as in step 3.
7. **Keep the laptop awake.** In a second terminal: `caffeinate -dims` (stop it with Ctrl-C after the session).

## 1. Start (live run)
1. **Set the folders.** `IN` = the folder where the camera images arrive (route to be approved by CSI). `OUT` = a
   **new** folder for every start; reusing one overwrites its CSV files.
   ```bash
   IN=/path/to/incoming_images
   OUT=results/live/csi_$(date +%Y%m%d_%H%M%S)
   ../.venv/bin/python live_inspect.py --source folder:"$IN" --out "$OUT" --note "CSI live run, Oct 26"
   ```
2. **Expected:**
   - One line names the inspector and its file hash, e.g. `inspector rule_yellow_seat  rule_thresholds.json
     322c29ec2ea9`; with `--inspector resnet`: `inspector resnet18_synth_v1[d038] t=0.50224 (pre-registered 0.99968)
     on mps  results/train/resnet18_v1/model.pt 8380851f8b4e`. Then nothing until the first event.
   - Within ~2 s, `$OUT` contains `overlays/`, `predictions.csv`, `session.json` and `trial_log.csv`.
   - In `session.json`, `"git"` is the frozen commit **without** `+modified`.
3. **Watch the log** in a second terminal: `tail -f "$OUT/trial_log.csv" | cut -d, -f6,8`. Each new image adds one
   `file,status` line within ~1 s.
4. **Check the first few images:**
   - No status `wrong_size`: they must be 640×480.
   - Column 7 (`frame_t`) increases by the camera's frame interval (`cut -d, -f6,7 "$OUT/trial_log.csv"`).
   - Images already in `IN` when you start are processed first, in name order.

## 2. While it runs
- **Normal statuses:**
  - `arm`: arm over the fixture, nothing is scored.
  - `settling`: waiting for 4 s of stillness.
  - `unchanged`: same fixture state as the last event.
  - `scored`: an event.
- **Event lines.** One per event: `event N <frame> K=<last filled hole> delay <s>  <state counts>`. The delay is
  normally 4.0 s (the stillness rule).
- **Operator view:**
  - `$OUT/overlay_latest.png` is rewritten after each event: the fixture with 30 coloured boxes and a legend.
  - Earlier events are kept in `$OUT/overlays/eNN_<frame>.png`.
  - Open it in Preview, and close and reopen it after an event line. There is no auto-refreshing window yet (§6).
- **Interventions.** Anything a person does goes on the paper log with the clock time: robot stopped, part moved,
  restart, cable, re-aim. After the session, copy those notes into the `intervention` column of the matching
  `trial_log.csv` rows. Never edit any other column.

## 3. Stop
1. Press **Ctrl-C once** in the terminal running `live_inspect.py`.
2. **Expected:** one line `N frames, M events, {...} -> <OUT>`. The prompt returns with no traceback.
   `session.json` shows `"stop_reason": "ctrl-c"`. Every row was already written as it happened, so nothing is lost.
3. **Copy all of `$OUT`** to the USB stick, and note the start and stop times on the paper log.

## 4. Errors: what you see and what to do
| What you see | What it means | What to do |
|---|---|---|
| `live_inspect.py: error: --source must be replay:DIR or folder:DIR with an existing DIR` | Typo, or the folder isn't there / not mounted | Fix the path; start again |
| `ProtectedDataError: N protected frame(s) in DIR` (replay only; nothing was processed) | The folder holds dataset frames from runs 4–5 or unassigned | Stop; don't open or move them; use the right folder; tell Noor |
| `can't open file ... live_inspect.py` | Not in the project folder | `cd ~/code/ignite/twin_to_line`; start again |
| A traceback at start naming `rule_thresholds.json` or `position_map_G.json` | A file is missing from this checkout | Check the version and hashes (§0.1); don't run until they match the freeze |
| `FileNotFoundError: ... results/train/resnet18_v1/run.json` (`--inspector resnet`; no `OUT` created) | The model folder isn't on this Mac (gitignored) | Copy it back from the backup and check its hashes against the freeze record; or run `--inspector rule` |
| `ValueError: ... model.pt does not match the sha256 recorded in run.json` | The model file was changed or damaged | Don't run the ResNet; restore the folder from the backup |
| `ModuleNotFoundError: No module named 'torch'` | `.venv` lacks torch | `../.venv/bin/pip install torch torchvision` before the session (not on the day); or run `--inspector rule` |
| Status `unreadable` | The image can't be decoded (corrupt, or still incomplete after 3 s) | One-off: note it, keep going. Every image: the copy route is broken → Ctrl-C, check with CSI |
| Status `wrong_size` (note says e.g. `1920x1080, expected 640x480`) | The camera isn't the 640×480 view the position map is built for | Ctrl-C. Do **not** resize by hand; the 1920×1080 map (plan step 5) is needed |
| Status `refused` | A dataset holdout frame (runs 4–5) arrived in the folder | Ctrl-C; take that folder out of use; tell Noor |
| Status `error` (the note has the message) | One frame failed; the program keeps going | One-off: note it. Repeated: Ctrl-C, start again with a new `OUT`, log it as an intervention |
| A new image is in `IN` but no trial-log line appears | It isn't `.png` / `.jpg` / `.jpeg`, or its name starts with `.` (ignored) | `ls -la "$IN"`; ask CSI for the file type |
| Trial-log lines keep coming but no event for minutes | The arm stays over the fixture, or the scene never holds still for 4 s; or `frame_t` doesn't increase (files without a timestamp in the name, all copied at once) | Check the statuses (`arm` / `settling`) and column 7; if `frame_t` is flat, stop and tell Noor (§6) |
| Boxes on the overlay don't sit on the holes; many holes UNSURE or WAITING that look filled | The camera view differs from the position map | Ctrl-C; take one photo of the screen; tell Noor. Never re-aim or move the camera (CSI rule) |
| The program crashed, or the terminal closed | — | Start again with a **new** `OUT` (§1). Images already in `IN` are processed again into the new session. Log the restart as an intervention |

## 5. Staged test images: don't run the software on them on the day
- The 22 staged images are the sealed test. Their labels are adjudicated first, before any model output is looked at.
  They are scored once, after the freeze (plan step 11).
- Keep them in their own folder that is **never** `IN`. While staging, `live_inspect.py` is stopped or watching a
  different folder.
- Scoring later (step 11), after the labels are locked, once per arm:
  `../.venv/bin/python live_inspect.py --source replay:<staged dir> --gate each --inspector <rule|resnet> --out results/live/sealed_<arm>`.
  `--gate each` scores every arm-clear image (one image per setup). For the ResNet, also run
  `--threshold preregistered` into its own `OUT` and report it next to the D038 result.

## 6. Open before the freeze
- CSI: camera resolution (640×480 assumed here) and how images reach the laptop (shared folder or CSI PC); both
  unconfirmed.
- CSI file names: whether they carry a timestamp (the event rule needs a real frame time; otherwise the file's
  modification time is used).
- An on-screen operator window that refreshes itself (today: the overlay file only).
- The frozen inspector and thresholds (R4); the full robustness tests (R8); the freeze record and hashes (R11).
- Measured on this Mac (DEV run 1 replay): rule median 27 ms per scored image, ResNet (MPS) 74 ms; 1.3 ms per other
  image (R7 target ≤ 1 s). ResNet start-up (torch, model load, warm-up) takes about 2.5 s before its first line.
