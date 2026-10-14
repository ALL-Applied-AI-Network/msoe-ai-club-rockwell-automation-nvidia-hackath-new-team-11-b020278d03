# Team Ignite — Handoff (read first)
Updated: 2026-10-14 11:10 CT · New session: work from `~/code/ignite`, run `git status` first, read this + `DECISIONS.md`, continue from **NEXT ACTION**, do not reopen settled decisions without new evidence. Replace stale facts here; no diary.

## Project
**Twin-to-Line** — Rockwell × NVIDIA Physical AI Innovation Lab, Dataset 1 (Final Vial Inspection). Commission the Good-fixture (G01–G30) overhead inspector from the CSI digital twin, using synthetic data to eliminate or sharply reduce the real defect data and line time needed at a changeover.
- Primary experiment: synthetic-only training → real evaluation (zero real images = best case, not a requirement; D003).
- Fallback: synthetic + nested predetermined real sets of 5 / 10 / 20 examples from runs 1–3 → same holdout → report performance vs. real examples (D014).
- Not "AI cap detection" (D002).
Decision doc (research, matrix, twin results in 2b, paste-ready team plan in section 13): https://claude.ai/code/artifact/34a0c4d3-4d98-4a90-81d6-d6eee43c37fc

## Architecture
Commissioning (GPU): twin files → position map at cap-top height (`capsealcam.py`) → golden image per position → Replicator defect renders (USD overrides) → small model (TAO Visual ChangeNet; ResNet-18 fallback).
Runtime (laptop): cap_seal frame → arm-clear check → 30 crops → score → fill-sequence logic → operator map (pass / defect / missed / waiting) + simulated stop flag. Cosmos escalation optional (D008). No PLC connection (MAIC rule).

## Confirmed facts
- Scope: Dataset 1, Good fixture G01–G30. Twin S fixture has no hole map (5 scrap vials lying down) → S out of scope.
- Twin: `G01–G30_tube` / `_cap` are separate editable prims; defect states authored as small USD override layers; numbering G01–G05 = rightmost column top→bottom = fill order. Station in inches under a 0.0254 root scale.
- Tanner (Oct 13, organizers): teams may use real, synthetic, new CSI data or any mix; vial/cap dimensions are preserved in the USD geometry/units/transforms → twin USD is the dimensional source of truth (D015); auto-labeling tool promised, not yet delivered.
- Camera: CapSealCam pipeline reproduced (`capsealcam.py` = `tools/apply_lens.py` to 0.001 px). Registration on real frames: 4.4 px median raw; after one global (−0.3, −3.6) px offset, seated caps 3.2 px median / 5.3 px p90. Good enough to continue, not perfect.
- Crooked caps (from twin geometry): ~2 px at 10°, ~3 px at 15°, ~4–4.5 px at 20°, ~7 px at 30°; level 5 mm lift ≈ 0.3 px; a 2° whole-vial lean moves the cap ~2.3 px. → Target tilts ≈15–20°+, report smaller tilt/lift as a likely camera-information limit, confirm with known-angle CSI examples (D005, D006, D016).
- Sequence: empty inside the placed prefix = missed; after it = waiting. A real placement count / order-complete signal is still wanted.
- Liquid: tray twin has none (vial plastic opacity 0). Plan: simple colored cylinder + material (D013); no fluid sim. Real uncapped vial from above reads dark grey-green.
- Real camera noise σ ≈ 2.7 gray levels; frame-to-frame p99 |Δ| = 12.

## Real-data boundary (D011, `real_splits.json`)
- **Runs 1–3**: development/reference — visual inspection, sim-to-real comparison, sanity checks, auto-labeling review; adaptation ONLY if D014 triggers (nested 5 ⊂ 10 ⊂ 20, chosen in advance).
- **Runs 4–5**: model holdout — never for classifier training, thresholds, prompt examples, augmentation decisions, choosing the synthetic recipe, or picking a model because it does better there. 8 of their frames were used for the Oct 13 geometry/noise check → valid model holdout, not a pristine end-to-end source.
- **CSI deliberate-defect collection** (hand-staged, D016): preferred final end-to-end evaluation; any adaptation subset chosen in advance and kept separate.
- Unit = placement event, not frame.

## Real-image prototype — DONE, approved as the current baseline (GPT review, Oct 14)
DEV runs 1–3 only, laptop: real frame → twin G01–G30 map (+ DEV offset) → 30 crops → yellow-fraction rule → fill-sequence logic → PASS / DEFECT / MISSED / WAITING / UNSURE. Empty fixture: 30/30 holes, 1.68 px median. 53 tests pass. `labels/dev_labels.csv` = DRAFT labels (not certified); artifact versions in `PROTOTYPE_SNAPSHOT.sha256`; commands in README "Real-image prototype". The rule baseline is finished (do not tune it); its pale-cap, crop-overlap, uncapped-vs-empty and displaced-cap limits are the case for a learned model. DEV has only 7 independent cap-defect units (5 displaced, 2 uncapped) → the dose curve needs the hand-staged CSI collection (`staging/`, draft kit).

## Current experiment — Isaac Sim appearance gate (kit **gate-v2.0.2**, frozen, NOT run)
Question: is synthetic appearance close enough to real cap_seal imagery for synthetic-first training to be credible? Outcome: INCONCLUSIVE / FAIL / PASS WITH WORK / PASS, decided by the rule in `GATE_v2.0.2.md` (frozen Oct 14, before any render).
Renders (CapSealCam 768×576 pinhole → real lens → 640×480, PathTracing, 64 subframes): `baseline` (as shipped) · `t00` (G01 pass, G02 missing cap, G03 0°, G04 missing vial = missed placement) · `t10` / `t20` / `t30` (only G03 tilt changes) · `liquid` (t20 + liquid cylinders).
Records: GPU, Isaac version, settings, per-render timings, cost if `RATE_PER_HR` set, undistorted + final images, crops, labels, scene layers, kit checksums. Then `compare_gate.py` (geometry, appearance ΔE per region, noise, crooked-cap visibility vs real seated-cap variation; DEV runs only).
**Status Oct 14: no Isaac render exists; gate result INCONCLUSIVE (no compute).** Team Brev and UWM DGX Spark access are both unavailable; this Mac (Apple M2) cannot run Isaac Sim. The v2.0 kit could not have rendered (`render_keep.py` `NameError`, fixed in v2.0.1). Next execution step: one frozen gate-v2.0.2 run when team compute exists. No personal spending (D010).

## Team
- Noor (captain): plan, geometry, evaluation, sequence logic, demo; runs the gate if needed.
- Muhammad Aadil (remote, India): Isaac Sim / Replicator — no reply to emails (Sat Oct 10, Mon Oct 12) or Slack; yes/no + weekly hours due **Wed Oct 14 6 pm CT**.
- Jordan Henderson (EE, UWM): CSI line + data collection — active again Oct 14; Noor sent him initial setup steps; CSI visit tentatively next week (date not set).
- Harshitha Devarakonda ("Haru" internally; use full name in the plan): joined Oct 14, ML / computer vision; no Claude plan line for her.
- If Muhammad does not confirm by 6 pm: Noor takes Isaac Sim / Replicator, scene setup, defect authoring, synthetic rendering, Brev; Harshitha takes TAO ChangeNet / ResNet-18 fallback, training experiments, model-side evaluation; Jordan keeps CSI / local testing / logistics. If he confirms: planned ownership stays. Architecture unchanged either way.
- Angelica withdrew (not listed in the plan); Jared unresponsive. Oct 14: asked Tom whether to list unconfirmed members and whether a merge is still possible.

## Resources / access
- Requested in plan: Brev $160 ≈ 25 GPU-hours, RTX PRO 6000 preferred, AWS L40S fallback, Start/Stop environments, log GPU/version/runtime/storage/credits. build.nvidia.com Cosmos Reason (free). UWM DGX Spark requested separately via UWM. Claude: $100 plan (Noor); $20 plan (Muhammad) only if he confirms.
- Brev org link: not received. Timing after submission is inferred, not confirmed. No link by ~Fri Oct 16 → Dan Schneider in #compute-questions.
- Oct 14 evening: no team Brev access and no UWM DGX Spark access → the Isaac gate cannot run yet.
- Noor has a personal NVIDIA cloud account (team-ignite-uwm) — no card, do not launch from it.

## Deadlines
Team plan **Wed Oct 14 11:59 pm CT** · Final submission Sun Nov 1 11:59 pm CT · Finals Thu Nov 5, MSOE Diercks Hall, 5–8 pm.

## Source of truth
- Repo: https://github.com/ALL-Applied-AI-Network/msoe-ai-club-rockwell-automation-nvidia-hackath-new-team-11-b020278d03 · branch `main` · gate kit v2.0 committed in `c673212`; real-image prototype + gate-v2.0.2 committed Oct 14 (`git log`).
- Local clone: `~/code/ignite` · project directory: `twin_to_line/` (this file, `DECISIONS.md`, `real_splits.json`, `README.md`, gate scripts `run_gate.sh` `make_variants.py` `render_keep.py` `cut_crops.py` `compare_gate.py` `capsealcam.py`, gate rule `GATE_v2.0.2.md` + `gate_evidence.py`, `eval_metrics.py`, real-image prototype (README section), `staging/`, earlier tools). Repo-root `README.md` is the organizers' — leave it.
- `~/Downloads/twin_to_line_kit/` is a backup only (also holds `_old_v1/` and `twin_findings.jpg`, deliberately not committed). All future work, including Claude Code sessions, happens in the repo.

## Data paths (Noor's Mac, not in git)
- Twin: `~/Downloads/csi_digital_twin/csi_digital_twin_v1/` · Real data: `~/Downloads/csi-vial-fill-dataset/cap_seal/`
- Frozen gate state = `MANIFEST.sha256` + `KIT_VERSION` (gate-v2.0.2). `.gitignore` keeps data, twins, archives, renders, results and weights out of git.

## Known-working commands
- In `twin_to_line/`: `shasum -a 256 -c MANIFEST.sha256` (Mac) or `sha256sum -c MANIFEST.sha256` (Linux) → 8 × OK (gate-v2.0.2)
- `../.venv/bin/python -m pytest tests -q` → 53 passed · `shasum -a 256 -c PROTOTYPE_SNAPSHOT.sha256` → 4 × OK
- `python3 eval_metrics.py --selftest` → "selftest passed…"
- `python make_variants.py <twin> <out>` (needs usd-core) → 6 scenes, labels self-checked
- On Brev: `RATE_PER_HR=<$/hr> bash ~/twin_to_line/run_gate.sh` → `~/ignite_gate/results.tar.gz` (full runbook in `GATE_v2.0.2.md`; renderer verified locally up to `import isaacsim`)
- After: `python compare_gate.py <results> <real_frames_dir> <twin> <out>` → `gate_report.json` + panels (tested on stand-in renders); then `python gate_evidence.py <results> <out>` (supplementary panels A–D)

## Known failures / risks
- Isaac Sim never run; `render_keep.py` untested on GPU (its v2.0 `NameError` is fixed in v2.0.1). Twin README: tested with Isaac Sim 6.0; launchable version unknown. If Isaac runs in Docker on the instance, run inside it (`ISAAC_PY=…`).
- Drive download on the instance may fail → `brev copy` the twin zip (script prints the command).
- `usd-core` has no Linux-aarch64 wheel (fine on Mac native, x86 Linux, Brev).
- UsdPreviewSurface liquid may render as plain alpha, not refraction — the gate will show.
- Real test set is small; recall will have wide uncertainty until the CSI collection exists.
- Later (not the gate): TAO needs NGC + Hugging Face accounts.

## Open questions (in the team plan)
Crooked-cap tilt/condition and acceptable vial lean/placement tolerance · same G01–G30 numbering? · placement count / order-complete logged for existing runs or available during our test · can CSI produce the hand-staged collection, and when; held-out real set? · when do Brev org links and UWM Spark access go out · team merge.

## Today, Oct 14 (admin only)
Already in section 13: Harshitha added to members; merge question notes she joined Oct 14.
1. Post the hand-staged data request in #data-and-testbed-requests tagging Shamar (text = section 13, data item 1).
2. Tom's reply (if any) → members-line wording for unconfirmed members.
3. 6 pm: Muhammad's reply → members line + keep/remove the bracketed $20 Claude line (remove the bracket text either way).
4. Paste section 13 into the team-plan form; submit by ~9 pm.

## When Brev arrives
Join org link → Isaac Sim launchable, RTX PRO 6000 (else AWS L40S with Start/Stop) → note $/hr → follow the runbook in `GATE_v2.0.2.md` (copies only the kit tarball) → copy back `results.tar.gz` → **stop the instance** → `compare_gate.py` + `gate_evidence.py` → score with `GATE_v2.0.2.md` section 5 (INCONCLUSIVE / FAIL / PASS WITH WORK / PASS) → record in the doc and here. One run only; no dataset, no training.

## NEXT ACTION
Submit the team plan (decision doc section 13) by Wed Oct 14 11:59 pm CT, after applying Muhammad's 6 pm reply to the members and coding-agent lines.
Engineering (blocked on team NVIDIA compute): run the frozen gate-v2.0.2 once when team Brev or DGX access exists (see "When Brev arrives"). No other engineering until then.
