# Twin-to-Line kit v2 — sim-to-real gate (frozen: gate-v2.0, see MANIFEST.sha256)

Start here: `HACKATHON_HANDOFF.md`, then `DECISIONS.md`.

Goal: six tiny Isaac Sim renders through CapSealCam, to measure the sim-to-real gap before any dataset or training.

## What gets rendered (all at 768×576 pinhole → real lens → 640×480)
| Variant | Scene |
| --- | --- |
| baseline | tray station as shipped: all 30 G vials capped (geometry + appearance check vs a full real frame) |
| t00 | G01 pass · G02 missing cap · G03 cap 0° · G04 no vial (missed placement) · G05–G30 empty |
| t10 / t20 / t30 | same, G03 cap tilted 10° / 20° / 30° about its rim (only G03 differs) |
| liquid | t20 + liquid cylinders: G01 blue, G02 orange (uncapped), G03 blue |

Path tracing, 64 subframes per frame, 2 orchestrator steps (the twin's own render settings, `--subframes` raised from 32).

## Run on the Brev Isaac Sim launchable (about 20–30 min of instance time)
```bash
brev copy ~/code/ignite/twin_to_line <instance-name>:/home/ubuntu   # from your Mac
brev shell <instance-name>
RATE_PER_HR=<$/hr shown in Brev> bash ~/twin_to_line/run_gate.sh   # downloads the twin, finds Isaac Sim, logs cost
#   if it cannot find Isaac Sim:  ISAAC_PY=/path/to/python.sh bash ~/twin_to_line/run_gate.sh
exit
brev copy <instance-name>:/home/ubuntu/ignite_gate/results.tar.gz ~/Downloads/   # then STOP the instance
```
Expected at the end of the log: six `exit=0` lines and `DONE -> .../results.tar.gz`.

## Files
- `run_gate.sh` — the whole run: twin download (gdown), a venv with usd-core for authoring, Isaac Sim detection,
  6 renders with timing, crops, tarball, `run_log.txt` (GPU, Isaac version, per-render wall time).
- `make_variants.py` — writes each variant as a tiny override layer over the untouched station file, plus
  `labels.json` (state, fill-sequence status, drawn box, seated-position anchor box for all 30 G positions).
  Asserts that labels derived from the composed USD equal the authored states.
- `render_keep.py` — the twin's `tools/render_example.py` with 3 marked changes: `--twin` path, keeps the
  undistorted `*_pinhole768.png`, writes `*.json` with render settings, Isaac version, GPU and timings.
- `cut_crops.py` — 4 labeled crops per render (empty holes use the anchor box) + overlay + `crops.csv`.
- `compare_gate.py` — runs on the results afterwards: geometry, appearance (Lab ΔE per region), noise,
  crooked-cap visibility against real seated-cap variation, comparison panels.
- `capsealcam.py` — CapSealCam projection (pinhole + k1), matches `apply_lens.py` to 0.001 px.
- `eval_metrics.py` — metrics for later (per-class recall, FN, FP rate, FAR at full recall, trailing-empty alarms,
  sequence accuracy); `--selftest` checks it on mock predictions. No model, no training.
- `real_splits.json` — which real runs are DEV vs HELD-OUT.
- Earlier tools: `registration.py`, `tilt_sensitivity.py`, `twin_positions.py`, `overlay.py`.

Twin note: the twin README says it was tested with Isaac Sim 6.0; `run_log.txt` records the version actually used.
