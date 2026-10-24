# Twin-to-Line — Handoff (read first)
Updated: 2026-10-23 (Fri) night CT. One handoff, two identical copies: `twin_to_line/HACKATHON_HANDOFF.md` (canonical, in
git) and the Claude Project doc `claude/hackathon-handoff.md`. Decisions: `DECISIONS.md` (D001–D039, same two-copy rule).
**The Project copies of this file and DECISIONS.md are behind the repo copies (Oct 23: D037–D039, gate run 2, training,
G3, 1080 frames, GB10 package) — Noor syncs them from these.**
Detailed plan to Oct 26: Project doc `claude/next-session-plan.md` (repo copy `twin_to_line/NEXT_SESSION_PLAN.md`).
New session: work from `~/code/ignite`, run `git status` first, read the plan, then this, continue from **NEXT ACTION**.
Do not reopen settled decisions without new evidence. Replace stale facts; no diary. **Never put passwords, tokens,
invitation links, team codes or auth URLs in this file or in memory** (that includes the CSI VPN password and the
YAAD team code).

## Standing rules
- Workflow: coherent feature branch → tests → commit → push → PR → teammate review → **never self-merge**.
- **Right now:** `feat/scene-generator` and `feat/live-runtime` stay **local and unpushed** until the team agrees on
  integration and ownership and Noor explicitly authorizes a push. Don't merge PR #1, don't change `main`, don't
  modify the frozen gate.
- Never overwrite Noor's unstaged edit in `twin_to_line/dose_sets.py` (blank lines in the argparse block; his, not
  ours). Stage files by name, never `git add -A` / `-u`.
- No AI/assistant attribution anywhere (no "Generated with …", no Co-Authored-By, no signatures). Tool credits go in the
  final submission's references.
- Never commit raw data, the twin, the labeler zip/images, renders, results, CSI images or model weights.
- Draft messages for Noor to send; don't send. Write them short and plain (Noor's preference; Shamar did not understand
  the first, technical request). CSI sessions and team decisions stay **unconfirmed** until approved.
- Working setup: ChatGPT = technical lead/reviewer, Claude = implementation engineer, Noor = product owner (final calls,
  talks to teammates/organizers). Noor is a Code Crusaders **member, not captain**: "compare and decide together".

## Status (Sat Oct 24)
### 1. Completed and verified
- **Scene generator** on local branch `feat/scene-generator`, commit `5c69c9f` (parent `2189e3a`, PR #1's branch
  `feat/organizer-feedback-integration`). New: `gen_scenes.py`, `configs/smoke.json` (300 scene definitions),
  `configs/tilt_sweep.json` (130), `tests/test_gen_scenes.py` (22 tests), README section.
  **Verified on Noor's Mac (Oct 21):** 91/91 tests pass · `gen_scenes.py --selftest` passes · `MANIFEST.sha256` 8 × OK ·
  no gate file modified. Also checked in a Linux container with Noor's exact usd-core 26.08 + NumPy 2.4.6: same results;
  repeated runs byte-identical (603 smoke / 263 sweep files), scenes identical across USD 26.08/26.11.
  What it checks: labels read back from each composed USD stage vs the authored spec; physical rules (seat height, cap on
  its vial, vial inside its plate hole, neighbour collisions); USD camera vs `CapSealCam.json`; seated projection vs
  `position_map_G.json` (≤0.01 px). Six deliberately broken copies of the generator each failed the tests.
- **Proposal doc** "Twin-first inspection plan (proposal)":
  https://claude.ai/code/artifact/7e742133-103c-483e-8409-8aca3b5e131e (private until Noor shares it). Its Session A/B
  structure is superseded by D036.
- **Brev access (Noor):** org **`UWM/MSOE-Team-25`**, **$500 shared credits**; Brev CLI **v0.6.337** on the Mac;
  `brev login`, `brev refresh`, `brev list` OK. **Vang authorized creating a GPU instance.** CLI `brev launch` of the
  Isaac Launchable failed 3× with "Internal Server Error" (g7e.2xlarge ×2, g6e.2xlarge); the console works.
- **First GPU gate run (Oct 22, 23:22–23:26 UTC):** instance `cc-isaac-gate` (console, Isaac Launchable), g6e.4xlarge,
  1× L40S 46 GB, driver 595.71.05, 16 vCPU, $3.65/hr; **Isaac Sim 6.0.1-rc.7** in the launchable's `vscode` container
  (`/isaac-sim/python.sh`; container had no `python3`, so `python3 python3-venv` were apt-installed there — environment
  only). Kit uploaded alone (§11; no real frames/labels). `run_log.txt`: "kit files match MANIFEST.sha256", twin from
  Drive (station `293d74ba…` = Mac copy), 6 × `exit=0`, 33–39 s per render (one Isaac start each), script 228 s ≈ $0.23.
  Validity X1–X5 all clear → valid run. Hard checks G0 (0.57/0.85 px), G1 (IoU 0.735), A1 (30/30), A2 (307 vs 310 px)
  pass. **Outcome (§5): PASS WITH WORK**, decided by the row "valid, no FAIL condition, and ≥ 1 of B1–B6 in WORK".
  V1–V4 and B6 checked by Claude, blind to ΔE; confirmed by Noor: V1–V4 pass, B6 visible. (Blind look = baseline/t00
  full frames + crops of all six; the t10/t20/t30/liquid full frames were viewed for V4 after ΔE was read. Outside the
  intended G02/G03 changes only ≤3-px path-tracing specks differ between renders.) Bands: B1 cap ΔE 19.1 WORK ·
  B2 plate ΔE 21.7 WORK · B3 hole interior ΔE 14.3 OK · B4 wall ΔE 14.4 OK · B5 frame luminance
  |57.3−123.3|/123.3 = 0.54 WORK (renders about half as bright as real) · B6 OK. Per §5: stop; WORK items are
  twin-only fixes (materials, lights), verified by re-running this same rule before any dataset. Crooked-cap scope (§6):
  SUPPORTED (t20 centroid shift 2.68× real seated spread, t30 4.21×). Results on the Mac (gitignored):
  `results/isaac_gate/run1/` (report, evidence), tarballs in `~/Downloads/isaac_gate_1022/`.
- **Gate run 2: post-WORK verification, colours calibrated on DEV runs 1–3 (Oct 23, 18:09–18:13 UTC).**
  - **Instance change:** `cc-isaac-gate` could not restart ("Capacity is unavailable in this region"; it now shows
    FAILURE, left untouched). Run 2 used **`cc-isaac-gate-2`**: console, Isaac Launchable, **Mumbai (ap-south-1)**,
    g6e.4xlarge, 1× L40S, driver 595.71.05, **$4.38/hr (was $3.65/hr)**, same Isaac Sim 6.0.1-rc.7 `vscode`
    container (`python3 python3-venv` apt-installed again, environment only).
  - **Uploaded:** kit + overlay only; the twin came from Drive on the instance (station `293d74ba…`, camera
    `0376842d…` = Mac copy).
  - **Twin-only fix `work1`** (`twin_fix.py`, commit `9849d00`): overlay twin `twin_fix1` next to the untouched twin.
    Both RectLights +0.75 EV (key 2864.79 → 4817.98, fill 1002.68 → 1686.29); cap `diffuseColor` blue 0.10 → 0.00.
    - Values were fixed before the render, from run 1 + DEV runs 1–3 only. The pooled DEV targets equal the gate's
      reference values, so in effect this is calibration on the gate references.
    - `--check`: only those 3 values differ (299 prims, 4,031 properties); variant labels = run 1's.
  - **Diagnosis behind it:**
    - Tone map is ACES (pre-gate probe, no render: `/rtx/post/tonemap/op = 6`, auto-exposure
      `/rtx/post/histogram/enabled = False`); no clipping; sRGB fine.
    - The left third of the frame is station-frame satin steel about 0.2 m from the lens rendering black; 8 % of
      the frame has no station geometry. So B5 cannot reach OK with lights or materials.
  - **Execution:** `run_log.txt`: "kit files match MANIFEST.sha256", 6 × `exit=0`, 34–36 s per render, script 214 s
    ≈ $0.26. X1–X5 clear → valid run.
  - **V1–V4 pass, B6 visible:** checked by Claude on both panels and all six full frames **before** reading ΔE;
    **confirmed by Noor** (Oct 23; Claude in chat also checked the run 2 panels).
  - **Hard checks pass:** G0 0.76/0.87 px · G1 0.725 · A1 30/30 · A2 318/310 = 1.03.
  - **Bands, run 1 → run 2 (prediction):** B1 19.1 → **8.7 OK** (8.7) · B2 21.7 → **13.3 OK** (13.3) · B3 14.3 → 9.8
    OK (9.8) · B4 14.4 → 7.2 OK (8.2) · B5 0.54 → **0.41 WORK** (0.41) · B6 OK.
  - **Outcome (§5): PASS WITH WORK**, the same row as run 1; B5 is the only WORK item. **Final gate result (D037):**
    PASS WITH WORK in every report; B5 is a known scene-composition limitation outside the 30 inspected crops; no
    further gate fixes.
  - **Regressions vs run 1** (all inside their limits):
    - G0 median 0.57 → 0.76 px; G1 0.735 → 0.725; A2 0.99 → 1.03.
    - Crooked-cap ratios: centroid t20 2.68 → 2.46, t30 4.21 → 3.92; elongation t20 1.12 → 0.08, t30 1.78 → 0.71.
      Scope still **SUPPORTED**.
    - Synthetic frame std 65.7 → 80.5 (real 65.2); plate spread 8.5 → 7.4 (real 17.9).
  - **Cost:** instance up ~17:48 UTC, stop issued 18:13, STOPPED by 18:21 ≈ 25–33 min ≈ $1.8–2.4 (the console has
    the billed figure); stopped, not deleted.
  - **Files** (gitignored): `results/isaac_gate/run2/` (report, evidence, probe log); tarballs in
    `~/Downloads/isaac_gate_run2/`. Run 1 files unchanged (88 sha256 re-checked).
- **Training set `train_v1` (Oct 23, `cc-isaac-gate-2`, ~19:09–20:40 UTC).** `configs/train_v1.json` +
  `configs/tilt_train.json` on the `work1` overlay, recipe `configs/recipe_dev.json` (DEV runs 1–3 only, sha
  `0ea15f52…`), code `9fcee85`.
  - **Checks fixed beforehand, both passed:** batch renderer vs `render_keep.py` mean diff 0.87 / 0.87 / 0.007 grey
    (limit 2.0), lens byte-identical to `tools/apply_lens.py`; recipe pre-flight wall |dL| 0.98, |db| 0.5, cap median
    ΔE 2.15, saturated cap b* 73 vs pale 47.
  - Labels generated on the instance = Mac labels (only float noise ≤ 9e-13 from its newer usd-core/numpy).
  - Renders 520/520 + 48/48 ok, 0 errors, 7.1 s/scene in one Isaac session (`render_batch.py`); render + crops + pack
    4,004 s.
  - **17,040 crops:** pass 7,289 · no_vial 3,801 · crooked 3,275 · missing 2,675. Validation by scene: 113 scenes,
    3,390 crops.
  - Copy back: 190 MB pack, sha256 `a0aaa329…` on both ends, 18,184 inner hashes OK. Files (gitignored):
    `results/train_v1/`; tarball in `~/Downloads/isaac_train_v1/pack/`.
  - Access: direct ssh started rejecting the Brev key mid-session (`brev exec` still worked); `brev refresh` fixed it,
    address unchanged.
  - **Cost:** up ~19:09 UTC, stopped by Noor from the console ~20:38, STOPPED by 20:45 ≈ 1.5 h ≈ $6.5–6.9 (the
    console has the billed figure); stopped, not deleted.
- **Synthetic-only ResNet-18 v1 (Oct 23, Mac MPS, `train_resnet.py` @ `097eaa3`).** ImageNet weights; design and
  threshold rule fixed before any training render; 15 epochs, 27 min; no real image read.
  - Synthetic validation is saturated: accuracy 1.000 from epoch 3 (one dip to 0.981 at epoch 6); final epoch kept.
    Highest non-defect score 0.008, lowest defect score 0.9966.
  - **Threshold (pre-registered rule):** t_defect = 0.99968 → validation defect recall 0.995 (6 of 1,200 missed:
    5 crooked → pass, mostly 20° tilts; 1 missing → no_vial); false alarms 0 on pass and on no_vial.
    t_catch_every_val_defect = 0.99664, also 0 false alarms.
  - **D038 (Noor, Oct 23, before any DEV evaluation):** deployed t = midpoint of the empty validation gap
    (0.007852 … 0.996635) = **0.50224** (`thresholds_d038.json` sha `338c955e…`); the pre-registered 0.99968 is
    reported next to it everywhere. The 99.5 % rule had dropped 6 validation defects scored ≥ 0.9966.
  - Files (gitignored): `results/train/resnet18_v1/` (`model.pt` sha `8380851f…`, `thresholds.json` sha
    `e9f4b5c5…`, `run.json`, `val_predictions.csv`).
- **G3 on DEV runs 1–3 (Oct 23, run once, `g3_check.py` @ `250cf5a`): NO-GO.** Pipeline = live defaults: one frame
  per placement event (20 events), DEV offset map, `inspect_frame.inspect`, LIVE_FILL, frontier WAITING, no tracker;
  583 usable draft labels (32 defect, 551 non-defect observations). Development signal only; no retuning.
  - **ResNet-18 v1 at D038 t = 0.50224:** recall **1.000 (32/32)**, false positives **87.7 % (483/551)** → fails
    ≤ 5 %. Per class (detection / exact class): crooked 19/19 / 12/19, missing 12/12 / 12/12, missed placement
    1/1 / 0/1. False alarms: 89 of 112 real passes → DEFECT (75 read as crooked); 394 of 439 trailing empties → 165
    DEFECT + 229 MISSED.
  - **At the pre-registered t = 0.99968:** recall 0.469 (15/32; crooked 2/19, missing 12/12, missed 1/1),
    false positives 55.9 % (308/551).
  - eval_metrics' false-alarm rate at full recall (t 0.844) is 38.3 %, so the failure is the model, not the
    threshold choice.
  - **Failure modes:**
    - Real empty holes read as uncapped vials: 166 of 440 → missing_cap, mostly the lighter top-row holes.
    - Real seated caps read as crooked: median defect score 0.94.
    - Each false "occupied" hole moves the fill frontier, turning the empties before it into MISSED (e.g. run 2:
      G28 → 13 MISSED).
  - **Rule baseline, same pipeline (reference only; thresholds fitted on these labels):** recall 31/32, false
    positives 14/551 (2.5 %), which reproduces D021.
  - Per the plan's fallback (NEXT_SESSION_PLAN, G3 no-go): the rule baseline runs live; ResNet-18 is still scored
    offline as arm A. The step-9 inspector choice is Noor's.
  - Files (gitignored): `results/g3/resnet18_v1/` (`g3_report.json`, predictions per arm, `probabilities.csv`,
    `annotated/`).
- **v2 attempt (D040, Sat Oct 24): check render failed 3 tries → no batch, no v2 model, no v2 G3.** `cc-isaac-gate-2`,
  code `5fd0930`; `twin_fix2 --check` OK, selftest passed, 18/18 check renders ok. Medians, 87 empty / 27 uncapped crops:

  | | real DEV | train_v1 | try 1 | try 2 | try 3 |
  |---|---|---|---|---|---|
  | empty core L* (E1) | 13–33 | 14.8 | 29.3 ✓ | 33.2 ✗ | 31.7 ✓ |
  | empty lit floor L* (E2) | 41–65 | 21.3 | 37.3 ✗ | 41.2 ✓ | 39.6 ✗ |
  | empty b* (E3) | 13–18 | 7.4 | 20.5 ✗ | 19.2 ✗ | 15.0 ✓ |
  | uncapped mouth L* (U1, ±3 of v1) | 43.4–48.0 | 20.4 | 28.7 ✗ | 30.8 ✗ | 28.9 ✗ |
  | uncapped mouth b* (U2, ±3 of v1) | 11.3–15.0 | 5.5 | 13.1 ✗ | 12.9 ✗ | 11.1 ✗ |
  | uncapped lit floor L* (U3) | — | 75.5 | 75.5 ✓ | 75.1 ✓ | 75.2 ✓ |

  Floor per try (value × blue): 1.0/1.0 → ×1.1872/×1.15 → ×0.9281/×1.15. Findings, not acted on: (1) E1–E3 never held
  together; the rendered hole is flatter than real (lit floor − core ≈ 8 L*). (2) U1/U2 are coupled to E2: an
  uncapped vial's mouth looks through the open vial onto the same floor, so a brighter floor lifts it too; the moves
  went **toward** the real uncapped range, but D040's "no worse" is ±3 of v1 either way. Any new try = Noor's OK + new
  decision + new spend. **Arm A stays v1** (no v2 exists); live inspector stays the rule baseline.
  Cost: start 16:55:37 UTC, stop issued 17:02:11, STOPPED by 17:08:37 ≈ 7–13 min ≈ $0.48–0.95 (console has the billed
  figure); stopped, not deleted. Files (gitignored): `results/train_v2_check/`; tar `~/Downloads/isaac_train_v2/check_only/`
  (sha256 `2f328206…`, matched both ends).
- **1920×1080 frames (D039, Oct 23, `2504904`).** CSI's 1080 still of the empty Good fixture
  (`results/csi_1080/csi_1080_empty_G.jpg`, sha256 `673a76a6…`, not in git) is the cap_seal view at a higher
  resolution: the 640×480 frames are its centre 4:3 part scaled by ~1/2.25.
  - Frozen transform `frame_warp_1080.json` (sha256 `9837b298…`, `register_1080.py`): a similarity registered image to
    image onto the DEV run-3 empty frame: scale 2.24918, rotation +0.009°, offset (239.83, −5.39) px. Station-only,
    G-only and S-only fits agree within 0.32 px at the 30 holes; OpenCV ECC affine within 0.05 px.
  - `live_inspect.py` picks by size: 640×480 as is; 1920×1080 → `frame_warp.py` (INTER_AREA) → the unchanged 640 path
    (map + DEV offset, gate, rule thresholds, crops); any other size `wrong_size`. Trial-log column `path`; the
    transform's sha256 in `session.json`.
  - Warped still: holes 30/30, median 1.74 px, mean (−1.67, +0.16), vs run 3's 1.68 px, (−1.57, +0.12); rule 30 WAITING.
  - DEV runs 1–3 as 1080 copies (`replay_1080.py`; geometry and plumbing only): identical events and statuses; 4 of
    600 holes differ (labelled pass, at rule thresholds); recall 31/32 on both; false positives 14/551 vs 10/551 (from
    the round trip's smoothing, not a 1080 result). **Not yet tested on real 1080 frames with caps.**
  - The twin-hole fit `position_map_G_1080.json` (`5cc73fb`) is evidence only: 1.75 px off the DEV grid (hole-vs-cap bias).
- **GB10 package + YAAD Spark rehearsal (Oct 23, `a72c51b`…`23b6764`).** `gb10/build_package.py` (Mac, from HEAD)
  builds `results/gb10_pkg/ttl_gb10_<sha>.tar` (243 MB, not in git): git archive (`ARCHIVE_COMMIT` filled in), standalone
  CPython 3.11.17 aarch64, aarch64 wheels (cp311/cp312: numpy 2.4.6 + opencv-python-headless 5.0.0.93 = the Mac;
  cp310: numpy 2.2.6), preflight frames (the still + 10 DEV run-1 event frames at 640 and 1080) with the Mac's
  predictions. `bootstrap.sh`: checksums → code → Python → offline install → `live_inspect.py --preflight`.
  - YAAD Spark (DGX Spark, GB10, Ubuntu 24.04.3, glibc 2.39; bare container, no python3/tmux/scp): unpack →
    `PREFLIGHT OK` in 5 s. DEV run 1 at 640 and as a 1080 copy built there: identical to the Mac (18 events, 0 of 540
    holes differ, score difference 0). Folder mode with the still: scored 0.4 s after the copy, 30 WAITING.
  - System-Python fallback (bundled Python disabled, non-root user, package in the home folder), arm64 Ubuntu 22.04
    (Python 3.10) and 24.04 (3.12) containers on the Mac: `PREFLIGHT OK`, identical to the Mac.
  - Spark folder `/workspace/ttl_rehearsal_1023` (4.5 GB: packages, DEV run 1 frames + 1080 copy, a runs-1–3-only
    index) is kept for the Sunday dry run; delete it after the event.
- **Frame sources (Oct 23).** Folder mode re-reads a file rewritten under the same name (mtime or size;
  a read that races a rewrite is dropped). `--source stream:<url|device|file>` (cv2.VideoCapture): a live source is read
  in a thread, the newest frame passed on every `--every` s, drops logged and reconnected; a video file gives one frame
  per `--every` s of its own timestamps. DEV run 1 video as a file: same 18 events and states as the replay. Local
  MJPEG-over-HTTP server: connect, event, drop, reconnect, Ctrl-C all fine. **Untested on a live camera.** The cp311 and
  cp312 aarch64 wheels decode the run 1 mp4 in an Ubuntu 24.04 arm64 container (33,662 frames, identical between the
  two) with the same 18 events as the Mac; 3 of 540 holes at rule thresholds changed state (the decode differs
  slightly from macOS).
- **Monday readiness in `live_inspect.py` (Oct 23).** Staged stills with `--gate each` (no `--track`) are scored each on
  their own (tested). Folder mode ignores images already in the folder at start (the camera folder will hold the staged
  images). Operator view: a console grid per event in the camera layout (primary), the overlay replaced atomically,
  and `view.html` reloading it every second (checked in Chrome over http://127.0.0.1; the test browser can't open
  `file://`). `LIVE_RUNBOOK.md` §7 is the Monday procedure.
- **Generator on the GPU (Oct 22):** selftest passed; smoke 300×30 and tilt sweep 130×30 labels OK + physical checks
  OK on the instance. 6 check renders `exit=0`, 34 s each, 30 crops each (`results/isaac_gate/check1/`). All-seated
  sweep 00000 vs gate baseline: mean abs diff 1.0 grey level. Eye checks: boxes on vials; hidden caps/vials absent;
  smoke lighting differs (frame mean 49/45/59), cap colour only slightly; 20°/30° caps visibly differ from seated.
  Handoff step-7 command bug: `render_keep.py` resolves a relative `--stage` against `--twin`, so pass an absolute
  path (`$PWD/$s/scene.usda`); first attempt rendered nothing (logs kept in `renders_check_try1`).
  Instance up ~22:53 UTC, stop issued 23:33, STOPPED 23:40 ≈ 40–47 min ≈ $2.45–2.90 (console has the billed
  figure); stopped, not deleted. Sizing: 34 s/render with one Isaac start per scene → 430 scenes ≈ 4.1 h ≈ $15.
- **YAAD access (Noor, Oct 22):** joined the Code Crusaders team on the YAAD site; CSI VPN (FortiClient) connects;
  SSH works: `ssh yt-codecrusaders6286@172.30.102.94` (VPN first); lands as root, `/workspace` empty.
- **CSI request sent (email to Shamar, Oct 22)** — see External dependencies. **Staging list doc** for the session:
  https://claude.ai/artifact/P1WRYUf2vJb2kUR2XPHTKh (private until shared; 22 images; ground-truth log columns).
- **Discord (Oct 22, 2:26 pm):** Noor posted a short update (CSI request, YAAD, first Brev GPU test today). Vang
  replied: "I'm working on the m8 inspection pipeline right now" — what "m8" means is **not yet clarified**.

### 2. Implemented but NOT verified
- **Generator overrides only partly checked:** 3 smoke renders show different lighting; whether every light and
  material override is honoured, and whether the variation looks realistic, is not measured yet.
- **Gate closed (D037, Oct 23): PASS WITH WORK.** B1 and B2 are fixed by `work1` and verified.
  - B5 (frame luminance 0.41) is recorded as a **known scene-composition limitation outside the 30 inspected crops**:
    the station-frame steel near the lens, plus no MagneMover or facility in station-only scenes.
  - No more gate fixes. Training renders use the `work1` overlay as their base.
- **Synthetic-only ResNet-18 v1 does not transfer to DEV frames (G3 NO-GO, 87.7 % false positives at D038).** Its
  synthetic validation is saturated and says nothing about real frames. No transfer claim anywhere; any model or
  threshold change after G3 needs Noor's OK and a new decision.
- **The live runtime `live_inspect.py` is verified on DEV replays (640 and 1080 copies, on the Mac and the Spark), the
  CSI 1080 still and synthetic folder runs.** Not yet tested on real 1080 frames with caps, on CSI's GB10, or with
  CSI's real camera folder (how frames arrive is unknown).
- Known generator limits (D035): tilted caps use the gate's approximate rim pivot (twin cap mesh has no interior);
  at 40° 29/240 crooked caps leave the runtime crop box (none at ≤35°); smoke labels are 58% empty positions (5,200 of
  9,000, mostly WAITING) → rebalance at training; materials vary per scene, not per cap; lifted caps (~0.3 px at 5 mm)
  are physically crooked but likely invisible, so smoke excludes them; leans limited to 0.95–4.47° by the twin's holes.
- When generated on a Brev instance from a `brev copy` (no `.git`), `run.json` shows git commit "unknown"; the
  generator's sha256 still identifies the code.

### 3. Pending team decisions (Code Crusaders) — architecture is a PROPOSAL (D031)
1. **Live runtime:** Noor + Claude built it (`live_inspect.py`, rule inspector, GB10 package). Tell Vang, and check that
   his "m8 inspection pipeline" doesn't duplicate it.
2. Which inspector leads: synthetic-only ResNet-18 (proposed) or the counterfactual / Vang's pipeline (scored either way).
3. Train on twin renders only, not Dataset 1 real images.
4. Sealed test = the Oct 26 staged images (+ runs 4–5 + organizer release); **every arm freezes Sun Oct 25 night** (D036).
5. Owners: counterfactual (Vang + Trevor?), compute (Vang?), labels (Tony?), video/summary/business case (Zara?). Noor
   proposed for twin geometry, synthetic pipeline, ResNet-18, scorer.
6. Compute split: Brev for the gate and renders; YAAD Spark: Noor's login, used for the GB10 rehearsal.
7. Crooked-cap scope: pre-registered at ≥20° (D036) — team to acknowledge.
8. Integration: whether/where `feat/scene-generator` is pushed (stacked on PR #1's branch).

### 4. External dependencies
- **CSI (Shamar Webster) answered Oct 23:**
  - Session **Mon Oct 26, 12:30–2 pm, confirmed** (staged sealed test, then the supervised live run).
  - The camera streams 320×240 and 1920×1080.
  - Our software runs on CSI's GB10, with no setup time beforehand.
  - He sent a 1080 empty-fixture still.
  **Not answered yet** (draft question in NEXT ACTION 1):
  - how frames reach our process on the GB10 (folder; new files or one rewritten name; which stream);
  - copying our 243 MB package onto it (USB) before 12:30; a screen to look at;
  - the GB10's OS, Python and internet (the package needs none of them);
  - the backup slot (Wed Oct 28 / Thu Oct 29).
  Never raised with him: side photos of tilted caps, filming the line, the optional live-defect demo (plan §2.6).
- **Organizer question (narrowed, optional):** may the color-rule baseline use thresholds fitted on supplied runs 1–3?
  Only matters if renders fail and the rule baseline needs real-image thresholds (plan §7–8). Real-data training is off.
- **PR #1 (Code Crusaders):** open, unmerged; holds the shared position mapping, fill-state logic and evaluation tools.
  Needs teammate review. The Ignite remote also has `origin/feat/organizer-feedback-integration`.
- Dataset 1 organizer release (1920×1080) not on the Mac yet (link in Slack `#dataset-1-vial-inspection`):
  development and evaluation only. Its labeler view sits +3.6° from the twin, unlike CSI's still (+0.4°).

## NEXT ACTION (from Sat Oct 24) — CSI question, v2 outcome, freeze + package, Monday
**Branch `feat/live-runtime`** (local only). `git status -sb` → `## feat/live-runtime` + ` M twin_to_line/dose_sets.py`.

**State (Oct 23 night):**
- 1920×1080 frames are handled by D039. The GB10 package passed on the YAAD Spark and in Ubuntu 22.04/24.04
  containers (all `PREFLIGHT OK`, identical to the Mac). The Monday procedure is `LIVE_RUNBOOK.md` §7.
- Live inspector = the rule baseline (ResNet-18 v1 G3 NO-GO; scored offline as arm A). `rule_thresholds.json` is
  DEV-fit (D033's organizer question is still open).
- The package in `results/gb10_pkg/` is pre-freeze: it is rebuilt Sunday from the freeze commit.

**Tasks, in order:**
1. **Noor asks Shamar (blocks the live run).** Draft, short and plain, not sent:
   > Hi Shamar, for Monday: when the camera saves an image, which folder on the GB10 does it land in, and is it the
   > 1920×1080 image (a new file each time, or one file that gets overwritten)? Can we copy one 250 MB folder from a
   > USB stick onto the GB10 before 12:30, and is there a screen where we can open an image? Thanks, Noor
2. **v2 attempt: done Oct 24, check render failed (no batch; see Status).** Arm A = v1. Open for Noor: drop v2 and go
   to the freeze, or a new decision for another try (U rule coupled to the floor; E1–E3 never held together).
3. **Sunday by 9 pm: freeze** (plan step 9): freeze record + hashes, tag locally. Then **rebuild the package from the
   freeze commit** (`../.venv/bin/python gb10/build_package.py`) and dry-run it on the Spark in a fresh folder:
   bootstrap → `PREFLIGHT OK`; DEV run 1 replay identical to the Mac; folder mode with the still. Copy the tar and its
   `.sha256` to the USB stick and check it there.
4. **Monday Oct 26:** `LIVE_RUNBOOK.md` §7. Staged images are only copied off (with sha256), never run on the day; the
   live run starts after staging; folder mode ignores the staged images already in the camera folder.
5. **Monday evening:** adjudicate and lock the staged labels (CSV + sha256), then score every arm once (§5).

## Milestones (proposed) — revised Oct 23
Oct 22 GPU gate run 1 · Oct 23 gate run 2 (closed, D037), training renders, ResNet-18 v1, G3 NO-GO, live runtime,
1080 frames (D039), GB10 package + Spark rehearsal (done) · Oct 24 v2 attempt (check render failed, no batch), CSI's
answer · Oct 25 **freeze by 9 pm**,
package rebuilt from the freeze commit, dry run on the Spark ·
**Mon Oct 26 12:30–2 pm CSI visit (confirmed; Noor + Tony): staged sealed test + live run on CSI's GB10** · Oct 26–27
adjudicate labels, score every arm once · Oct 28–29 backup slot if needed (unconfirmed); error analysis; business case
· Oct 30 final evaluation write-up · Oct 31 video, one-page summary, docs · **Sun Nov 1 11:59 pm CT final submission**
(~5-min video, one-page summary, repo, references) · Thu Nov 5 5–8 pm finals, MSOE Diercks Hall. Gate definitions and
fallbacks F1–F4: proposal doc, "Go/no-go gates".

## Project and proposed architecture (D002, D031)
**Twin-to-Line**, Rockwell × NVIDIA Physical AI Innovation Lab, Challenge 1 / Dataset 1 (Final Vial Inspection), Good
fixture G01–G30. Claim: the twin cuts the real defect data and line time needed to commission inspection.
- Offline (GPU): twin position map → Isaac renders with exact labels + randomization (`gen_scenes.py`) → synthetic-only
  ResNet-18 (thresholds from synthetic validation, D033) → freeze record.
- Live (CSI's GB10, from the package): frame source (1920×1080 → DEV 640×480 grid, D039) → event gating (arm-clear
  frames) → 30 crops (`positions.py`) → inspector (rule baseline live; ResNet-18 scored offline) → fill state
  (`fill_state.py`, LIVE_FILL, D021) → console grid + overlay + trial log. No PLC
  connection (D019), no connection to the plant network.
- Scoring: every arm writes the same predictions CSV, scored once on sealed real data (`eval_metrics.py`).
- Counterfactual / Vang's pipeline: optional, scored separately on eligible events + coverage (D034).
- Real-example experiment: **not run** (D036; D032 kept as designed). `dose_sets.py` still implements 5/10/20 (not
  updated; Noor has an unstaged edit there).

## Real-data boundary (D011, D025, D033, D036)
Runs 1–3: development/reference only, no fitting. Runs 4–5: holdout, never for training, thresholds, prompts, recipe or
model choice. Organizer release (1920×1080): development + evaluation only. **Oct 26 staged images: sealed final test,
labels adjudicated before any model runs on them, scored once after the Sun Oct 25 freeze; never training or tuning.**
No Session A. Unit = placement event or arrangement-position, never a frame. `rule_thresholds.json` was fitted on DEV
draft labels — not used for any scored arm unless organizers allow it; scored rule thresholds come from synthetic
validation. `labels/dev_labels.csv` = DRAFT labels.

## Organizer facts (Derek Riley Oct 16; guides fetched Oct 22)
- Derek: direction aligned, not exclusive · confirm training-data rules first (D025) · crooked cap = any cap not fully
  seated; a defined refinement is allowed (ours: ≥20°, D036) · a supervised live run counts as the hardware demo as long
  as our implementation runs on real hardware (D029) · no PLC/robot/placement-count data; no order-complete signal
  (D019, D021) · CSI numbering differs; G01–G30 is our twin convention (D022) · CSI requests: test plan, duration,
  attendees, dates; CSI confirms booking and supervision.
- Data Collection guide: requests go in `#data-and-testbed-requests` tagging Shamar (email fallback); a data request
  has 10 items (team/dataset, question, what to record, examples/counterexamples, camera/framing/resolution/frame
  rate, conditions, number/duration, labels/metadata, date needed, success criterion); extra collection is not
  guaranteed. May not: move/re-aim/disconnect/reconfigure a camera; change PLC, robot, FactoryTalk, safety, recipe or
  program; connect hardware to the industrial network without approval; place objects where they could collide with
  the robot. Before a physical test: freeze code and model, document inputs and expected outputs, start/stop
  procedure, metrics, failure handling tested on saved data, runs without changing plant controls. Trial log: every
  attempt with software version, model, input condition, prediction, expected result, latency, operator intervention.
- Dataset 1 page: real images are for understanding the station — "avoid training your models on them"; no test set is
  provided, keep your own separate; crooked_cap = visibly tilted or not seated, a leaning vial alone is not enough;
  report per class, false alarms and misses separately, false-alarm rate at the threshold that catches every known
  defect, complete fixture scenes; missed defects matter more than false alarms.
- NVIDIA vial labeler = manual review tool, 1920×1080 only, no class predictions (D027) · `damaged_vial` out of scope
  for v1, still counted (D026) · organizer grid consistent with the twin map (supporting evidence only, D024) ·
  strongest no-teach evidence: real 640×480 empty fixture, 30/30 holes, ~1.68 px median, no per-position teaching.

## Team and contacts
- **Code Crusaders** (Challenge 1): Zara, Matthew, Trevor, Vang, Anthony "Tony" Harvey (Data Science), Jamie Gill (CS),
  Noor ("Jatt" on Discord). Their Oct 14 plan (Vang): Isaac synthetic data + AOI baseline, twin-expected-state compare,
  reasoning-model escalation, FLUX.2 composites, Brev + DGX Spark. Trevor's own warning: a whole-scene twin compare
  breaks after the first defect (per-position crops + occupancy answer it). Vang (Oct 22): working on "the m8
  inspection pipeline".
- Team Ignite (old): repo preserved intact (D028); Haru, Jordan, Muhammad placement unknown. Tom Hershberger's answers
  on "Leave Team Ignite" and Ignite repo access: last recorded Oct 19, outcome not recorded here.
- Contacts: CSI/data/testbed Shamar Webster (`#data-and-testbed-requests`, webste63@uwm.edu; also YAAD help) · dataset
  Brett Storoe, Derek Riley, Tanner Cellio (`#dataset-1-vial-inspection`) · compute Dan Schneider (`#compute-questions`)
  · workspace/GitHub Brett Storoe (`#hackathon-general`) · program Tom Hershberger.

## Compute and resources
- **Brev (gate + renders):** team org `UWM/MSOE-Team-25`, $500 shared, Noor logged in via CLI v0.6.337, Vang
  authorized an instance.
  - `cc-isaac-gate` (g6e.4xlarge L40S, $3.65/hr) shows FAILURE: it could not restart Oct 23 (no capacity in its
    region); left untouched.
  - `cc-isaac-gate-2` (Mumbai ap-south-1, g6e.4xlarge L40S, **$4.38/hr**) is **stopped** after the v2 check render
    (Oct 24, STOPPED 17:08 UTC). `brev start` worked from the CLI (~1 min); ssh lands on the host, Isaac runs in the
    `vscode` container (`docker exec vscode …`). On Oct 24 `brev list` showed only this instance (`cc-isaac-gate` gone).
  - Create instances from the console (CLI launch fails). Stop instances whenever idle. No personal spending (D010).
- Dan Schneider's Oct 16 Brev org for Noor (as Ignite captain, $500): relation to `UWM/MSOE-Team-25` not confirmed —
  don't spend from two orgs without Noor saying so.
- **YAAD GPU Lab** (CSI, free): 8 DGX Sparks (aarch64); team workspace exists, Noor joined Oct 22 (login above; VPN
  first; files deleted after the event; put a password on any open port). Used Oct 23 for the GB10 rehearsal: key
  ssh works; our workspace is a bare container (no python3, tmux, scp or rsync), so copy with `tar -cf - … | ssh … 'tar
  -xf - -C …'` and run long jobs with `setsid nohup … &`. Isaac Sim 6.0.0 and 5.1.0 images run on the Sparks (YAAD guide). **Correction:** usd-core 26.11 ships
  Linux aarch64 wheels for Python 3.11–3.14 (not 3.10), so `gen_scenes.py` can run in a Spark venv with Python ≥3.11
  (not yet tried). Renders made on a Spark must be checked against the Brev check renders before training on them.
- CSI's GB10 (Shamar): no access before Monday; our software runs there from the package (`LIVE_RUNBOOK.md` §7).
  build.nvidia.com usable. AI tool accounts per team: pending.

## Source of truth and paths
- Ignite repo: https://github.com/ALL-Applied-AI-Network/msoe-ai-club-rockwell-automation-nvidia-hackath-new-team-11-b020278d03
  · `main` @ `2a935de` (unchanged) · `feat/organizer-feedback-integration` @ `2189e3a` (also on origin; PR #1's work) ·
  `feat/scene-generator` @ `d623eb4` (merged into the next) · **`feat/live-runtime` = the work branch** (1080 map
  `5cc73fb`, D039 `2504904`, GB10 package `a72c51b`…`23b6764`, Monday readiness after) — both **local only**.
- Local clone `~/code/ignite`, project dir `twin_to_line/`, venv `~/code/ignite/.venv` (Python 3.11, usd-core 26.08,
  NumPy 2.4.6, OpenCV, torch 2.14.1 / torchvision 0.29.1 with MPS). Repo-root `README.md` is the organizers' — leave it.
- Data (not in git): twin `~/Downloads/csi_digital_twin/csi_digital_twin_v1/` (station sha256 `293d74ba…`, camera JSON
  `0376842d…`); real `~/Downloads/csi-vial-fill-dataset/cap_seal/`; labeler `~/Downloads/vial-labeler-participants-20261014.zip`
  (same file as the Slack "auto labeling tool" link).
- Docs: next-session plan (Project `claude/next-session-plan.md`); staging list (above); proposal (above); old Ignite
  decision doc https://claude.ai/code/artifact/34a0c4d3-4d98-4a90-81d6-d6eee43c37fc (section 13 superseded by Project
  `claude/team-plan-final.md`, the submitted Ignite plan); `ORGANIZER_UPDATE_2026-10-16.md`; `GATE_v2.0.2.md` (frozen
  rule + runbook §11). Organizer guides: https://github.com/MSOE-AI-Club/maic-content/blob/main/unlisted/Rockwell-NVIDIA-Fall-2026-Data-Collection/Rockwell-NVIDIA-Fall-2026-Data-Collection.md
  and https://github.com/MSOE-AI-Club/maic-content/blob/main/unlisted/Rockwell-NVIDIA-Fall-2026-Vial-Inspection/Rockwell-NVIDIA-Fall-2026-Vial-Inspection.md

## Known-working commands (in `twin_to_line/`, Mac)
```bash
git status -sb                                   # expect: ## feat/live-runtime  +  " M twin_to_line/dose_sets.py"
shasum -a 256 -c MANIFEST.sha256                 # expect: 8 lines ending OK (gate-v2.0.2)
shasum -a 256 -c PROTOTYPE_SNAPSHOT.sha256       # expect: 4 x OK
IGNITE_TWIN=~/Downloads/csi_digital_twin/csi_digital_twin_v1 ../.venv/bin/python -m pytest tests -q   # expect: 166 passed
../.venv/bin/python gen_scenes.py ~/Downloads/csi_digital_twin/csi_digital_twin_v1 --selftest            # expect: selftest passed
../.venv/bin/python eval_metrics.py --selftest
../.venv/bin/python inspect_frame.py --run 1 --events [--track]      # DEV runs only
../.venv/bin/python live_inspect.py --source replay:results/live/replay_run1 --labels labels/dev_labels.csv --out <new dir>   # LIVE_RUNBOOK.md §0.4
../.venv/bin/python gb10/build_package.py         # GB10 package from HEAD (runtime files committed) -> results/gb10_pkg/
../.venv/bin/python live_inspect.py --preflight <pkg>/preflight --out <dir>   # package self-check (bootstrap runs it)
../.venv/bin/python register_1080.py              # re-checks the frozen 1080 transform; refuses to replace it
../.venv/bin/python replay_1080.py make results/live/replay_run1 results/live/replay_run1_1080   # DEV frames only
ssh yt-codecrusaders6286@172.30.102.94           # YAAD Spark; FortiClient VPN connected first
```

## Known risks
- **How frames reach our process on CSI's GB10 is unknown** (folder; new files or one rewritten name; a live stream).
  Covered by one pipeline (`LIVE_RUNBOOK.md` §7 step 5 table): folder mode (re-reads a rewritten file), `stream:`
  (RTSP/HTTP/device; **untested on a live camera**), stills on request with `--gate each`. The GB10's aarch64 OpenCV
  decodes video slightly differently from the Mac (DEV run 1: 3 of 540 holes at rule thresholds changed state).
- **CSI's GB10 itself is untested:** the package passed on the YAAD Spark and in Ubuntu 22.04/24.04 containers, but
  user rights, USB mounting and a screen there are unknown. Freeze: Sun Oct 25, 9 pm.
- **No real 1080 frame with caps yet** (D039): only the empty still and 1080 copies of DEV frames. The 320×240 stream
  is not supported (`wrong_size`).
- **The ResNet doesn't transfer (G3 NO-GO).** The training set was rendered with the 640×480 camera; the v2 attempt
  (D040) stopped at its check render, so v1 is the only model arm.
- Isaac/launchable version may differ from 6.0 (recorded, not a reason to change the kit); Isaac in Docker → run inside
  it with `ISAAC_PY=…`; Drive download on the instance may fail → `brev copy` the twin zip.
- Renders: `render_batch.py` (one Isaac session, 7.1 s/scene for `train_v1`); `render_keep.py` restarts Isaac per scene.
- UsdPreviewSurface material/light overrides and liquid may render differently in RTX (check renders).
- Crooked caps below ~20° may be physically unresolvable from this camera (D005/D006/D023); real caps may not hold a
  chosen tilt → stage the natural tilt and measure it from the side photo.
- Color rules may match any model on missing cap / no vial; the honest competitor stays in every report.
- Team may keep the counterfactual / Vang's pipeline as primary; the scorer, gates and generator are useful either way.
