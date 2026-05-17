"""
Run validation and smoke tests for the bulk-generated v1 culture rollout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


BENCHMARK_DIR = ROOT / "data" / "benchmarks"
CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and smoke-test the bulk Mythic Clash v1 rollout.")
    parser.add_argument(
        "--summary",
        default=str(BENCHMARK_DIR / "bulk-rollout-build-summary.json"),
        help="Path to the bulk build summary JSON.",
    )
    parser.add_argument(
        "--output",
        default=str(BENCHMARK_DIR / "bulk-rollout-test-report.json"),
        help="Aggregate output report path.",
    )
    parser.add_argument("--seeds", default="31,47")
    parser.add_argument("--max-steps", type=int, default=140)
    parser.add_argument(
        "--include-greek-gate",
        action="store_true",
        help="Also run an Ancient Greek both-seat gate for each culture.",
    )
    return parser.parse_args()


def load_summary(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Bulk rollout summary must be a list of culture records.")
    return payload


def resolve_pack_path(item: dict[str, object]) -> Path:
    expected = Path(str(item["pack"]))
    if expected.exists():
        return expected
    culture = str(item["culture"])
    fallback = CARDS_DIR / f"{culture}-v1.json"
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"Could not resolve pack for {culture}.")


def resolve_deck_path(item: dict[str, object]) -> Path:
    expected = Path(str(item["deck"]))
    if expected.exists():
        return expected
    culture = str(item["culture"])
    matches = sorted(DECKS_DIR.glob(f"{culture}-*.json"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"Could not resolve deck for {culture}.")
    raise ValueError(f"Multiple deck candidates found for {culture}: {[path.name for path in matches]}")


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, cwd=ROOT)


def validate(pack: Path, deck: Path) -> dict[str, object]:
    proc = run_command(
        [sys.executable, str(ROOT / "scripts" / "validate-v1-deck.py"), "--pack", str(pack), "--deck", str(deck)]
    )
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def smoke(
    culture: str,
    pack: Path,
    deck: Path,
    seeds: str,
    max_steps: int,
    *,
    benchmarks: str = "ancient-greek,haitian-vodou,inuit",
    seat_mode: str = "single",
    output_suffix: str = "bulk-smoke",
) -> dict[str, object]:
    output = BENCHMARK_DIR / f"{culture}-{output_suffix}.json"
    proc = run_command(
        [
            sys.executable,
            str(ROOT / "scripts" / "run-v1-smoke-gauntlet.py"),
            "--pack",
            str(pack),
            "--deck",
            str(deck),
            "--candidate-name",
            culture,
            "--benchmarks",
            benchmarks,
            "--seeds",
            seeds,
            "--max-steps",
            str(max_steps),
            "--seat-mode",
            seat_mode,
            "--output",
            str(output),
        ]
    )
    payload = None
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
    return {
        "ok": proc.returncode == 0 and payload is not None,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "output": str(output),
        "summary": payload,
    }


def greek_record(summary: dict[str, object] | None) -> tuple[int, int, int]:
    if not summary:
        return (0, 0, 0)
    greek = summary.get("by_benchmark", {}).get("ancient-greek", {})
    return (
        int(greek.get("wins", 0)),
        int(greek.get("losses", 0)),
        int(greek.get("draws", 0)),
    )


def classify(record: dict[str, object]) -> list[str]:
    flags: list[str] = []
    if not record["validation"]["ok"]:
        flags.append("validation_fail")
        return flags

    smoke_summary = record["smoke"]["summary"]
    if not record["smoke"]["ok"] or not smoke_summary:
        flags.append("smoke_fail")
        return flags

    overall = smoke_summary["overall_record"]
    total_wins = int(overall["wins"])
    total_losses = int(overall["losses"])
    greek_wins, greek_losses, _ = greek_record(smoke_summary)

    if total_wins <= 1:
        flags.append("weak_field")
    elif total_wins >= 5:
        flags.append("strong_field")

    if greek_losses == 2 and greek_wins == 0:
        flags.append("greek_soft")
    elif greek_wins == 2 and greek_losses == 0:
        flags.append("greek_spike")

    if total_losses >= 5:
        flags.append("high_loss")

    return flags


def main() -> None:
    args = parse_args()
    items = load_summary(Path(args.summary))
    results: list[dict[str, object]] = []

    for item in items:
        culture = str(item["culture"])
        pack = resolve_pack_path(item)
        deck = resolve_deck_path(item)
        print(f"[{culture}] validating")
        validation = validate(pack, deck)
        smoke_result = {"ok": False, "stdout": "", "stderr": "", "output": "", "summary": None}
        greek_gate = {"ok": False, "stdout": "", "stderr": "", "output": "", "summary": None}
        if validation["ok"]:
            print(f"[{culture}] smoke")
            smoke_result = smoke(culture, pack, deck, args.seeds, args.max_steps)
            if args.include_greek_gate:
                print(f"[{culture}] greek-gate")
                greek_gate = smoke(
                    culture,
                    pack,
                    deck,
                    args.seeds,
                    args.max_steps,
                    benchmarks="ancient-greek",
                    seat_mode="both",
                    output_suffix="bulk-greek-gate",
                )
        record = {
            "culture": culture,
            "primary_family": item.get("primary_family", ""),
            "secondary_family": item.get("secondary_family", ""),
            "pack": str(pack),
            "deck": str(deck),
            "validation": validation,
            "smoke": smoke_result,
            "greek_gate": greek_gate,
        }
        record["flags"] = classify(record)
        results.append(record)

    passed_validation = sum(1 for record in results if record["validation"]["ok"])
    passed_smoke = sum(1 for record in results if record["smoke"]["ok"])
    flagged = [record["culture"] for record in results if record["flags"]]
    payload = {
        "summary_path": str(Path(args.summary)),
        "culture_count": len(results),
        "validated_count": passed_validation,
        "smoke_count": passed_smoke,
        "flagged_count": len(flagged),
        "flagged_cultures": flagged,
        "results": results,
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ["culture_count", "validated_count", "smoke_count", "flagged_count"]}, indent=2))
    if flagged:
        print("flagged:", ", ".join(flagged))


if __name__ == "__main__":
    main()
