# Twin-to-Line — Handoff (read first)
Updated: 2026-10-21 evening CT (session closeout). One handoff, two identical copies: `twin_to_line/HACKATHON_HANDOFF.md`
(canonical, in git) and the Claude Project doc `claude/hackathon-handoff.md`. Decisions: `DECISIONS.md` (D001–D035, same
two-copy rule). New session: work from `~/code/ignite`, run `git status` first, read this, continue from **NEXT ACTION**.
Do not reopen settled decisions without new evidence. Replace stale facts; no diary. **Never put passwords, tokens,
invitation links or auth URLs in this file or in memory.**

## Standing rules
- Workflow: coherent feature branch → tests → commit → push → PR → teammate review → **never self-merge**.
- **Right now:** `feat/scene-generator` stays **local and unpushed** until the team agrees on integration and ownership
  and Noor explicitly authorizes a push. Don't merge PR #1, don't change `main`, don't modify the frozen gate.
- Never overwrite Noor's unstaged edit in `twin_to_line/dose_sets.py` (blank lines in the argparse block; his, not
  ours). Stage files by name, never `git add -A` / `-u`.
- No AI/assistant attribution anywhere (no "Generated with …", no Co-Authored-By, no signatures). Tool credits go in the
  final submission's references.
- Never commit raw data, the twin, the labeler zip/images, renders, results or model weights.
- Draft messages for Noor to send; don't send. CSI sessions and team decisions stay **unconfirmed** until approved.
- Working setup: ChatGPT = technical lead/reviewer, Claude = implementation engineer, Noor = product owner (final calls,
  talks to teammates/organizers). Noor is a Code Crusaders **member, not captain**: "compare and decide together".

## Status at closeout (Wed Oct 21)
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
- **Proposal doc** "Twin-first inspection plan (proposal)" updated with the four corrections (D032–D034 + framing):
  https://claude.ai/code/artifact/7e742133-103c-483e-8409-8aca3b5e131e (private until Noor shares it).
- **Brev access (Noor):** NVIDIA account created; org **`UWM/MSOE-Team-25`**, **$500 shared credits** shown; Brev CLI
  **v0.6.337** on the Mac; `brev login`, `brev refresh`, `brev list` all OK (correct org; **no instances**).
  **Vang authorized creating a GPU instance** ("go ahead and create one to start testing").

### 2. Implemented but NOT verified
- **No Isaac Sim render exists.** Unknown whether RTX honours the generator's light (intensity, colour temperature,
  rotation) and material (UsdPreviewSurface) overrides, or whether the variation looks realistic.
- **Frozen gate-v2.0.2 has never run on a GPU → no gate result** (not PASS, not anything). Status: INCONCLUSIVE/not run.
- **No synthetic-trained ResNet-18 exists.** Synthetic-to-real transfer is untested. No transfer claim anywhere.
- Known generator limits (D035): tilted caps use the gate's approximate rim pivot (twin cap mesh has no interior);
  at 40° 29/240 crooked caps leave the runtime crop box (none at ≤35°); smoke labels are 58% empty positions (5,200 of
  9,000, mostly WAITING) → rebalance at training; materials vary per scene, not per cap; lifted caps (~0.3 px at 5 mm)
  are physically crooked but likely invisible, so smoke excludes them; leans limited to 0.95–4.47° by the twin's holes.
- When generated on a Brev instance from a `brev copy` (no `.git`), `run.json` shows git commit "unknown"; the
  generator's sha256 still identifies the code.

### 3. Pending team decisions (Code Crusaders) — architecture is a PROPOSAL (D031)
1. Which inspector leads: synthetic-only ResNet-18 (proposed) or the counterfactual (the scorer works either way).
2. Train baselines on twin renders, not Dataset 1 real images (unless organizers approve).
3. One sealed test set (Session B + runs 4–5 + organizer release); every arm freezes Wed Oct 28, 6 pm.
4. Owners: counterfactual (Vang + Trevor?), compute (Vang?), runtime/UI (Jamie or Matthew?), labels (Tony?),
   video/summary/business case (Zara?). Noor proposed for twin geometry, synthetic pipeline, ResNet-18, scorer.
5. Compute split (Brev seats, YAAD team + who drives the Spark).
6. Who sends the organizer question, and when (cutoff Tue Oct 27 noon for the real-example experiment).
7. Crooked-cap scope (D023): set by Session A. 8. Session B + supervised test date and attendees.
9. Integration: whether/where `feat/scene-generator` is pushed (stacked on PR #1's branch).

### 4. External dependencies
- **Organizer answer (D025/D033), not recorded as sent:** may we (a) train on newly collected CSI images, (b) calibrate
  thresholds on real images, (c) keep rule-baseline thresholds fitted on runs 1–3? Ask in `#dataset-1-vial-inspection`
  (quote Tanner's Oct 13 "up to you"). Also ask CSI which camera/resolution Session A/B use (640×480 cap_seal vs
  1920×1080; the latter needs a camera re-solve before the twin map is used).
- **CSI (Shamar Webster, `#data-and-testbed-requests`):** Session A Mon Oct 26 1 pm (Noor + Tony) and supervised test
  Oct 28–29 are **requests, unconfirmed**.
- **PR #1 (Code Crusaders):** open, unmerged; holds the shared position mapping, fill-state logic and evaluation tools.
  Needs teammate review. The Ignite remote also has `origin/feat/organizer-feedback-integration`.
- Team reply to the Oct 21 Discord proposal (send not confirmed here — ask Noor).
- Dataset 1 organizer release (1920×1080) not on the Mac yet (link in Slack `#dataset-1-vial-inspection`).

## NEXT ACTION (Thu Oct 22) — one priority: first GPU run
**Provision a Brev GPU, run the frozen gate unchanged, get the first verified renders.** Team discussion in parallel.
Blockers: none for compute (Vang authorized). Stop and ask Noor before creating anything that costs money.
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
Not tomorrow (after the gate): batch renderer (one Isaac session for many scenes; `render_keep.py` restarts Isaac per
scene, so 300 scenes that way is infeasible), then the Oct 25 smoke training. No ResNet training before the gate result.

## Milestones (all proposed; CSI items unconfirmed)
Oct 22 team architecture/ownership talk + compute setup · Oct 23 GPU access + first gate run (G1/G2) · Oct 25 synthetic
smoke-test checkpoint (G3: ~300 renders, 3 states, synthetic-only ResNet-18 on DEV runs 1–3; go if ≥90% DEV defect
observations caught at ≤5% false alarms; development signal only) · **Oct 26 1 pm CSI Session A (Noor + Tony)** ·
Oct 27 noon cutoff for organizer permission · **Oct 28 6 pm model/threshold freeze** (G5) · Oct 28–29 Session B +
supervised live run (G6) · Oct 30 final evaluation + error analysis · Oct 31 video, docs, business case ·
**Sun Nov 1 11:59 pm CT final submission** (~5-min video, one-page summary, repo, references) · Thu Nov 5 5–8 pm finals,
MSOE Diercks Hall. Gate definitions and fallbacks F1–F4: proposal doc, "Go/no-go gates".

## Project and proposed architecture (D002, D031)
**Twin-to-Line**, Rockwell × NVIDIA Physical AI Innovation Lab, Challenge 1 / Dataset 1 (Final Vial Inspection), Good
fixture G01–G30. Claim: the twin cuts the real defect data and line time needed to commission inspection.
- Offline (GPU): twin position map → Isaac renders with exact labels + randomization (`gen_scenes.py`) → synthetic-only
  ResNet-18 (thresholds from synthetic validation, D033) → freeze record.
- Live (laptop): real-to-real event detection → 30 crops (`positions.py`) → inspector (ResNet-18; rule baseline alongside)
  → fill state (`fill_state.py`, occupancy, D021) → operator map + trial log. No PLC connection (D019).
- Scoring: every arm writes the same predictions CSV, scored once on sealed real data (`eval_metrics.py`).
- Counterfactual: optional, scored separately on eligible events + coverage (D034).
- Real-example experiment: exploratory 1/2/4 per class, Session A only, permission-gated (D032); 5/10/20 kept as the
  objective for later. `dose_sets.py` still implements 5/10/20 (not updated; Noor has an unstaged edit there).

## Real-data boundary (D011, D025, D033)
Runs 1–3: development/reference only, no fitting. Runs 4–5: holdout, never for training, thresholds, prompts, recipe or
model choice. Organizer release (1920×1080): development + evaluation only. Session A: development + feasibility
(and training data only with written permission). Session B: sealed final test, opened after the freeze. Unit = placement
event or arrangement-position, never a frame. `rule_thresholds.json` was fitted on DEV draft labels (status part of the
organizer question). `labels/dev_labels.csv` = DRAFT labels.

## Organizer facts (Derek Riley Oct 14/16; guides)
Direction aligned, not exclusive · confirm training-data rules first (D025) · crooked cap = any cap not fully seated;
our refinement ≥~15–20° visible, rest = camera limit (D023) · supervised live run in Session B counts as the hardware demo
(D029) · no PLC/robot/placement-count data; no order-complete signal (D019, D021) · CSI numbering differs; G01–G30 is our
twin convention (D022) · NVIDIA vial labeler = manual review tool, 1920×1080 only (D027) · `damaged_vial` out of scope
for v1, still counted (D026) · organizer grid consistent with the twin map (supporting evidence only, D024) · strongest
no-teach evidence: real 640×480 empty fixture, 30/30 holes, ~1.68 px median, no per-position teaching.

## Team and contacts
- **Code Crusaders** (Challenge 1): Zara, Matthew, Trevor, Vang, Anthony "Tony" Harvey (Data Science), Jamie Gill (CS),
  Noor ("Jatt" on Discord). Their Oct 14 plan (Vang): Isaac synthetic data + AOI baseline, twin-expected-state compare,
  reasoning-model escalation, FLUX.2 composites, Brev + DGX Spark. Trevor's own warning: a whole-scene twin compare
  breaks after the first defect (per-position crops + occupancy answer it).
- Team Ignite (old): repo preserved intact (D028); Haru, Jordan, Muhammad placement unknown. Tom Hershberger's answers
  on "Leave Team Ignite" and Ignite repo access: last recorded Oct 19, outcome not recorded here.
- Contacts: CSI/data/testbed Shamar Webster (`#data-and-testbed-requests`) · dataset Brett Storoe, Derek Riley, Tanner
  Cellio (`#dataset-1-vial-inspection`) · compute Dan Schneider (`#compute-questions`) · workspace/GitHub Brett Storoe
  (`#hackathon-general`) · program Tom Hershberger.

## Compute and resources
- **Brev (use this first):** team org `UWM/MSOE-Team-25`, $500 shared, Noor logged in via CLI v0.6.337, Vang authorized
  an instance, **none created yet**. Stop instances whenever idle. No personal spending (D010); Noor's personal NVIDIA
  cloud account is not used.
- Dan Schneider's Oct 16 Brev org for Noor (as Ignite captain, $500): was on hold pending Tom; relation to
  `UWM/MSOE-Team-25` not confirmed — don't spend from two orgs without Noor saying so.
- **YAAD GPU Lab** (Code Crusaders, CSI): 8 DGX Sparks; CSI VPN (FortiClient SSL-VPN `vpn.csi.uwm.edu:443`, shared
  account `CodeCrusaders`, password only in the team email) → site sign-in with @uwm.edu + 6-digit code → own SSH key →
  captain creates the team and shares the 8-character code. Files deleted after the event. Guide
  https://www.yaadops.com/guide. Status (team created? captain?) unknown. **Spark is aarch64 and `usd-core` has no aarch64
  wheel** → `make_variants.py`/`gen_scenes.py` can't run there in a venv (use Isaac's bundled `pxr` or generate elsewhere).
- UWM GB10 (Shamar): no access; `GB10_PREFLIGHT.md` ready. build.nvidia.com usable. AI tool accounts per team: pending.

## Source of truth and paths
- Ignite repo: https://github.com/ALL-Applied-AI-Network/msoe-ai-club-rockwell-automation-nvidia-hackath-new-team-11-b020278d03
  · `main` @ `2a935de` (unchanged) · `feat/organizer-feedback-integration` @ `2189e3a` (also on origin; PR #1's work) ·
  `feat/scene-generator` @ `5c69c9f` + a local docs commit (closeout) — **local only**.
- Local clone `~/code/ignite`, project dir `twin_to_line/`, venv `~/code/ignite/.venv` (Python 3.11, usd-core 26.08,
  NumPy 2.4.6, OpenCV). Repo-root `README.md` is the organizers' — leave it.
- Data (not in git): twin `~/Downloads/csi_digital_twin/csi_digital_twin_v1/` (station sha256 `293d74ba…`, camera JSON
  `0376842d…`); real `~/Downloads/csi-vial-fill-dataset/cap_seal/`; labeler `~/Downloads/vial-labeler-participants-20261014.zip`.
- Docs: proposal (above); old Ignite decision doc https://claude.ai/code/artifact/34a0c4d3-4d98-4a90-81d6-d6eee43c37fc
  (section 13 superseded by Project `claude/team-plan-final.md`, the submitted Ignite plan); `ORGANIZER_UPDATE_2026-10-16.md`
  (§5 has the organizer questions); `GATE_v2.0.2.md` (frozen rule + runbook §11).

## Known-working commands (in `twin_to_line/`, Mac)
```bash
git status -sb                                   # expect: ## feat/scene-generator  +  " M twin_to_line/dose_sets.py"
shasum -a 256 -c MANIFEST.sha256                 # expect: 8 lines ending OK (gate-v2.0.2)
shasum -a 256 -c PROTOTYPE_SNAPSHOT.sha256       # expect: 4 x OK
IGNITE_TWIN=~/Downloads/csi_digital_twin/csi_digital_twin_v1 ../.venv/bin/python -m pytest tests -q   # expect: 91 passed
../.venv/bin/python gen_scenes.py ~/Downloads/csi_digital_twin/csi_digital_twin_v1 --selftest            # expect: selftest passed
../.venv/bin/python eval_metrics.py --selftest
../.venv/bin/python inspect_frame.py --run 1 --events [--track]      # DEV runs only
```

## Known risks
- Isaac/launchable version may differ from 6.0 (recorded, not a reason to change the kit); Isaac in Docker → run inside
  it with `ISAAC_PY=…`; Drive download on the instance may fail → `brev copy` the twin zip.
- `render_keep.py` restarts Isaac per scene → batch renderer needed before 300+ renders (next coding task after the gate).
- UsdPreviewSurface material/light overrides and liquid may render differently in RTX (check renders).
- Crooked caps may be physically unresolvable from this camera at small angles (D005/D006/D023): Session A decides scope.
- Color rules may match any model on missing cap / no vial; the honest competitor stays in every report.
- Real-example experiment may be blocked by the organizer rule (then F4: zero-real results only).
- Team may keep the counterfactual as primary; the scorer, gates and generator are useful either way.
