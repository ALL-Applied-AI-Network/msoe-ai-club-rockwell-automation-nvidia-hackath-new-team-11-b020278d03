import csv, os, shutil, subprocess, sys, tempfile, unittest, unittest.mock
from datetime import datetime, timedelta
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import positions as P
import real_data as R
import frame_warp as FW
import live_inspect as L
from replay_1080 import warp_up

PM = P.PositionMap()
FWARP = FW.FrameWarp()
YELLOW = (0, 220, 230)
T0 = datetime(2026, 10, 26, 12, 30, 0)
EVENTS = os.path.join(P.HERE, "results", "prototype", "events")
DEV_STILLS = [os.path.join(EVENTS, "cap_seal_video_1.mp4@t1050.0.png"), os.path.join(EVENTS, "cap_seal_video_1.mp4@t0464.0.png")]
RUN3_EMPTY = "cap_seal_20260923_184630_557477.jpg"
DEV = os.path.exists(os.path.join(R.REAL_ROOT, "image_index.csv")) and all(map(os.path.exists, DEV_STILLS))


def fixture(filled=()):
    img = np.full((480, 640, 3), 90, np.uint8)
    for i in filled:
        x, y = PM.cap_centers[i - 1]
        cv2.circle(img, (int(round(x)), int(round(y))), 10, YELLOW, -1)
    return img


def name(k):
    return f"staged_{(T0 + timedelta(seconds=30 * k)).strftime('%Y%m%d_%H%M%S_%f')}.png"


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def score(frames, track=False):
    """Session --gate each over (name, image) pairs; predictions keyed by (frame, position), without the event number."""
    out = tempfile.mkdtemp(); s = L.Session(out, gate="each", track=track, ix=None, quiet=True)
    for n, img in frames:
        s.process_frame(n, img)
    s.close()
    return {(r["frame"], r["position"]): {k: v for k, v in r.items() if k != "event"} for r in read_csv(os.path.join(out, "predictions.csv"))}


class StagedStillsIndependent(unittest.TestCase):
    """--gate each (no --track): every staged still is resolved from that image alone (fill frontier included)."""

    def check(self, a, b):
        together, reverse = score([a, b]), score([b, a])
        alone = {**score([a]), **score([b])}
        self.assertEqual(together, alone)
        self.assertEqual(reverse, alone)
        return alone

    def test_synthetic_fixtures(self):
        a = (name(0), fixture([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12]))           # G04 empty inside the prefix -> MISSED
        b = (name(1), fixture([1, 2]))                                         # G04 after the frontier -> WAITING
        alone = self.check(a, b)
        self.assertEqual(alone[(a[0], "G04")]["final_state"], "MISSED")
        self.assertEqual(alone[(b[0], "G04")]["final_state"], "WAITING")
        self.assertEqual({alone[(a[0], "G12")]["K"], alone[(b[0], "G12")]["K"]}, {"12", "2"})

    def test_tracker_would_carry_state(self):                                   # why --track is not in the staged command
        a, b = (name(0), fixture(range(1, 13))), (name(1), fixture([1, 2]))
        self.assertNotEqual(score([a, b], track=True)[(b[0], "G05")]["final_state"], score([b])[(b[0], "G05")]["final_state"])

    @unittest.skipUnless(DEV, "needs the DEV dataset and the cached run-1 event frames")
    def test_two_dev_fixtures_in_a_row(self):
        ix = R.Index()
        a = (DEV_STILLS[0], cv2.imread(DEV_STILLS[0]))
        b = (RUN3_EMPTY, ix.load(RUN3_EMPTY))
        c = (DEV_STILLS[1], cv2.imread(DEV_STILLS[1]))
        self.check(a, b); self.check(a, c)
        self.check((a[0], warp_up(a[1], FWARP)), (c[0], warp_up(c[1], FWARP)))  # the same at 1080


class Preflight(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); os.makedirs(os.path.join(self.d, "expected"))
        frames = {"run1_640": [(name(0), fixture([1, 2, 3])), (name(1), fixture(range(1, 9)))]}
        frames["run1_1080"] = [(n, warp_up(im, FWARP)) for n, im in frames["run1_640"]]
        frames["still_1080"] = [("still.png", warp_up(fixture(), FWARP))]
        for k, fs in frames.items():
            os.makedirs(os.path.join(self.d, k))
            for n, im in fs:
                cv2.imwrite(os.path.join(self.d, k, n), im)
            preds, _ = L.score_folder(os.path.join(self.d, k), os.path.join(self.d, "_mac", k))
            shutil.copy2(os.path.join(self.d, "_mac", k, "predictions.csv"), os.path.join(self.d, "expected", k + ".csv"))

    def test_ok_then_fails_on_a_changed_state_or_wrong_path(self):
        self.assertTrue(L.preflight(self.d, tempfile.mkdtemp()))
        exp = os.path.join(self.d, "expected", "run1_640.csv"); rows = read_csv(exp)
        rows[0]["final_state"] = "DEFECT"
        with open(exp, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        self.assertFalse(L.preflight(self.d, tempfile.mkdtemp()))

    def test_fails_when_a_1080_set_runs_the_640_path(self):
        st = os.path.join(self.d, "still_1080"); os.remove(os.path.join(st, "still.png"))
        cv2.imwrite(os.path.join(st, "still.png"), fixture())
        self.assertFalse(L.preflight(self.d, tempfile.mkdtemp()))


class Provenance(unittest.TestCase):
    def test_archive_commit_without_git(self):
        f = tempfile.NamedTemporaryFile("w", delete=False); f.write("0123456789abcdef\n"); f.close()
        no_git = unittest.mock.patch.object(L.subprocess, "run", side_effect=OSError("no git"))
        with no_git, unittest.mock.patch.object(L, "ARCHIVE_COMMIT", f.name):
            self.assertEqual(L.code_version(), "0123456 (archive)")
        with no_git:                                                            # the repo file is still a placeholder
            self.assertEqual(L.code_version(), "unknown")

    def test_git_archive_fills_the_commit(self):
        head = subprocess.run(["git", "-C", P.HERE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        out = subprocess.run(["git", "-C", P.HERE, "archive", "HEAD", "twin_to_line/ARCHIVE_COMMIT"], capture_output=True)
        if out.returncode != 0:
            self.skipTest("ARCHIVE_COMMIT not committed yet")
        import io, tarfile
        with tarfile.open(fileobj=io.BytesIO(out.stdout)) as t:
            self.assertEqual(t.extractfile("twin_to_line/ARCHIVE_COMMIT").read().decode().strip(), head)

    def test_runtime_files_and_bootstrap(self):
        for f in L.RUNTIME_FILES:
            self.assertTrue(os.path.exists(os.path.join(P.HERE, f)), f)
        b = open(os.path.join(P.HERE, "gb10", "bootstrap.sh")).read()
        self.assertIn("--no-index", b); self.assertIn("--preflight", b); self.assertIn("sha256sum --quiet -c SHA256SUMS", b)
        self.assertTrue(os.access(os.path.join(P.HERE, "gb10", "bootstrap.sh"), os.X_OK))


if __name__ == "__main__":
    unittest.main()
