from __future__ import annotations

TRACK2_REQUIRED_CLAUSES = [
    "simulate rare combinations of extreme weather and peak-demand pricing",
    "occupant safety outranks energy cost during extreme weather",
    "shed flexible loads before changing critical-zone comfort",
    "emit an observability trace for every conflict decision",
]


def optimize_energy_instructions(instruction: str) -> dict[str, object]:
    missing = [clause for clause in TRACK2_REQUIRED_CLAUSES if clause not in instruction]
    optimized = instruction
    if missing:
        optimized = instruction.rstrip() + "\n\nTrack 2 optimization rules:\n"
        optimized += "\n".join(f"- {clause}." for clause in missing)
    return {
        "changed": bool(missing),
        "missing_clauses": missing,
        "optimized_instruction": optimized,
    }

