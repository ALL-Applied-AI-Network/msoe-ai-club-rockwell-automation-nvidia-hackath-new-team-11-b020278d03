# Live runbook: `live_inspect.py`
Draft for the Sunday dry run (plan §2.5 R9). The software is **not frozen yet**. §0–§5 run on Noor's Mac in
`~/code/ignite/twin_to_line`; **Monday runs on CSI's GB10 from the package: §7.** The camera streams 1920×1080 (and
320×240); 1920×1080 frames are warped into the DEV 640×480 grid and then follow the same path (D039). How image files
reach our process is **not confirmed yet** (§6).

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
   → `156 passed` (or the count in the freeze record).
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
3. **Watch the log** in a second terminal: `tail -f "$OUT/trial_log.csv" | cut -d, -f6,8,77`. Each new image adds one
   `file,status,path` line within ~1 s.
4. **Check the first few images:**
   - No status `wrong_size`. Column 77 (`path`) is `1080->640` for 1920×1080 frames (warped into the DEV grid with
     `frame_warp_1080.json`, D039) or `640` for 640×480 frames. Any other size (e.g. the 320×240 stream) is
     `wrong_size`: see §4.
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
| Status `wrong_size`, note e.g. `320x240, expected 640x480 or 1920x1080` | The images are neither 1920×1080 nor 640×480 (e.g. the 320×240 stream) | Ctrl-C. Ask CSI for the 1920×1080 images. Never resize or crop by hand |
| Status `wrong_size`, note `1920x1080, expected 640x480` (no `or 1920x1080`) | `frame_warp_1080.json` is missing from this copy, so 1080 frames can't be warped | Ctrl-C. Check the version and hashes (§0.1, or the preflight in §7); use the frozen package |
| Status `refused` | A dataset holdout frame (runs 4–5) arrived in the folder | Ctrl-C; take that folder out of use; tell Noor |
| Status `error` (the note has the message) | One frame failed; the program keeps going | One-off: note it. Repeated: Ctrl-C, start again with a new `OUT`, log it as an intervention |
| A new image is in `IN` but no trial-log line appears | It isn't `.png` / `.jpg` / `.jpeg`, or its name starts with `.` (ignored) | `ls -la "$IN"`; ask CSI for the file type |
| Trial-log lines keep coming but no event for minutes | The arm stays over the fixture, or the scene never holds still for 4 s; or `frame_t` doesn't increase (files without a timestamp in the name, all copied at once) | Check the statuses (`arm` / `settling`) and column 7; if `frame_t` is flat, stop and tell Noor (§6) |
| Boxes on the overlay don't sit on the holes; many holes UNSURE or WAITING that look filled | The camera view differs from the position map | Ctrl-C; take one photo of the screen; tell Noor. Never re-aim or move the camera (CSI rule) |
| The program crashed, or the terminal closed | — | Start again with a **new** `OUT` (§1). Images already in `IN` are processed again into the new session. Log the restart as an intervention |

## 5. Staged test images: score them only after their labels are locked
- The 22 staged images are the sealed test (D036). Their labels are adjudicated and **locked first** (the labels CSV
  and its sha256 written down) before any output is looked at. Each arm is scored once.
- Keep them in their own folder that is **never** `IN`. While staging, `live_inspect.py` is stopped or watching a
  different folder.
- Command (on the GB10 right after the labels are locked, §7 step 4; or later on the Mac), once per arm:
  `<python> live_inspect.py --source replay:<staged dir> --gate each --out results/live/staged_<arm>_<time>`
  (Mac: `<python>` = `../.venv/bin/python`, add `--inspector resnet` for arm A; the ResNet is not in the GB10 package).
  For the ResNet, also run `--threshold preregistered` into its own `OUT` and report it next to the D038 result.
- `--gate each` scores every arm-clear image on its own: each staged setup is an independent fixture, and its fill
  frontier comes from that image alone (tested: two different fixtures in a row give the same result as each alone).
  **Never add `--track`** here: the tracker carries MISSED latches from one image to the next. Images are taken in
  time order (time in the name, else file time); the order does not change any result. An image with the arm over
  the fixture is logged `arm` and not scored.

## 6. Open before the freeze
- CSI: how images reach our process on the GB10 (folder path, which stream, file names with a timestamp or not:
  the event rule needs a real frame time, otherwise the file's modification time is used); a screen for the overlay.
- 1920×1080 is handled by the D039 warp; the 320×240 stream is not supported (`wrong_size`).
- An on-screen operator window that refreshes itself (today: the overlay file only).
- The frozen inspector and thresholds (R4); the full robustness tests (R8); the freeze record and hashes (R11).
- Measured on this Mac (DEV run 1 replay): rule median 27 ms per scored image, ResNet (MPS) 74 ms; 1.3 ms per other
  image (R7 target ≤ 1 s); a 1920×1080 frame adds ~3.4 ms for the warp. ResNet start-up (torch, model load, warm-up)
  takes about 2.5 s before its first line.

## 7. Monday Oct 26 on CSI's GB10: start to stop
Our software runs on CSI's GB10 (aarch64 Linux) from the frozen package, rule inspector only (no torch, no Isaac). The
package brings its own Python 3.11 and wheels and installs offline; it writes only inside its own folder.
Rehearsed Oct 23 on the YAAD Spark (NVIDIA DGX Spark, GB10, Ubuntu 24.04.3, glibc 2.39, no system Python):
unpack → `PREFLIGHT OK` in **5 s**; package 243 MB (596 MB unpacked); DEV run 1 replayed at 640 and as 1080 copies
gave the same states and scores as the Mac, hole for hole.

**Bring:** USB stick with `ttl_gb10_<sha>.tar` + `ttl_gb10_<sha>.tar.sha256` (built from the freeze commit), room on it
for the results; printed staging list, label sheet and this section; paper log.

1. **Before 12:30 (≈5 min): install and check.** Open a terminal on the GB10.
   ```bash
   lsblk -o NAME,SIZE,MOUNTPOINT                 # find the stick, e.g. /media/<user>/<label>
   USB=/media/<user>/<label>
   mkdir -p ~/ttl && cp "$USB"/ttl_gb10_<sha>.tar* ~/ttl/ && cd ~/ttl
   sha256sum -c ttl_gb10_<sha>.tar.sha256        # -> ttl_gb10_<sha>.tar: OK
   tar -xf ttl_gb10_<sha>.tar && cd ttl_gb10_<sha> && bash bootstrap.sh
   ```
   Expected (Spark, 5 s in total):
   ```
   == 1/5 checksums (0 s)
   SHA256SUMS OK (40 files)
   == 2/5 code (0 s)
   commit <the freeze commit>
   == 3/5 python (0 s)
   python /home/<user>/ttl/ttl_gb10_<sha>/pyhome/python/bin/python3 (Python 3.11.17), wheels/cp311
   == 4/5 venv + install (1 s)
   numpy                  2.4.6
   opencv-python-headless 5.0.0.93
   == 5/5 preflight (4 s)
   os / kernel / arch aarch64 / glibc / python 3.11.17 / numpy 2.4.6 / opencv 5.0.0 / torch not installed (not needed)
   code     <sha> (archive)
   sha256   ...  (one line per runtime file; check them against the freeze record)
   still_1080  1 frames, path 1080->640, {'WAITING': 30}; vs Mac: 0 holes differ, max |score diff| 0 -> OK
   run1_640   10 frames, path 640, {'UNSURE': 39, 'PASS': 79, 'MISSED': 10, 'WAITING': 172}; vs Mac: 0 holes differ, max |score diff| 0 -> OK
   run1_1080  10 frames, path 1080->640, {'UNSURE': 36, 'PASS': 82, 'MISSED': 10, 'WAITING': 172}; vs Mac: 0 holes differ, max |score diff| 0 -> OK
   PREFLIGHT OK -> .../preflight_out/preflight.json
   BOOTSTRAP OK in 5 s
   ```
   Hashes to check by eye: `rule_thresholds.json` 322c29ec…, `frame_warp_1080.json` 9837b298…, `position_map_G.json`
   7ffaf48c…, `registration_dev.json` 6dd0de1b….
   If it stops with `BOOTSTRAP FAILED: ...`:
   - `SHA256SUMS mismatch`: copy the tar again from the stick.
   - `bundled Python not usable here; trying the system Python`: this line alone is fine if a `python ...` line and `OK`
     follow. `no usable Python`: stop and tell Noor (no install on CSI's machine without CSI's OK).
   - `offline install failed`: only if CSI allows internet on the GB10: `bash bootstrap.sh --online`. Else stop.
   - `preflight`: **don't run.** Note which set says `FAIL`; results on this machine would differ from the Mac.
   Then, for every later step:
   ```bash
   cd ~/ttl/ttl_gb10_<sha>/code/twin_to_line
   PY=../../venv/bin/python
   ```
2. **The camera folder.** `IN=/path/where/the/images/arrive` (from CSI). Check one image:
   `ls -lt "$IN" | head -3` and `$PY -c "import cv2,sys; print(cv2.imread(sys.argv[1]).shape)" "$IN/<newest file>"`
   → `(1080, 1920, 3)` (or `(480, 640, 3)`). Anything else (e.g. `(240, 320, 3)`): ask CSI for the 1920×1080 images.
3. **12:30 staging.** CSI saves one image per staged setup into a folder `STAGED` that is never `IN`. Nothing runs on
   `STAGED` yet. Noor and Tony fill the label sheet per setup.
4. **Staged stills, only after the labels are locked** (§5): the label CSV is complete and its sha256 is on the paper
   log (`sha256sum <labels csv>`). Then, once:
   ```bash
   OUT=results/live/staged_rule_$(date +%Y%m%d_%H%M%S)
   $PY live_inspect.py --source replay:"$STAGED" --gate each --out "$OUT" --note "sealed staged test, rule arm, Oct 26"
   ```
   Expected: `inspector rule_yellow_seat  rule_thresholds.json 322c29ec2ea9`, one line per image,
   `event  N  <file> K=<last filled hole> delay   0.0s  <state counts>`, then `22 frames, 22 events, {'scored': 22} -> <OUT>`.
   An image with the arm over the fixture is counted as `arm` and gets no event line. Every image is scored on its
   own; never add `--track`.
5. **Live run (events gate).**
   ```bash
   OUT=results/live/csi_live_$(date +%Y%m%d_%H%M%S)
   $PY live_inspect.py --source folder:"$IN" --out "$OUT" --note "CSI live run, Oct 26"
   ```
   Expected: the inspector line, then nothing until the first event. In a second terminal
   `tail -f "$OUT/trial_log.csv" | cut -d, -f6,8,77` shows one `<file>,<status>,1080->640` line per new image within
   ~1 s (Spark: 0.3–0.4 s). After 4 s of a still fixture with the arm away: `event N <frame> K=.. delay 4.0s ...`.
   Operator view: `$OUT/overlay_latest.png`, rewritten after each event (open it with the image viewer, e.g.
   `xdg-open "$OUT/overlay_latest.png"`, and reopen after each event line).
   **If frames arrive only one at a time** (saved on a trigger, or seconds apart): look at
   `cut -d, -f6,7,8 "$OUT/trial_log.csv"` (file, frame time, status).
   - Images ≥ 4 s apart while the fixture stays the same: the event comes with the second image (its delay = the gap).
   - Every image shows a new fixture state, or `frame_t` doesn't increase: the status stays `settling` and no event line
     ever comes. Ctrl-C and start again into a **new** `OUT` with `--gate each`: every arm-clear image is then scored on
     its own (Spark: scored 0.4 s after the file appeared). Log the restart as an intervention.
6. **Stop.** Ctrl-C once → `N frames, M events, {...} -> <OUT>`; `session.json` has `"stop_reason": "ctrl-c"`.
7. **Copy the results to the stick, with sha256.**
   ```bash
   cd ~/ttl && tar -cf ttl_results_20261026.tar -C ttl_gb10_<sha> preflight_out code/twin_to_line/results/live
   sha256sum ttl_results_20261026.tar > ttl_results_20261026.tar.sha256
   cp ttl_results_20261026.tar ttl_results_20261026.tar.sha256 "$USB"/ && sync
   (cd "$USB" && sha256sum -c ttl_results_20261026.tar.sha256)     # -> ttl_results_20261026.tar: OK
   ```
   Keep `~/ttl` on the GB10 until the stick has been checked on the Mac (`shasum -a 256 -c`); then remove it only if
   CSI asks. Delete nothing else on CSI's machine.
