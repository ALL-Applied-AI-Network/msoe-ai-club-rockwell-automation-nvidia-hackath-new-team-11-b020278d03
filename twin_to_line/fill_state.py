"""Fill-sequence reasoning (D007): turn a per-position VISUAL observation into a PROCESS state.

Kept separate from vision on purpose: the classifier only says what a crop looks like; this module knows
the fill order (G01..G30 = twin numbering = robot fill order) and how many placements were expected (K).

Visual states (same terms as eval_metrics.py): pass | missing_cap | crooked_cap | damaged_vial | no_vial | unknown
Process states: PASS | DEFECT | MISSED | WAITING | UNSURE

    position <= K : pass -> PASS, cap/vial defect -> DEFECT, no_vial -> MISSED (skipped placement)
    position >  K : no_vial -> WAITING, anything occupied -> UNSURE (nothing should be there yet)
    K unknown     : pass / defects resolve as above; no_vial -> UNSURE (missed vs waiting unresolved)
    unknown visual (occluded, ambiguous) -> UNSURE everywhere
"""
N_POSITIONS = 30
DEFECT_VISUALS = {"missing_cap", "crooked_cap", "damaged_vial"}
VISUAL_STATES = {"pass", "no_vial", "unknown"} | DEFECT_VISUALS
FINAL_STATES = ("PASS", "DEFECT", "MISSED", "WAITING", "UNSURE")


def check_fill_count(fill_count):
    if fill_count is None:
        return None
    if isinstance(fill_count, bool) or not isinstance(fill_count, int) or not 0 <= fill_count <= N_POSITIONS:
        raise ValueError(f"fill count must be an int in 0..{N_POSITIONS} or None, got {fill_count!r}")
    return fill_count


def resolve_state(index, fill_count, visual):
    """index: 1..30 (G01 = 1). fill_count: placements expected so far (K), or None if unknown.
    Returns (final_state, reason)."""
    if not 1 <= index <= N_POSITIONS:
        raise ValueError(f"position index must be 1..{N_POSITIONS}, got {index!r}")
    if visual not in VISUAL_STATES:
        raise ValueError(f"unknown visual state {visual!r}")
    K = check_fill_count(fill_count)
    if visual == "unknown":
        return "UNSURE", "vision could not decide"
    if K is not None and index > K:
        if visual == "no_vial":
            return "WAITING", f"after fill count K={K}"
        return "UNSURE", f"occupied ({visual}) beyond fill count K={K}"
    if visual == "pass":
        return "PASS", ""
    if visual in DEFECT_VISUALS:
        return "DEFECT", visual
    if K is None:                                                     # visual == no_vial
        return "UNSURE", "empty; fill count unknown (missed vs waiting unresolved)"
    return "MISSED", f"empty inside the filled prefix (K={K})"


def infer_fill_count(visuals):
    """K from occupancy: the highest position that visibly holds a vial (any visual except no_vial / unknown).
    visuals: list of 30 visual states in G01..G30 order. Limitation: a skipped LAST placement looks exactly
    like 'waiting', so prefer a real placement count / order-complete signal whenever one exists."""
    if len(visuals) != N_POSITIONS:
        raise ValueError(f"need {N_POSITIONS} visual states, got {len(visuals)}")
    occupied = [i for i, v in enumerate(visuals, 1) if v not in ("no_vial", "unknown")]
    return max(occupied, default=0)


def resolve_fixture(visuals, fill_count=None, infer=False):
    """All 30 positions at once. Returns (K, K_source, [(final_state, reason), ...]);
    K_source is 'given', 'inferred' or 'unknown'."""
    if fill_count is not None:
        K, src = check_fill_count(fill_count), "given"
    elif infer:
        K, src = infer_fill_count(visuals), "inferred"
    else:
        K, src = None, "unknown"
    return K, src, [resolve_state(i, K, v) for i, v in enumerate(visuals, 1)]
