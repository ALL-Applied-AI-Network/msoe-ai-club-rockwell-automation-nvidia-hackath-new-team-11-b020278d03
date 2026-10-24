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
   → `166 passed` (or the count in the freeze record).
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
     on mps  results/train/resnet18_v1/model.pt 8380851f8b4e`.
   - `watching <IN>: N image(s) already there are ignored; new images only`: images already in `IN` at the start
     (e.g. the staged test images in the camera folder) are never read; `session.json` records N.
   - `operator view: this console (one grid per event), <OUT>/overlay_latest.png, or <OUT>/view.html in a browser`.
     Then nothing until the first event.
   - Within ~2 s, `$OUT` contains `overlays/`, `predictions.csv`, `session.json`, `trial_log.csv` and `view.html`.
   - In `session.json`, `"git"` is the frozen commit **without** `+modified`.
3. **Watch the log** in a second terminal: `tail -f "$OUT/trial_log.csv" | cut -d, -f6,8,77`. Each new image adds one
   `file,status,path` line within ~1 s.
4. **Check the first few images:**
   - No status `wrong_size`. Column 77 (`path`) is `1080->640` for 1920×1080 frames (warped into the DEV grid with
     `frame_warp_1080.json`, D039) or `640` for 640×480 frames. Any other size (e.g. the 320×240 stream) is
     `wrong_size`: see §4.
   - Column 7 (`frame_t`) is monotonic time when the validated file version was seen, in seconds
     (`cut -d, -f6,7 "$OUT/trial_log.csv"`). Folder mode uses this one clock regardless of filenames or mtimes;
     replay keeps filename timestamps.
   - Images already in `IN` when you start are ignored (the start line says how many); only images that arrive
     after the start are read, in arrival order.

## 2. While it runs
- **Normal statuses:**
  - `arm`: arm over the fixture, nothing is scored.
  - `settling`: waiting for 4 s of stillness.
  - `unchanged`: same fixture state as the last event.
  - `scored`: an event.
- **Event lines.** One per event: `event N <frame> K=<last filled hole> delay <s>  <state counts>`. The delay is
  normally 4.0 s (the stillness rule).
- **Operator view (primary): the console grid** printed under every event line, the 30 holes as the camera sees
  them (G26 … G01 across the top row, as in the staging doc), then the counts. DEV run 1, event 18:
  ```
      G26 .     G21 .     G16 ok    G11 ??    G06 ok    G01 ??
      G27 .     G22 .     G17 ok    G12 ??    G07 MISS  G02 ok
      G28 .     G23 .     G18 .     G13 ??    G08 ok    G03 ok
      G29 .     G24 .     G19 .     G14 ??    G09 ok    G04 ok
      G30 .     G25 .     G20 ??    G15 ??    G10 ok    G05 ok
      PASS 10  DEFECT 0  MISSED 1  UNSURE 7  WAITING 12    (ok = PASS  DEF = DEFECT  MISS = MISSED  ?? = UNSURE  . = WAITING)
  ```
  In a terminal the codes are coloured (green ok, red DEF, magenta MISS, yellow ??, dim .).
- **Operator view (extra, if there is a browser):** open `$OUT/view.html` (`xdg-open "$OUT/view.html"`, or drag it into
  the browser). It reloads `overlay_latest.png` every second over `file://`; the image is replaced atomically (temp
  file + rename), so a half-written overlay is never shown. Earlier events stay in `$OUT/overlays/eNN_<frame>.png`.
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
| `FileNotFoundError: ... frame_warp_1080.json` at startup | The required warp file is missing; startup stops while hashing runtime files | Restore the frozen package and check its hashes (§0.1 or §7) before restarting |
| `WARNING folder ...`, status `source_error` | The watched directory cannot be listed (e.g. disconnected mount or permissions) | The runtime retries every `--poll` seconds and logs `source_recovered` on recovery; restore access. If `--idle-exit` ends during the outage, `session.json` records the source error |
| Status `refused` | A dataset holdout frame (runs 4–5) arrived in the folder | Ctrl-C; take that folder out of use; tell Noor |
| Status `error` (the note has the message) | One frame failed; the program keeps going | One-off: note it. Repeated: Ctrl-C, start again with a new `OUT`, log it as an intervention |
| A new image is in `IN` but no trial-log line appears | It isn't `.png` / `.jpg` / `.jpeg`, or its name starts with `.` (ignored) | `ls -la "$IN"`; ask CSI for the file type |
| Trial-log lines keep coming but no event for minutes | The arm stays over the fixture, or successive observed images never show the same setup for 4 s | Check `arm` / `settling`; for independent stills saved on request, restart with `--gate each` (§7.5) |
| Boxes on the overlay don't sit on the holes; many holes UNSURE or WAITING that look filled | The camera view differs from the position map | Ctrl-C; take one photo of the screen; tell Noor. Never re-aim or move the camera (CSI rule) |
| The program crashed, or the terminal closed | — | Start again with a **new** `OUT` (§1). Images already in `IN` are ignored by the new session, so images that arrived while it was down are not read. Log the restart and the gap as an intervention |

## 5. Staged test images: don't run the software on them on the day
- The 22 staged images are the sealed test (D036). On the day they are only **copied off to the USB stick with their
  sha256** (§7 step 4). Monday evening their labels are adjudicated and locked (the labels CSV and its sha256 written
  down) before any output is looked at. Then each arm is scored once.
- They stay out of every run on the day: CSI saves them in the camera folder, and the live run starts only after
  staging is done; folder mode ignores the images already in `IN` at its start (§1.2).
- Scoring later (after the labels are locked, on the Mac), once per arm:
  `../.venv/bin/python live_inspect.py --source replay:<staged dir> --gate each --inspector <rule|resnet> --out results/live/sealed_<arm>`.
  For the ResNet, also run `--threshold preregistered` into its own `OUT` and report it next to the D038 result.
- `--gate each` scores every arm-clear image on its own: each staged setup is an independent fixture, and its fill
  frontier comes from that image alone (tested: two different fixtures in a row give the same result as each alone).
  **Never add `--track`** here: the tracker carries MISSED latches from one image to the next. An image with the arm
  over the fixture is logged `arm` and not scored.

## 6. Open before the freeze
- CSI: how images reach our process on the GB10 (folder path or stream URL, and capture cadence); a screen for the
  overlay. Folder mode times validated arrivals; replay uses filename times, falling back to modification times.
- 1920×1080 is handled by the D039 warp; the 320×240 stream is not supported (`wrong_size`).
- Operator view: the console grid (primary) and `view.html` (needs a browser on the GB10; checked in Chrome over
  http://127.0.0.1 because the test browser could not open `file://`).
- How frames arrive (new files, one rewritten file, a live stream, stills on request) decides the §7 step 5 command.
  Folder mode re-reads a file written again under the same name; stream mode is untested on a live camera.
- The frozen inspector and thresholds (R4); the full robustness tests (R8); the freeze record and hashes (R11).
- Measured on this Mac (DEV run 1 replay): rule median 27 ms per scored image, ResNet (MPS) 74 ms; 1.3 ms per other
  image (R7 target ≤ 1 s); a 1920×1080 frame adds ~3.4 ms for the warp. ResNet start-up (torch, model load, warm-up)
  takes about 2.5 s before its first line.

## 7. Monday Oct 26 on CSI's GB10: start to stop
Our software runs on CSI's GB10 (aarch64 Linux) from the frozen package, rule inspector only (no torch, no Isaac). The
package brings its own Python 3.11 and wheels and installs offline; it writes only inside its own folder.
Rehearsed Oct 23 on the YAAD Spark (NVIDIA DGX Spark, GB10, Ubuntu 24.04.3, glibc 2.39, no system Python):
unpack → `PREFLIGHT OK` in **5 s**; package 243 MB (596 MB unpacked); DEV run 1 replayed at 640 and as 1080 copies
gave the same states and scores as the Mac, hole for hole. The system-Python fallback (bundled Python disabled), as
a non-root user with the package in the home folder, passed in arm64 Ubuntu 22.04 (Python 3.10) and 24.04 (Python
3.12) containers: `PREFLIGHT OK` in 6 s and 5 s, identical to the Mac.

**Bring:** USB stick with `ttl_gb10_<sha>.tar` + `ttl_gb10_<sha>.tar.sha256` (built from the freeze commit), room on it
for the results; printed staging list, label sheet and this section; paper log.

1. **Before 12:30 (≈5 min): install and check.** Open a terminal on the GB10.
   ```bash
   lsblk -o NAME,SIZE,MOUNTPOINT                 # find the stick, e.g. /media/<user>/<label>
   USB=/media/<user>/<label>
   mkdir -p ~/ttl && cp "$USB"/ttl_gb10_<sha>.tar* ~/ttl/ && cd ~/ttl
   sha256sum -c ttl_gb10_<sha>.tar.sha256        # -> ttl_gb10_<sha>.tar: OK
   test ! -e ttl_gb10_<sha> || { echo "Use a fresh folder; keep existing results"; exit 1; }
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
   - `results already exist`: bootstrap refuses before cleanup or installation. It never deletes or moves results.
     Keep that folder; unpack the original tar into a fresh parent folder and run its `bootstrap.sh`. This includes
     `preflight_out` from an earlier successful or failed preflight. Do not unpack over an existing installation.
   - `SHA256SUMS mismatch`: copy the tar again from the stick.
   - `bundled Python not usable here; trying the system Python`: this line alone is fine if a `python ...` line and `OK`
     follow. `no usable Python`: stop and tell Noor (no install on CSI's machine without CSI's OK).
   - `offline install failed`: only if CSI allows internet on the GB10: `bash bootstrap.sh --online`. Else stop.
   - `preflight`: **don't run.** Note which set says `FAIL`; results on this machine would differ from the Mac.
   Preflight compares the bundled **still images** only: every state must match and all scores must be finite with
   score difference exactly **0**. Video decoding is outside preflight's scope. The package also carries a
   checksummed metadata-only `data_index/image_index.csv` to refuse known protected still filenames without raw data.
   Then, for every later step:
   ```bash
   cd ~/ttl/ttl_gb10_<sha>/code/twin_to_line
   PY=../../venv/bin/python
   ```
2. **How do frames arrive?** Ask CSI, then pick the row (step 5 uses it). Saved files: `IN=<the folder>`, and check
   one image with `$PY -c "import cv2,sys; print(cv2.imread(sys.argv[1]).shape)" "$IN/<newest file>"` →
   `(1080, 1920, 3)` (or `(480, 640, 3)`; anything else, e.g. `(240, 320, 3)`, is `wrong_size`: ask for 1920×1080).
   A live stream: `SRC=<the RTSP or HTTP URL>`. Raw camera devices require the folder/stills fallback below.
3. **12:30 staging.** Nothing of ours runs during staging. CSI saves one image per staged setup, in the camera
   folder `IN`. Noor and Tony fill the label sheet per setup (image file name ↔ setup).
4. **Staged images: copy them off, don't run anything on them** (§5). Copy exactly the images on the label sheet:
   ```bash
   ls -lt "$IN" | head -25                         # the staged images, newest first
   mkdir -p ~/ttl/staged_20261026 && cp -p "$IN"/<each staged file> ~/ttl/staged_20261026/
   cd ~/ttl && tar -cf staged_20261026.tar staged_20261026 && sha256sum staged_20261026.tar > staged_20261026.tar.sha256
   cp staged_20261026.tar staged_20261026.tar.sha256 "$USB"/ && sync
   (cd "$USB" && sha256sum -c staged_20261026.tar.sha256)     # -> staged_20261026.tar: OK
   ls ~/ttl/staged_20261026 | wc -l                 # -> 22
   ```
   Monday evening on the Mac: adjudicate and lock the labels, then score once per arm (§5).
5. **Live run, only after staging is done.** Always from `~/ttl/ttl_gb10_<sha>/code/twin_to_line`, with
   `OUT=results/live/csi_live_$(date +%Y%m%d_%H%M%S)` (a new one for every start) and the row that matches step 2:

   | Frames arrive as | Command (`$PY live_inspect.py` + …) | Expected first lines (after the `inspector …` line) |
   |---|---|---|
   | New image files in a folder | `--source folder:"$IN" --out "$OUT"` | `watching <IN>: N image(s) already there are ignored; new images only` |
   | One file rewritten again and again (same name) | the same command | the same; the trial log repeats that file name, one row per new version |
   | A live video stream (RTSP / HTTP URL) — **untested on a live camera** | `--source stream:"$SRC" --every 1.0 --out "$OUT"` | `stream <SRC>: live source, newest frame every 1 s; …`, then `stream <SRC>: connected, 1920x1080` |
   | A raw camera device on the GB10 (`0`, `/dev/video0`) | Ask CSI to save images; use `--source folder:"$IN" --out "$OUT"` (add `--gate each` for independent stills) | Direct device mode is refused because its reads cannot be bounded |
   | Stills saved only on request (CSI saves one image per fixture state) | `--source folder:"$IN" --gate each --out "$OUT"` | `watching <IN>: …`; then one event line + grid per saved still |
   | Nothing reachable | no live run; staging is unaffected | — |

   All rows go through the same path (size switch, D039 warp, event gate, rule) and print the `operator view: …` line,
   then nothing until the first event. After 4 s of a still fixture with the arm away (`--gate each`: at once):
   `event N <frame> K=.. delay 4.0s ...` and under it the 6×5 grid (§2), the primary operator view. Extra, if the GB10
   has a browser: `xdg-open "$OUT/view.html"` (reloads the latest overlay every second). In a second terminal
   `tail -f "$OUT/trial_log.csv" | cut -d, -f6,8,77` shows one `<frame>,<status>,<path>` line per frame (folder: within
   ~1 s of the file appearing, Spark 0.3–0.4 s; stream: one per `--every` s, named `stream_<UTC time>`).
   - **Stream drops:** `WARNING stream <SRC>: dropped after N frames; reconnecting in 2 s` (or `cannot open; retrying`)
     is logged and the stream is reopened. FFmpeg open and read calls each request a 5 s timeout. A watchdog prints
     `WARNING ... no new frame for 10 s` and requests release and reconnect. Release happens after the reader returns,
     with a further bounded 5.5 s wait. If the backend ignores the deadlines, the source stops and prints the
     folder/stills fallback; it does not accumulate blocked reader threads. Devices or backends without bounded reads
     require CSI to save files: `--source folder:"$IN"` (independent stills: add `--gate each`). FFmpeg may print its own lines (e.g.
     `Stream ends prematurely`); they are harmless. If an RTSP stream keeps dropping, try
     `export OPENCV_FFMPEG_CAPTURE_OPTIONS="rtsp_transport;tcp"` before the command. Checked Oct 23 only against a
     local MJPEG-over-HTTP server (connect, event after 4.1 s, drop, reconnect, Ctrl-C) and the DEV run 1 video as a
     file (same 18 events as the replay); the GB10's aarch64 OpenCV decodes video slightly differently from the Mac
     (3 of 540 DEV holes, all at rule thresholds, changed state).
   - **Files that arrive one at a time** (saved on a trigger, or seconds apart): look at
     `cut -d, -f6,7,8 "$OUT/trial_log.csv"` (file, frame time, status). Images ≥ 4 s apart while the fixture stays the
     same: the event comes with the second image (its delay = the gap). Every image a new fixture state, or `frame_t`
     not increasing: the status stays `settling` and no event ever comes. Then Ctrl-C and start again into a **new**
     `OUT` with `--gate each` (the "stills on request" row): every arm-clear image is scored on its own (Spark: 0.4 s
     after the file appeared). Images that arrived before the restart are ignored. Log the restart as an intervention.
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
