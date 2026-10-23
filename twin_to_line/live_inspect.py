"""Live runtime: camera frames -> event gating (arm clear, scene stable) -> 30 position crops -> inspector ->
fill-sequence state (LIVE_FILL, D021) -> predictions CSV + trial log + operator overlay. Reads image files only (R10).

    python live_inspect.py --source replay:DIR [--labels labels/dev_labels.csv] [--out DIR]
    python live_inspect.py --source folder:DIR [--poll 0.25] [--idle-exit S]
    python live_inspect.py --export-replay 1 --out results/live/replay_run1 [--from video|stills] [--step 1.0]

Sources (one code path after decoding: Session.process_frame):
  replay:DIR  every image in DIR in frame-time order, as fast as it runs
  folder:DIR  watches DIR; a new image is read once its size is unchanged for one poll and its end marker
              (JPEG FFD9 / PNG IEND) is present, so a half-written file is never read
Frame time: from a video frame id (cap_seal_video_1.mp4@t0612.0.png) or a CSI still name
(cap_seal_20260922_192843_993721.jpg); otherwise the file's modification time.
Gating (--gate):
  events (default)  events.py's rule, online: arm-clear frames with no position changing by >= CHANGE_T form a
                    segment; one that lasts >= STABLE_S and differs from the previous event is an event, and its
                    FIRST frame is scored (the same frames as events.segment_events, so frame ids join DEV labels)
  each              every arm-clear frame is its own event (staged stills: one image per setup)
Frames with the arm over the fixture are never scored. Fill state from occupancy (LIVE_FILL default), or
fill_state.SequenceTracker with --track (persist 1: each event is already a stable segment).
Outputs in --out (default results/live/<UTC time>):
  predictions.csv     one row per position per event (inspect_frame.py schema; eval_metrics.py reads it)
  trial_log.csv       one row per input frame, every attempt: status, event, per-position state + score, expected
                      state (--labels), latency, notes; an empty 'intervention' column for the operator
  overlay_latest.png  operator view of the latest event (30 coloured boxes + legend); overlays/eNN_<frame>.png
  session.json        configuration, code / thresholds / map hashes, counts
Data rule (D011): a frame that is in the dataset index but not in DEV runs 1-3 is refused, so runs 4-5 are never
processed; images from outside the dataset (staged / live captures) are accepted.
The rule baseline's rule_thresholds.json was fitted on DEV draft labels: a plumbing placeholder, not a scored arm.
"""
import argparse, csv, hashlib, json, os, re, shutil, subprocess, time
from collections import Counter
from datetime import datetime, timezone
import cv2, numpy as np
import positions as P
import real_data as R
import events as E
from eval_metrics import gt_final
from fill_state import SequenceTracker, LIVE_FILL, MODES
from inspect_frame import inspect, annotate, prediction_rows, safe
from rules import RuleInspector, THRESHOLDS

IMAGE_EXT = (".png", ".jpg", ".jpeg")
STILL_RE = re.compile(r"(\d{8})_(\d{6})_(\d{6})")
FLAGGED = ("DEFECT", "MISSED", "UNSURE")
RUNTIME_FILES = ("live_inspect.py", "inspect_frame.py", "positions.py", "fill_state.py", "rules.py", "events.py",
                 "real_data.py", "position_map_G.json", "registration_dev.json", "rule_thresholds.json")
PRED_FIELDS = ["run", "event", "frame", "position", "predicted_state", "defect_score", "pred_sequence", "final_state",
               "K", "K_source", "cap_frac", "cap_offset", "reason"]
IDS = [f"G{i:02d}" for i in range(1, 31)]
TRIAL_FIELDS = (["time_utc", "session", "git", "inspector", "model_sha256", "input_file", "frame_t", "status", "arm_px",
                 "event", "event_frame", "event_delay_s", "K", "n_flagged", "n_differ_from_expected", "latency_ms"]
                + [f"pred_{p}" for p in IDS] + [f"exp_{p}" for p in IDS] + ["note", "intervention"])


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def code_version():
    """Short git sha, '+modified' when a runtime source file differs from HEAD (others, e.g. dose_sets.py, ignored)."""
    try:
        g = lambda *a: subprocess.run(["git", "-C", P.HERE, *a], capture_output=True, text=True, check=True).stdout.strip()
        return g("rev-parse", "--short", "HEAD") + ("+modified" if g("status", "--porcelain", "--", *RUNTIME_FILES) else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def frame_id(path):
    """Frame id as the labels and inspect_frame.py use it: a cached video frame 'cap_seal_video_1.mp4@t0612.0.png'
    is the video frame id without '.png'; any other image keeps its file name."""
    name = os.path.basename(path)
    return name[:-4] if R.VIDEO_RE.match(name) and name.endswith(".png") else name


def frame_time(path):
    name = os.path.basename(path)
    m = R.VIDEO_RE.match(name)
    if m:
        return float(m.group(2))
    m = STILL_RE.search(name)
    if m:
        return datetime.strptime("".join(m.groups()), "%Y%m%d%H%M%S%f").replace(tzinfo=timezone.utc).timestamp()
    return os.path.getmtime(path)


def dataset_index():
    try:
        return R.Index()
    except OSError:
        return None                       # no dataset on this machine: nothing to protect


def refusal(ix, path):
    """Why a frame must not be processed (dataset frame outside DEV runs 1-3), or None."""
    if ix is None:
        return None
    try:
        run = ix.run_of_source(path)
        if run is not None:
            R.check_allowed(run, role_map=ix.role_map)
    except R.ProtectedDataError as e:
        return str(e)
    return None


def is_image(name):
    return name.lower().endswith(IMAGE_EXT) and not name.startswith(".")


def complete(path):
    """The file ends with its format's end marker (a half-written JPEG still decodes, as a partly grey image)."""
    try:
        with open(path, "rb") as f:
            f.seek(-12, os.SEEK_END); tail = f.read()
    except OSError:
        return False
    if path.lower().endswith(".png"):
        return tail.endswith(b"IEND\xaeB`\x82")
    return tail.rstrip(b"\x00").endswith(b"\xff\xd9")


def replay(folder, ix=None):
    """(path, image) for every image in folder, in frame-time order. The folder is checked when replay() is
    called: one protected frame refuses all of it before anything is read."""
    paths = [os.path.join(folder, n) for n in os.listdir(folder) if is_image(n)]
    bad = [r for r in (refusal(ix, p) for p in paths) if r]
    if bad:
        raise R.ProtectedDataError(f"{len(bad)} protected frame(s) in {folder}, e.g. {bad[0]}")
    paths.sort(key=lambda p: (frame_time(p), os.path.basename(p)))
    return ((p, cv2.imread(p)) for p in paths)


def watch(folder, poll=0.25, idle_exit=None, give_up_s=3.0):
    """(path, image) for each new image in folder, in arrival order, once its size is unchanged for one poll and
    it is complete; a file that stays incomplete for give_up_s is passed on anyway (logged as unreadable or as
    what it decodes to). Runs until Ctrl-C, or until no new file has arrived for idle_exit seconds."""
    seen, sizes, last = set(), {}, time.monotonic()
    while True:
        for n in sorted(os.listdir(folder)):
            p = os.path.join(folder, n)
            if n in seen or not is_image(n):
                continue
            try:
                s = os.path.getsize(p)
            except OSError:
                continue
            now = time.monotonic()
            if s > 0 and n in sizes and sizes[n][0] == s and (complete(p) or now - sizes[n][1] >= give_up_s):
                seen.add(n); del sizes[n]; last = now
                yield p, cv2.imread(p)
            elif n not in sizes or sizes[n][0] != s:
                sizes[n] = (s, now)
        if idle_exit is not None and time.monotonic() - last > idle_exit:
            return
        time.sleep(poll)


class EventGate:
    """events.segment_events, online. update() once per frame, in time order. Returns (status, frame, changed):
    'arm' (arm over the fixture), 'settling' (segment not yet stable for stable_s), 'unchanged' (segment already
    decided, or the same as the last event) or 'event' with frame = (name, t, image) of the segment's first frame."""

    def __init__(self, boxes, ids, change_t=E.CHANGE_T, stable_s=E.STABLE_S, each=False):
        self.boxes, self.ids, self.change_t, self.stable_s, self.each = boxes, ids, change_t, stable_s, each
        self.first = self.prev = self.last_event = None
        self.decided = False

    def _changed(self, img):
        if self.last_event is None:
            return list(self.ids)
        return [p for p, x in zip(self.ids, E.box_change(img, self.last_event, self.boxes)) if x >= self.change_t]

    def update(self, name, t, img, arm):
        if arm:
            self.first = self.prev = None
            return "arm", None, None
        if self.each:
            changed = self._changed(img); self.last_event = img
            return "event", (name, t, img), changed
        if self.first is not None and E.box_change(img, self.prev[2], self.boxes).max() >= self.change_t:
            self.first = None
        if self.first is None:
            self.first, self.decided = (name, t, img), False
        self.prev = (name, t, img)
        if self.decided:
            return "unchanged", None, None
        if t - self.first[1] < self.stable_s:
            return "settling", None, None
        self.decided = True
        changed = self._changed(self.first[2])
        if not changed:
            return "unchanged", None, None
        self.last_event = self.first[2]
        return "event", self.first, changed


def expected_states(path):
    """{(frame, position): expected final state} from a labels CSV (eval_metrics ground-truth columns)."""
    with open(path, newline="") as f:
        return {(r["frame"], r["position"]): gt_final(r) for r in csv.DictReader(f) if r.get("usable", "1") != "0"}


class CsvLog:
    """CSV written and flushed row by row, so Ctrl-C or a crash never loses a logged row."""

    def __init__(self, path, fields):
        self.f = open(path, "w", newline="")
        self.w = csv.DictWriter(self.f, fieldnames=fields, extrasaction="ignore"); self.w.writeheader(); self.f.flush()

    def write(self, rows):
        self.w.writerows(rows); self.f.flush()

    def close(self):
        self.f.close()


class Session:
    def __init__(self, out, source="", run_id=None, gate="events", mode=LIVE_FILL, track=False, labels=None,
                 note="", ix="auto", pmap=None, inspector=None, quiet=False):
        self.out, self.run_id, self.mode, self.quiet = out, run_id, mode, quiet
        self.pm = pmap or P.PositionMap(); self.plate = self.pm.plate_mask()
        self.insp = inspector or RuleInspector()
        self.gate = EventGate(self.pm.anchor_boxes, self.pm.ids, each=gate == "each")
        self.tracker = SequenceTracker(1, mode) if track else None
        self.ix = dataset_index() if ix == "auto" else ix
        self.expected = expected_states(labels) if labels else {}
        self.name = os.path.basename(os.path.normpath(out))
        self.git, self.model_sha = code_version(), sha256(THRESHOLDS)
        self.events, self.counts, self.latency, self.stop_reason = 0, Counter(), [], "end of source"
        os.makedirs(os.path.join(out, "overlays"), exist_ok=True)
        self.preds = CsvLog(os.path.join(out, "predictions.csv"), PRED_FIELDS)
        self.trial = CsvLog(os.path.join(out, "trial_log.csv"), TRIAL_FIELDS)
        self.info = {"session": self.name, "started_utc": self.now(), "source": source, "gate": gate, "mode": mode,
                     "track": track, "run_id": run_id, "labels": labels, "note": note, "git": self.git,
                     "inspector": {"name": self.insp.name, "thresholds": os.path.relpath(THRESHOLDS, P.HERE),
                                   "sha256": self.model_sha, "status": "fitted on DEV draft labels: plumbing placeholder, "
                                                                       "not a scored arm"},
                     "position_map": {"file": os.path.relpath(P.MAP_PATH, P.HERE), "sha256": sha256(P.MAP_PATH),
                                      "image_size": list(self.pm.size), "offset_px": list(self.pm.offset),
                                      "offset_source": self.pm.offset_source},
                     "event_rule": {"change_t": E.CHANGE_T, "stable_s": E.STABLE_S, "arm_min_area": E.ARM_MIN_AREA},
                     "code_sha256": {f: sha256(os.path.join(P.HERE, f)) for f in RUNTIME_FILES}}
        self.write_info()

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def write_info(self, **extra):
        self.info.update(extra)
        json.dump(self.info, open(os.path.join(self.out, "session.json"), "w"), indent=1)

    def run_of(self, name):
        if self.run_id:
            return self.run_id
        try:
            return (self.ix.run_of_source(name) if self.ix else None) or "live"
        except R.ProtectedDataError:
            return "live"

    def process_frame(self, path, img, t=None):
        """One input frame (any source). Logs exactly one trial-log row and returns it."""
        t0 = time.perf_counter(); name = frame_id(path)
        row = {"time_utc": self.now(), "session": self.name, "git": self.git, "inspector": self.insp.name,
               "model_sha256": self.model_sha, "input_file": os.path.basename(path)}
        try:
            why = refusal(self.ix, path)
            if why:
                row.update(status="refused", note=why)
            elif img is None:
                row.update(status="unreadable", note="could not decode the image")
            elif img.shape[1::-1] != tuple(self.pm.size):
                row.update(status="wrong_size", note=f"{img.shape[1]}x{img.shape[0]}, expected {self.pm.size[0]}x{self.pm.size[1]}")
            else:
                t = frame_time(path) if t is None else t
                arm = E.arm_pixels(img, self.pm, self.plate)
                status, ev, changed = self.gate.update(name, t, img, arm > 0)
                row.update(frame_t=round(t, 3), status=status, arm_px=arm)
                if status == "event":
                    row.update(self.score(ev, changed, t))
        except Exception as e:                                  # never let one bad frame stop the session
            row.update(status="error", note=f"{type(e).__name__}: {e}")
        row["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        self.counts[row["status"]] += 1; self.latency.append(row["latency_ms"])
        self.trial.write([row])
        return row

    def score(self, ev, changed, t_now):
        name, t, img = ev
        self.events += 1
        res = inspect(img, name, self.pm, self.insp, plate=self.plate, mode=self.mode, tracker=self.tracker)
        self.preds.write(prediction_rows(self.run_of(name), self.events, res))
        view = annotate(img, res, self.pm)
        cv2.imwrite(os.path.join(self.out, "overlays", f"e{self.events:02d}_{safe(name)}.png"), view)
        tmp = os.path.join(self.out, ".overlay_latest.png"); cv2.imwrite(tmp, view)
        os.replace(tmp, os.path.join(self.out, "overlay_latest.png"))   # a viewer never sees half a file
        pos = res["positions"]
        row = {"status": "scored", "event": self.events, "event_frame": name, "event_delay_s": round(t_now - t, 1),
               "K": res["K"], "n_flagged": sum(p["final_state"] in FLAGGED for p in pos),
               "note": "changed: " + (" ".join(changed) if len(changed) < 30 else "ALL")}
        for p in pos:
            row[f"pred_{p['position']}"] = f"{p['final_state']} {p['defect_score']:.3f}"
            exp = self.expected.get((name, p["position"]), "")
            row[f"exp_{p['position']}"] = exp
        if any(self.expected.get((name, p["position"])) for p in pos):
            row["n_differ_from_expected"] = sum(self.expected.get((name, p["position"])) not in (None, p["final_state"]) for p in pos)
        if not self.quiet:
            c = Counter(p["final_state"] for p in pos)
            print(f"event {self.events:2d} {name[-34:]:>34s} K={res['K']:2d} delay {row['event_delay_s']:5.1f}s  "
                  + " ".join(f"{s}={n}" for s, n in sorted(c.items())))
        return row

    def close(self):
        self.preds.close(); self.trial.close()
        lat = sorted(self.latency)
        self.write_info(ended_utc=self.now(), stop_reason=self.stop_reason, frames=sum(self.counts.values()),
                        events=self.events, status_counts=dict(self.counts),
                        latency_ms_median=lat[len(lat) // 2] if lat else None)
        if not self.quiet:
            print(f"{sum(self.counts.values())} frames, {self.events} events, {dict(self.counts)} -> {self.out}")


def run(session, frames):
    """Feed every (path, image) of a source through the session; Ctrl-C stops cleanly with all logs flushed."""
    try:
        for path, img in frames:
            session.process_frame(path, img)
    except KeyboardInterrupt:
        session.stop_reason = "ctrl-c"
    finally:
        session.close()


def export_replay(run_id, out, source="video", step=1.0):
    """A DEV run as a replay folder: video frames every `step` s (PNG, named by video frame id) or the run's stills
    (copied unchanged). Runs 4-5 are refused by real_data."""
    ix = R.Index(); os.makedirs(out, exist_ok=True); n = 0
    if source == "video":
        for t, img in R.iter_video(ix.video_path(run_id), step):
            cv2.imwrite(os.path.join(out, R.video_id(run_id, t) + ".png"), img); n += 1
    else:
        for f in ix.frames(run_id):
            shutil.copy2(os.path.join(ix.root, "images", f), out); n += 1
    print(f"run {run_id}: {n} frames ({source}) -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="live inspection runtime (replay or watched folder)")
    ap.add_argument("--source", help="replay:DIR or folder:DIR")
    ap.add_argument("--out"); ap.add_argument("--run-id"); ap.add_argument("--labels", help="expected states (trial log)")
    ap.add_argument("--gate", choices=("events", "each"), default="events")
    ap.add_argument("--mode", choices=MODES, default=LIVE_FILL); ap.add_argument("--track", action="store_true")
    ap.add_argument("--poll", type=float, default=0.25); ap.add_argument("--idle-exit", type=float)
    ap.add_argument("--note", default="")
    ap.add_argument("--export-replay", metavar="RUN"); ap.add_argument("--from", dest="from_", choices=("video", "stills"), default="video")
    ap.add_argument("--step", type=float, default=1.0)
    a = ap.parse_args()
    if a.export_replay:
        if not a.out:
            ap.error("--export-replay needs --out")
        export_replay(a.export_replay, a.out, a.from_, a.step)
    else:
        kind, _, folder = (a.source or "").partition(":")
        if kind not in ("replay", "folder") or not os.path.isdir(folder):
            ap.error("--source must be replay:DIR or folder:DIR with an existing DIR")
        ix = dataset_index()
        frames = replay(folder, ix) if kind == "replay" else watch(folder, a.poll, a.idle_exit)
        out = a.out or os.path.join(P.HERE, "results", "live", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
        run(Session(out, a.source, a.run_id, a.gate, a.mode, a.track, a.labels, a.note, ix=ix), frames)
