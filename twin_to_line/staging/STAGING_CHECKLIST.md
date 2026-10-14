# CSI hand-staged collection — staging kit (DRAFT, 2026-10-14)

Preparation only. Collection counts and the Session A / Session B design come from the agreed plan; this kit does
not set or change them. Unit = placement event (D011). Labels written here are the reference labels for scoring.

## Files
- `staging_sessions_template.csv` — one row per session (camera/fixture check).
- `staging_log_template.csv` — one row per G position per placement event.

## 1. Start of every session: empty-fixture hole registration check (record, never tune)
1. Fixed camera, G fixture empty, arm clear. Save one frame; note its file name.
2. From `twin_to_line/`:
   ```bash
   ../.venv/bin/python -c "
   import sys, numpy as np, positions as P, register_dev as RD, real_data as R
   img = R.Index().load(sys.argv[1]); r = RD.hole_check(img, P.PositionMap()); d = [float(np.hypot(*v)) for v in r.values()]
   print(f'{len(r)}/30 holes matched, median {np.median(d):.2f} px, p90 {np.percentile(d, 90):.2f} px')" <empty_frame.jpg>
   ```
3. Record the result in `staging_sessions_template.csv`. DEV reference (run 3, Sept 23 pose): 30/30, median 1.68 px,
   p90 2.53 px. If it is clearly worse, flag it to Noor before staging (the camera or fixture may have moved). Do not
   change the position map, offset or rule thresholds from session data.

## 2. Before staging each unit
- Write its `designation` (`adaptation` or `final_test`) **before** staging it, never after seeing any result.
- `final_test` frames go to their own folder and are never opened for development (D011).

## 3. Per placement event (`staging_log_template.csv`)
| Column | Meaning |
| --- | --- |
| `session` | session id (matches `staging_sessions_template.csv`) |
| `event_id` | placement event number within the session |
| `frame_id` | camera file name of the first arm-clear frame after the placement |
| `position` | G01–G30; record all 30 positions per event, as `labels/dev_labels.csv` does |
| `placement_count_K` | placements attempted so far, so `fill_state.py` can tell missed from waiting |
| `defect_class` | `pass`, `missing_cap`, `crooked_cap` or `no_vial` (visual class only; missed/waiting comes from K) |
| `known_tilt_deg` | measured cap tilt for `crooked_cap` when known; blank otherwise (displaced caps: describe in notes) |
| `staging_start`, `staging_end` | local ISO time the staged state was set up and released |
| `designation` | `adaptation` or `final_test`, fixed before staging |
| `notes` | displaced vs tilted, lighting/glare, neighbour interference, anything unusual |

## 4. After the session
- Check: no blank `designation`; `known_tilt_deg` only on `crooked_cap`; `defect_class` in the four classes; 30 rows per event.
- Keep adaptation and final-test frames in separate folders, and record which is which in the session notes.
