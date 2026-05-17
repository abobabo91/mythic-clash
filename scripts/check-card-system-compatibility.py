"""
Check how well the current figure dataset fits the structured card system.

This script gives us an honest migration read:
- figure bodies that already translate cleanly
- ability text that fits the new effect grammar
- concepts that still depend on the older broader generator language
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.card_translation import summarize_unsupported_concepts, translate_raw_figure
from game.engine import derive_keywords
from game.card_schema import dataclass_to_dict
from game.rules import minion_attack, minion_health


FIGURES_DIR = ROOT / "data" / "figures"
REPORT_JSON = ROOT / "data" / "card-system-compatibility.json"
REPORT_MD = ROOT / "data" / "card-system-compatibility.md"


def pct(part: int, whole: int) -> str:
    return f"{(part / whole * 100):.1f}%" if whole else "0.0%"


def main() -> None:
    translations = []
    culture_counts: Counter[str] = Counter()
    culture_blueprints: Counter[str] = Counter()
    ability_text_counter: Counter[str] = Counter()
    keyword_counter: Counter[str] = Counter()

    for fp in sorted(FIGURES_DIR.glob("*.json")):
        payload = json.loads(fp.read_text(encoding="utf-8"))
        culture_slug = fp.stem
        for figure in payload["figures"]:
            culture_counts[culture_slug] += 1
            attack = minion_attack(figure["stats"]["power"], figure["stats"]["speed"])
            health = minion_health(figure["stats"]["defense"], figure["stats"]["wisdom"])
            keywords = derive_keywords(figure, attack, health)
            translation = translate_raw_figure(figure, keywords=keywords)
            translations.append(translation)
            ability_text_counter.update([figure["ability"]["description"]])
            keyword_counter.update(translation.card.keywords)
            if translation.ability_blueprint_ready:
                culture_blueprints[culture_slug] += 1

    total = len(translations)
    body_ready = total
    blueprint_ready = sum(1 for item in translations if item.ability_blueprint_ready)
    keyword_ready = sum(1 for item in translations if item.card.keywords)
    unsupported_counter = summarize_unsupported_concepts(translations)
    requires_manual_design = total - blueprint_ready

    culture_rows = []
    for slug, count in sorted(culture_counts.items()):
        ready = culture_blueprints[slug]
        culture_rows.append(
            {
                "culture_slug": slug,
                "figure_count": count,
                "blueprint_ready": ready,
                "blueprint_ready_pct": round(ready / count * 100, 1),
            }
        )
    culture_rows.sort(key=lambda row: (row["blueprint_ready_pct"], row["culture_slug"]))

    top_duplicates = [
        {"description": text, "count": count}
        for text, count in ability_text_counter.most_common(15)
    ]

    report = {
        "cultures": len(culture_counts),
        "figures": total,
        "body_ready": body_ready,
        "body_ready_pct": round(body_ready / total * 100, 1),
        "keyword_ready": keyword_ready,
        "keyword_ready_pct": round(keyword_ready / total * 100, 1),
        "ability_blueprint_ready": blueprint_ready,
        "ability_blueprint_ready_pct": round(blueprint_ready / total * 100, 1),
        "requires_manual_design": requires_manual_design,
        "requires_manual_design_pct": round(requires_manual_design / total * 100, 1),
        "top_keywords": keyword_counter.most_common(12),
        "unsupported_concepts": unsupported_counter.most_common(),
        "most_duplicate_ability_descriptions": top_duplicates,
        "lowest_blueprint_ready_cultures": culture_rows[:20],
        "sample_translations": [dataclass_to_dict(item.card) for item in translations[:5]],
    }

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Card System Compatibility",
        "",
        "## Summary",
        "",
        f"- Cultures checked: **{len(culture_counts)}**",
        f"- Figures checked: **{total}**",
        f"- Figures whose **body** already translates cleanly: **{body_ready}** ({pct(body_ready, total)})",
        f"- Figures with at least one inferred keyword in the new model: **{keyword_ready}** ({pct(keyword_ready, total)})",
        f"- Figures with a **simple ability blueprint** that fits the new grammar without extra redesign: **{blueprint_ready}** ({pct(blueprint_ready, total)})",
        f"- Figures that still need manual rules rewriting or broader primitive support: **{requires_manual_design}** ({pct(requires_manual_design, total)})",
        "",
        "## What This Means",
        "",
        "- The current figure list is compatible with the new card **body** model.",
        "- The current figure list is **not** yet directly compatible with the full structured ability model at a high rate.",
        "- The main migration pain is not stats, rarity, or culture ownership. It is the current broad freeform ability language.",
        "",
        "## Top Unsupported Concept Buckets",
        "",
    ]

    for label, count in unsupported_counter.most_common():
        lines.append(f"- `{label}` appears in **{count}** figure abilities.")

    lines.extend(
        [
            "",
            "## Most Repeated Ability Descriptions",
            "",
        ]
    )
    for row in top_duplicates:
        lines.append(f"- **{row['count']}**x: {row['description']}")

    lines.extend(
        [
            "",
            "## Lowest Blueprint-Ready Cultures",
            "",
            "| Culture | Figures | Simple Blueprints | Rate |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in culture_rows[:20]:
        lines.append(
            f"| {row['culture_slug']} | {row['figure_count']} | {row['blueprint_ready']} | {row['blueprint_ready_pct']}% |"
        )

    lines.extend(
        [
            "",
            "## Migration Read",
            "",
            "The existing dataset already works for:",
            "",
            "- figure identity",
            "- cost / attack / health projection",
            "- culture ownership",
            "- rarity and uniqueness decisions",
            "- keyword inference as a starting point",
            "",
            "The existing dataset still needs redesign for:",
            "",
            "- old five-stat ability language (`power`, `defense`, `speed`, `magic`, `wisdom`)",
            "- broad custom subsystem wording like hidden cards, reserve, resource growth, and alignment-specific checks",
            "- repeated template text that does not create a clean faction role on its own",
            "",
            "## Files",
            "",
            f"- JSON report: `{REPORT_JSON.relative_to(ROOT)}`",
            f"- Markdown report: `{REPORT_MD.relative_to(ROOT)}`",
        ]
    )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Wrote {REPORT_JSON.relative_to(ROOT)}")
    print(f"Wrote {REPORT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

