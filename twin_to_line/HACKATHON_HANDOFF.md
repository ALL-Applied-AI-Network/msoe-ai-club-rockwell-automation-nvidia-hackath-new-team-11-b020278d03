# Twin-to-Line — Handoff (read first)
Updated: 2026-10-22, 2:45 pm CT. One handoff, two identical copies: `twin_to_line/HACKATHON_HANDOFF.md` (canonical, in
git) and the Claude Project doc `claude/hackathon-handoff.md`. Decisions: `DECISIONS.md` (D001–D036, same two-copy rule).
**The repo copies of this file and DECISIONS.md are behind the Project copies (Oct 22) — sync them first (plan step 0).**
Detailed plan to Oct 26: Project doc `claude/next-session-plan.md` (repo copy `twin_to_line/NEXT_SESSION_PLAN.md`).
New session: work from `~/code/ignite`, run `git status` first, read the plan, then this, continue from **NEXT ACTION**.
Do not reopen settled decisions without new evidence. Replace stale facts; no diary. **Never put passwords, tokens,
invitation links, team codes or auth URLs in this file or in memory** (that includes the CSI VPN password and the
YAAD team code).

## Standing rules
- Workflow: coherent feature branch → tests → commit → push → PR → teammate review → **never self-merge**.
- **Right now:** `feat/scene-generator` stays **local and unpushed** until the team agrees on integration and ownership
  and Noor explicitly authorizes a push. Don't merge PR #1, don't change `main`, don't modify the frozen gate.
- Never overwrite Noor's unstaged edit in `twin_to_line/dose_sets.py` (blank lines in the argparse block; his, not
  ours). Stage files by name, never `git add -A` / `-u`.
- No AI/assistant attribution anywhere (no "Generated with …", no Co-Authored-By, no signatures). Tool credits go in the
  final submission's references.
- Never commit raw data, the twin, the labeler zip/images, renders, results, CSI images or model weights.
- Draft messages for Noor to send; don't send. Write them short and plain (Noor's preference; Shamar did not understand
  the first, technical request). CSI sessions and team decisions stay **unconfirmed** until approved.
- Working setup: ChatGPT = technical lead/reviewer, Claude = implementation engineer, Noor = product owner (final calls,
  talks to teammates/organizers). Noor is a Code Crusaders **member, not captain**: "compare and decide together".

## Status (Thu Oct 22, 2:45 pm)
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
  - **V1–V4 pass, B6 visible:** checked by Claude on both panels and all six full frames **before** reading ΔE; Noor
    to confirm.
  - **Hard checks pass:** G0 0.76/0.87 px · G1 0.725 · A1 30/30 · A2 318/310 = 1.03.
  - **Bands, run 1 → run 2 (prediction):** B1 19.1 → **8.7 OK** (8.7) · B2 21.7 → **13.3 OK** (13.3) · B3 14.3 → 9.8
    OK (9.8) · B4 14.4 → 7.2 OK (8.2) · B5 0.54 → **0.41 WORK** (0.41) · B6 OK.
  - **Outcome (§5): PASS WITH WORK**, the same row as run 1; B5 is the only WORK item.
  - **Regressions vs run 1** (all inside their limits):
    - G0 median 0.57 → 0.76 px; G1 0.735 → 0.725; A2 0.99 → 1.03.
    - Crooked-cap ratios: centroid t20 2.68 → 2.46, t30 4.21 → 3.92; elongation t20 1.12 → 0.08, t30 1.78 → 0.71.
      Scope still **SUPPORTED**.
    - Synthetic frame std 65.7 → 80.5 (real 65.2); plate spread 8.5 → 7.4 (real 17.9).
  - **Cost:** instance up ~17:48 UTC, stop issued 18:13, STOPPED by 18:21 ≈ 25–33 min ≈ $1.8–2.4 (the console has
    the billed figure); stopped, not deleted.
  - **Files** (gitignored): `results/isaac_gate/run2/` (report, evidence, probe log); tarballs in
    `~/Downloads/isaac_gate_run2/`. Run 1 files unchanged (88 sha256 re-checked).
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
- **Gate WORK after run 2: only B5 (frame luminance 0.41) is still open.** B1 and B2 are fixed by `work1` and
  verified.
  - B5 needs a scene decision, not lights or materials: either the station-frame part near the lens, or composing the
    MagneMover + facility.
  - Awaiting review (ChatGPT/Noor) before any dataset.
  - Training renders would use the `work1` overlay (the generator inherits its base light and cap values; the
    generator's randomization ranges are not yet re-checked against it).
- **No synthetic-trained ResNet-18 exists.** Synthetic-to-real transfer is untested. No transfer claim anywhere.
- **No live runtime exists** (camera frames → 30 per-hole results on screen + trial log). Most parts exist offline
  (`positions.py`, `fill_state.py`, `inspect_frame.py` event detection, `eval_metrics.py`); the live wrapper does not.
- Known generator limits (D035): tilted caps use the gate's approximate rim pivot (twin cap mesh has no interior);
  at 40° 29/240 crooked caps leave the runtime crop box (none at ≤35°); smoke labels are 58% empty positions (5,200 of
  9,000, mostly WAITING) → rebalance at training; materials vary per scene, not per cap; lifted caps (~0.3 px at 5 mm)
  are physically crooked but likely invisible, so smoke excludes them; leans limited to 0.95–4.47° by the twin's holes.
- When generated on a Brev instance from a `brev copy` (no `.git`), `run.json` shows git commit "unknown"; the
  generator's sha256 still identifies the code.

### 3. Pending team decisions (Code Crusaders) — architecture is a PROPOSAL (D031)
1. **Live runtime owner — blocks the Oct 26 demo.** Ask Vang whether his "m8 inspection pipeline" is this; avoid two
   runtimes. If nobody owns it by Fri Oct 23, Noor + Claude build the minimum version (plan §4).
2. Which inspector leads: synthetic-only ResNet-18 (proposed) or the counterfactual / Vang's pipeline (scored either way).
3. Train on twin renders only, not Dataset 1 real images.
4. Sealed test = the Oct 26 staged images (+ runs 4–5 + organizer release); **every arm freezes Sun Oct 25 night** (D036).
5. Owners: counterfactual (Vang + Trevor?), compute (Vang?), labels (Tony?), video/summary/business case (Zara?). Noor
   proposed for twin geometry, synthetic pipeline, ResNet-18, scorer.
6. Compute split: Brev for the gate and renders; YAAD Spark (team exists) — who drives it.
7. Crooked-cap scope: pre-registered at ≥20° (D036) — team to acknowledge.
8. Integration: whether/where `feat/scene-generator` is pushed (stacked on PR #1's branch).

### 4. External dependencies
- **CSI (Shamar Webster), email sent Oct 22, awaiting reply.** Asked: (1) camera resolution at the final vial station —
  640×480 or 1920×1080 — before the session; (2) one ~90-min supervised session **Mon Oct 26, 1 pm** (or next slot):
  robot stopped, we hand-place vials/caps in the Good fixture, CSI saves one image per setup, then a short supervised
  live run with our software reading the camera (hardware demo); (3) how our laptop gets camera images without plugging
  into the plant network (shared folder or a CSI PC); (4) backup slot Wed Oct 28 or Thu Oct 29. Attendees: Noor, Tony.
  **Unconfirmed.** If no reply by Fri Oct 23 noon, post the short version in `#data-and-testbed-requests` tagging him.
  Not yet raised with him: side photos of tilted caps, filming the line, the optional live-defect demo (plan §2.6).
- **Organizer question (narrowed, optional):** may the color-rule baseline use thresholds fitted on supplied runs 1–3?
  Only matters if renders fail and the rule baseline needs real-image thresholds (plan §7–8). Real-data training is off.
- **PR #1 (Code Crusaders):** open, unmerged; holds the shared position mapping, fill-state logic and evaluation tools.
  Needs teammate review. The Ignite remote also has `origin/feat/organizer-feedback-integration`.
- Dataset 1 organizer release (1920×1080) not on the Mac yet (link in Slack `#dataset-1-vial-inspection`) — needed now
  in case the live camera is 1920×1080.

## NEXT ACTION (Thu Oct 22, rest of day) — first GPU run
**Done Oct 22 evening (steps 1–9; results under Completed): gate PASS WITH WORK; stopped for review (ChatGPT/Noor).
Do not rerun the gate as-is; the next gate run follows the review's twin-only WORK fixes.**
**Provision a Brev GPU, run the frozen gate unchanged, get the first verified renders.** Then continue with
`claude/next-session-plan.md`. Stop and ask Noor before creating anything that costs money.
1. `brev refresh && brev list` → expect org `UWM/MSOE-Team-25`, no instances (or only ones a teammate made — don't touch).
2. Pick a GPU in the Brev console (Isaac Sim launchable). Must have RT cores: **RTX PRO 6000** preferred, **L40S**
   fallback; not A100/H100 (no RT cores). Twin is tested with **Isaac Sim 6.0**. Note **$/hr**, tell Noor, get a yes.
3. Create the instance on the shared credits; `brev shell <instance>` works; note GPU, driver, Isaac version.
4. From the Mac: `brev copy ~/code/ignite/twin_to_line <instance>:/home/ubuntu` (branch `feat/scene-generator` checked
   out, so the generator ships with the gate kit; gate files unchanged). If the instance can't download the twin from
   Drive, also copy the twin zip: `brev copy ~/Downloads/'Copy of csi_digital_twin.zip' <instance>:ignite_gate/twin.zip`.
5. Gate, exactly as frozen (`GATE_v2.0.2.md` §11): `RATE_PER_HR=<$/hr> bash ~/twin_to_line/run_gate.sh`
   → expect "kit files match MANIFEST.sha256", six `exit=0` lines, `DONE -> ~/ignite_gate/results.tar.gz`.
   No changes to thresholds, scenes, references, materials or lighting; no runs 4–5.
6. Generator on the instance (scenes sublayer the twin by relative path, so generate where you render):
   ```bash
   cd ~/ignite_gate
   sha256sum ~/twin_to_line/gen_scenes.py            # expect 006b7196faf36cf6...
   venv/bin/python ~/twin_to_line/gen_scenes.py csi_digital_twin_v1 --selftest            # expect: selftest passed
   venv/bin/python ~/twin_to_line/gen_scenes.py csi_digital_twin_v1 scenes_smoke --config ~/twin_to_line/configs/smoke.json --seed 0
   venv/bin/python ~/twin_to_line/gen_scenes.py csi_digital_twin_v1 scenes_sweep --config ~/twin_to_line/configs/tilt_sweep.json
   # expect for each: "labels OK: Nx30 ..." and "physical checks OK ..."
   ```
7. Small representative render (frozen `render_keep.py`, one Isaac start per scene). `ISAAC_PY` = the "Isaac python:"
   line in `~/ignite_gate/run_log.txt`. Smoke scenes cover pass / missing cap / no vial; sweep 00025 = 20°, 00041 = 30°
   crooked caps (direction 0°), 00000 = all seated.
   ```bash
   mkdir -p renders_check crops_check; ALL=$(python3 -c "print(','.join(f'G{i:02d}' for i in range(1,31)))")
   for s in scenes_smoke/scenes/smoke_00000 scenes_smoke/scenes/smoke_00001 scenes_smoke/scenes/smoke_00002 \
            scenes_sweep/scenes/tilt_sweep_00000 scenes_sweep/scenes/tilt_sweep_00025 scenes_sweep/scenes/tilt_sweep_00041; do
     n=$(basename $s)
     "$ISAAC_PY" ~/twin_to_line/render_keep.py --twin csi_digital_twin_v1 --camera CapSealCam --stage $s/scene.usda \
        --out renders_check/$n.png --subframes 64 > renders_check/$n.log 2>&1; echo "$n exit=$?"
     venv/bin/python ~/twin_to_line/cut_crops.py renders_check/$n.png $s/labels.json crops_check/$n $ALL
   done
   tar czf check.tar.gz renders_check crops_check scenes_smoke/run.json scenes_sweep/run.json
   ```
   → expect 6 `exit=0` lines and 30 crops each. Copy back both tarballs (`brev copy <instance>:/home/ubuntu/ignite_gate/<file> ~/Downloads/`).
8. **Stop the instance** as soon as renders are copied (`brev stop <instance>` or Stop in the console). Record GPU,
   Isaac version, per-render seconds and cost here.
9. On the Mac: `compare_gate.py` per `GATE_v2.0.2.md` §11 → record PASS / PASS WITH WORK / FAIL / INCONCLUSIVE exactly
   as its frozen rule says, then **stop for review** (ChatGPT/Noor). Check the 6 check renders by eye: boxes in each
   `overlay.png` land on vials; hidden caps/vials are absent; lighting and cap colour differ between smoke scenes;
   tilted caps visibly differ from seated at 20°/30°.
After the gate (Fri): batch renderer (one Isaac session for many scenes; `render_keep.py` restarts Isaac per scene, so
300 scenes that way is infeasible) and the live runtime. No ResNet training before the gate result.

## Milestones (proposed; CSI items unconfirmed) — revised Oct 22 (D036)
Oct 22 GPU gate run (G1/G2) + YAAD (done) · Oct 23 camera answer from CSI, gate review, batch renderer, live runtime
skeleton, organizer release downloaded · Oct 24 training renders + synthetic-only ResNet-18 + runtime integrated and
replay-tested · Oct 25 G3 check on DEV runs 1–3 (go if ≥90% DEV defect observations caught at ≤5% false alarms;
development signal only), dry run, **freeze by Sun night** · **Mon Oct 26 1 pm CSI visit (Noor + Tony): staged sealed
test + live demo** · Oct 26–27 adjudicate labels, score every arm once · Oct 28–29 backup slot if needed; error
analysis; business case · Oct 30 final evaluation write-up · Oct 31 video, one-page summary, docs · **Sun Nov 1
11:59 pm CT final submission** (~5-min video, one-page summary, repo, references) · Thu Nov 5 5–8 pm finals, MSOE
Diercks Hall. Gate definitions and fallbacks F1–F4: proposal doc, "Go/no-go gates".

## Project and proposed architecture (D002, D031)
**Twin-to-Line**, Rockwell × NVIDIA Physical AI Innovation Lab, Challenge 1 / Dataset 1 (Final Vial Inspection), Good
fixture G01–G30. Claim: the twin cuts the real defect data and line time needed to commission inspection.
- Offline (GPU): twin position map → Isaac renders with exact labels + randomization (`gen_scenes.py`) → synthetic-only
  ResNet-18 (thresholds from synthetic validation, D033) → freeze record.
- Live (laptop): frame source → event gating (arm-clear frames) → 30 crops (`positions.py`) → inspector (ResNet-18;
  rule baseline alongside) → fill state (`fill_state.py`, LIVE_FILL, D021) → operator map + trial log. No PLC
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
  - `cc-isaac-gate-2` (Mumbai ap-south-1, g6e.4xlarge L40S, **$4.38/hr**) is **stopped** after gate run 2.
  - Create instances from the console (CLI launch fails). Stop instances whenever idle. No personal spending (D010).
- Dan Schneider's Oct 16 Brev org for Noor (as Ignite captain, $500): relation to `UWM/MSOE-Team-25` not confirmed —
  don't spend from two orgs without Noor saying so.
- **YAAD GPU Lab** (CSI, free): 8 DGX Sparks (aarch64); team workspace exists, Noor joined Oct 22 (login above; VPN
  first; files deleted after the event; put a password on any open port; use tmux for long jobs). Who drives the Spark:
  undecided. Isaac Sim 6.0.0 and 5.1.0 images run on the Sparks (YAAD guide). **Correction:** usd-core 26.11 ships
  Linux aarch64 wheels for Python 3.11–3.14 (not 3.10), so `gen_scenes.py` can run in a Spark venv with Python ≥3.11
  (not yet tried). Renders made on a Spark must be checked against the Brev check renders before training on them.
- UWM GB10 (Shamar): no access; `GB10_PREFLIGHT.md` ready. build.nvidia.com usable. AI tool accounts per team: pending.

## Source of truth and paths
- Ignite repo: https://github.com/ALL-Applied-AI-Network/msoe-ai-club-rockwell-automation-nvidia-hackath-new-team-11-b020278d03
  · `main` @ `2a935de` (unchanged) · `feat/organizer-feedback-integration` @ `2189e3a` (also on origin; PR #1's work) ·
  `feat/scene-generator` @ `5c69c9f` + a local docs commit (closeout) — **local only**.
- Local clone `~/code/ignite`, project dir `twin_to_line/`, venv `~/code/ignite/.venv` (Python 3.11, usd-core 26.08,
  NumPy 2.4.6, OpenCV). Repo-root `README.md` is the organizers' — leave it.
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
git status -sb                                   # expect: ## feat/scene-generator  +  " M twin_to_line/dose_sets.py"
shasum -a 256 -c MANIFEST.sha256                 # expect: 8 lines ending OK (gate-v2.0.2)
shasum -a 256 -c PROTOTYPE_SNAPSHOT.sha256       # expect: 4 x OK
IGNITE_TWIN=~/Downloads/csi_digital_twin/csi_digital_twin_v1 ../.venv/bin/python -m pytest tests -q   # expect: 91 passed
../.venv/bin/python gen_scenes.py ~/Downloads/csi_digital_twin/csi_digital_twin_v1 --selftest            # expect: selftest passed
../.venv/bin/python eval_metrics.py --selftest
../.venv/bin/python inspect_frame.py --run 1 --events [--track]      # DEV runs only
ssh yt-codecrusaders6286@172.30.102.94           # YAAD Spark; FortiClient VPN connected first
```

## Known risks
- **Live runtime has no owner and does not exist yet; freeze is Sun Oct 25 night.** Without it the Oct 26 visit is data
  collection only and the demo moves to the backup slot.
- **Camera resolution unknown.** If the live camera is 1920×1080, the position map must be re-solved and training renders
  made with that camera — decide Fri before rendering the training set.
- **Laptop access to the camera unknown** (no plant-network connection allowed without approval).
- Isaac/launchable version may differ from 6.0 (recorded, not a reason to change the kit); Isaac in Docker → run inside
  it with `ISAAC_PY=…`; Drive download on the instance may fail → `brev copy` the twin zip.
- `render_keep.py` restarts Isaac per scene → batch renderer needed before 300+ renders.
- UsdPreviewSurface material/light overrides and liquid may render differently in RTX (check renders).
- Crooked caps below ~20° may be physically unresolvable from this camera (D005/D006/D023); real caps may not hold a
  chosen tilt → stage the natural tilt and measure it from the side photo.
- Color rules may match any model on missing cap / no vial; the honest competitor stays in every report.
- Team may keep the counterfactual / Vang's pipeline as primary; the scorer, gates and generator are useful either way.
