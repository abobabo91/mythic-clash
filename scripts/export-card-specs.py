"""
Export the current figure dataset into the draft structured card schema.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.card_schema import dataclass_to_dict
from game.card_translation import translate_raw_figure
from game.engine import derive_keywords
from game.rules import minion_attack, minion_health


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export figure cards into the draft card schema.")
    parser.add_argument(
        "--culture",
        action="append",
        default=[],
        help="Optional culture slug filter. Can be passed multiple times.",
    )
    parser.add_argument(
        "--output",
        default="data/card-specs-v1.json",
        help="Output path for the exported card specs.",
    )
    return parser.parse_args()


def load_figures(culture_filters: set[str]) -> list[dict[str, Any]]:
    figures: list[dict[str, Any]] = []
    for path in sorted((ROOT / "data" / "figures").glob("*.json")):
        culture_slug = path.stem
        if culture_filters and culture_slug not in culture_filters:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        figures.extend(payload["figures"])
    return figures


def export_cards(figures: list[dict[str, Any]]) -> dict[str, Any]:
    cards: list[dict[str, Any]] = []
    cultures: set[str] = set()
    blueprint_ready = 0

    for figure in figures:
        stats = figure["stats"]
        attack = minion_attack(stats["power"], stats["speed"])
        health = minion_health(stats["defense"], stats["wisdom"])
        keywords = derive_keywords(figure, attack, health)
        translation = translate_raw_figure(figure, keywords=keywords)
        if translation.ability_blueprint_ready:
            blueprint_ready += 1
        cultures.add(translation.card.culture_slug)
        cards.append(
            {
                "card": dataclass_to_dict(translation.card),
                "translation": {
                    "ability_blueprint_ready": translation.ability_blueprint_ready,
                    "inferred_effect_kinds": translation.inferred_effect_kinds,
                    "inferred_target_rule": translation.inferred_target_rule,
                    "unsupported_concepts": translation.unsupported_concepts,
                },
            }
        )

    return {
        "schema_version": "card-system-v1-draft",
        "source": "current-figure-dataset",
        "cultures_exported": len(cultures),
        "figures_exported": len(cards),
        "simple_blueprints": blueprint_ready,
        "manual_rules_rewrites": len(cards) - blueprint_ready,
        "cards": cards,
    }


def main() -> None:
    args = parse_args()
    culture_filters = {slug.strip() for slug in args.culture if slug.strip()}
    figures = load_figures(culture_filters)
    export = export_cards(figures)

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "output": str(output_path),
                "cultures_exported": export["cultures_exported"],
                "figures_exported": export["figures_exported"],
                "simple_blueprints": export["simple_blueprints"],
                "manual_rules_rewrites": export["manual_rules_rewrites"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
