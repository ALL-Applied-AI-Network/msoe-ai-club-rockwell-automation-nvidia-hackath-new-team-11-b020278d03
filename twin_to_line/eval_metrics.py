"""Evaluation metrics for Twin-to-Line. No model, no training: scores a predictions CSV against ground truth.

Result format (one row per position per inspection EVENT, not per video frame):
  run, event, position, ground_truth, predicted_state, defect_score, gt_sequence, pred_sequence
    ground_truth / predicted_state: pass | missing_cap | crooked_cap | damaged_vial | no_vial
    gt_sequence / pred_sequence   : missed | waiting | (blank when a vial is present)
    defect_score                  : higher = more likely defective (blank if the method has none)
A position is a DEFECT when its state is missing_cap / crooked_cap / damaged_vial, or no_vial with sequence
'missed'. 'no_vial' + 'waiting' is NOT a defect (a trailing empty position).

    python eval_metrics.py predictions.csv [threshold]
    python eval_metrics.py --selftest
"""
import csv, sys
from collections import Counter, defaultdict

DEFECT_STATES = {"missing_cap", "crooked_cap", "damaged_vial"}

def is_defect(state, seq):
    return state in DEFECT_STATES or (state == "no_vial" and seq == "missed")

def gt_class(r):
    if r["ground_truth"] == "no_vial":
        return "missed_placement" if r["gt_sequence"] == "missed" else "waiting"
    return r["ground_truth"]

def evaluate(rows, threshold=None):
    """rows: dicts with the columns above. If threshold is given and defect_score is present,
    a row counts as flagged when score >= threshold OR the predicted state/sequence is a defect."""
    def flagged(r):
        f = is_defect(r["predicted_state"], r.get("pred_sequence", ""))
        if threshold is not None and r.get("defect_score") not in (None, ""):
            f = f or float(r["defect_score"]) >= threshold
        return f
    out = {"n_positions": len(rows), "n_events": len({(r["run"], r["event"]) for r in rows})}
    gt_def = [r for r in rows if is_defect(r["ground_truth"], r["gt_sequence"])]
    gt_ok = [r for r in rows if not is_defect(r["ground_truth"], r["gt_sequence"])]
    fn = [r for r in gt_def if not flagged(r)]; fp = [r for r in gt_ok if flagged(r)]
    out["counts"] = {"defects": len(gt_def), "non_defects": len(gt_ok), "false_negatives": len(fn), "false_positives": len(fp),
                     "by_ground_truth_class": dict(Counter(gt_class(r) for r in rows))}
    out["defect_recall"] = round(1 - len(fn) / len(gt_def), 4) if gt_def else None
    out["false_positive_rate"] = round(len(fp) / len(gt_ok), 4) if gt_ok else None
    per = defaultdict(lambda: [0, 0, 0])            # class -> [n, flagged as any defect, exact class right]
    for r in gt_def:
        c = gt_class(r); per[c][0] += 1; per[c][1] += flagged(r)
        exact = (r["predicted_state"] == r["ground_truth"] and (c != "missed_placement" or r.get("pred_sequence") == "missed"))
        per[c][2] += exact
    out["per_class"] = {c: {"n": n, "detection_recall": round(d / n, 4), "exact_class_recall": round(e / n, 4), "false_negatives": n - d}
                        for c, (n, d, e) in sorted(per.items())}
    trailing = [r for r in rows if gt_class(r) == "waiting"]
    out["trailing_empty_false_alarms"] = sum(flagged(r) for r in trailing)
    empties = [r for r in rows if r["ground_truth"] == "no_vial" and r["predicted_state"] == "no_vial"]
    out["sequence_accuracy_on_detected_empties"] = (round(sum(r["gt_sequence"] == r.get("pred_sequence") for r in empties) / len(empties), 4)
                                                     if empties else None)
    scored = [r for r in rows if r.get("defect_score") not in (None, "")]
    if scored and gt_def and all(r.get("defect_score") not in (None, "") for r in gt_def):
        t_all = min(float(r["defect_score"]) for r in gt_def)              # MAIC spec: threshold that catches every known defect
        fa = sum(float(r["defect_score"]) >= t_all for r in gt_ok if r.get("defect_score") not in (None, ""))
        out["false_alarm_rate_at_full_recall"] = {"threshold": t_all, "rate": round(fa / len(gt_ok), 4) if gt_ok else None}
    out["threshold_used"] = threshold
    return out

def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def selftest():
    R = lambda run, ev, pos, gt, pred, score, gseq="", pseq="": dict(run=run, event=ev, position=pos, ground_truth=gt,
            predicted_state=pred, defect_score=score, gt_sequence=gseq, pred_sequence=pseq)
    rows = [
        R("5", 1, "G01", "pass", "pass", 0.10), R("5", 1, "G02", "pass", "missing_cap", 0.70),      # FP
        R("5", 1, "G03", "missing_cap", "missing_cap", 0.90), R("5", 1, "G04", "crooked_cap", "pass", 0.40),  # FN
        R("5", 1, "G05", "crooked_cap", "crooked_cap", 0.80),
        R("5", 1, "G06", "no_vial", "no_vial", 0.95, "missed", "missed"),                            # missed placement caught
        R("5", 1, "G07", "no_vial", "no_vial", 0.05, "waiting", "waiting"),                          # trailing empty, fine
        R("5", 1, "G08", "no_vial", "no_vial", 0.60, "waiting", "missed"),                           # trailing-empty false alarm
        R("5", 2, "G01", "pass", "pass", 0.20), R("5", 2, "G02", "missing_cap", "crooked_cap", 0.85), # detected, wrong class
    ]
    m = evaluate(rows)
    assert m["counts"] == {"defects": 5, "non_defects": 5, "false_negatives": 1, "false_positives": 2,
                           "by_ground_truth_class": {"pass": 3, "missing_cap": 2, "crooked_cap": 2, "missed_placement": 1, "waiting": 2}}, m["counts"]
    assert m["defect_recall"] == 0.8 and m["false_positive_rate"] == 0.4
    assert m["per_class"]["missing_cap"] == {"n": 2, "detection_recall": 1.0, "exact_class_recall": 0.5, "false_negatives": 0}
    assert m["per_class"]["crooked_cap"] == {"n": 2, "detection_recall": 0.5, "exact_class_recall": 0.5, "false_negatives": 1}
    assert m["per_class"]["missed_placement"]["detection_recall"] == 1.0
    assert m["trailing_empty_false_alarms"] == 1
    assert m["sequence_accuracy_on_detected_empties"] == round(2 / 3, 4)
    # every defect caught needs threshold 0.40 (G04); non-defects scoring >= 0.40: G02 0.70, G08 0.60 -> 2/5
    assert m["false_alarm_rate_at_full_recall"] == {"threshold": 0.40, "rate": 0.4}
    m2 = evaluate(rows, threshold=0.5)        # score >= 0.5 also flags; G04 (0.40) stays a FN
    assert m2["counts"]["false_negatives"] == 1 and m2["counts"]["false_positives"] == 2
    m3 = evaluate(rows, threshold=0.35)       # now G04 is caught; G01 run 5 ev 1 (0.10) and ev 2 (0.20) stay clean
    assert m3["counts"]["false_negatives"] == 0 and m3["defect_recall"] == 1.0
    print("selftest passed: recall, FP rate, per-class, trailing empties, sequence accuracy, FAR@full-recall, thresholds")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
    else:
        import json
        print(json.dumps(evaluate(load(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else None), indent=1))
