"""
Generate a compact statistics report for figure balance across cultures.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CULTURES_PATH = ROOT / "data" / "cultures.json"
FIGURES_DIR = ROOT / "data" / "figures"
REPORT_MD = ROOT / "data" / "figures-statistics.md"
REPORT_CSV = ROOT / "data" / "figures-culture-summary.csv"


def avg(values):
    return round(sum(values) / len(values), 2) if values else 0.0


def pct(part, whole):
    return round((part / whole) * 100, 1) if whole else 0.0


with CULTURES_PATH.open(encoding="utf-8") as fh:
    cultures = json.load(fh)["cultures"]

meta = {culture["slug"]: culture for culture in cultures}

rows = []
region_values = defaultdict(list)
region_power = defaultdict(list)
region_magic = defaultdict(list)
region_wisdom = defaultdict(list)
region_defense = defaultdict(list)
rarity_counter = Counter()
alignment_counter = Counter()

for fp in sorted(FIGURES_DIR.glob("*.json")):
    with fp.open(encoding="utf-8") as fh:
        payload = json.load(fh)

    slug = fp.stem
    figures = payload["figures"]
    totals = [sum(figure["stats"].values()) for figure in figures]
    power = [figure["stats"]["power"] for figure in figures]
    defense = [figure["stats"]["defense"] for figure in figures]
    speed = [figure["stats"]["speed"] for figure in figures]
    magic = [figure["stats"]["magic"] for figure in figures]
    wisdom = [figure["stats"]["wisdom"] for figure in figures]
    aggression = [figure["stats"]["power"] + figure["stats"]["speed"] for figure in figures]
    mystic = [figure["stats"]["magic"] + figure["stats"]["wisdom"] for figure in figures]
    durable = [figure["stats"]["defense"] + figure["stats"]["wisdom"] for figure in figures]

    rarity = Counter(figure["rarity"] for figure in figures)
    alignment = Counter(figure["alignment"] for figure in figures)
    rarity_counter.update(rarity)
    alignment_counter.update(alignment)

    region = meta[slug]["region"]
    region_values[region].append(avg(totals))
    region_power[region].append(avg(power))
    region_magic[region].append(avg(magic))
    region_wisdom[region].append(avg(wisdom))
    region_defense[region].append(avg(defense))

    row = {
        "slug": slug,
        "name": meta[slug]["name"],
        "region": region,
        "avg_total": avg(totals),
        "min_total": min(totals),
        "max_total": max(totals),
        "avg_power": avg(power),
        "avg_defense": avg(defense),
        "avg_speed": avg(speed),
        "avg_magic": avg(magic),
        "avg_wisdom": avg(wisdom),
        "avg_aggression": avg(aggression),
        "avg_mystic": avg(mystic),
        "avg_durable": avg(durable),
        "legendary": rarity["legendary"],
        "rare": rarity["rare"],
        "uncommon": rarity["uncommon"],
        "common": rarity["common"],
        "light": alignment["light"],
        "neutral": alignment["neutral"],
        "dark": alignment["dark"],
        "chaos": alignment["chaos"],
        "rare_plus_legendary": rarity["rare"] + rarity["legendary"],
    }
    rows.append(row)

rows_by_strength = sorted(
    rows,
    key=lambda row: (
        -row["avg_total"],
        -row["rare_plus_legendary"],
        -row["avg_power"],
        row["slug"],
    ),
)

rows_by_power = sorted(rows, key=lambda row: (-row["avg_power"], -row["avg_total"], row["slug"]))
rows_by_magic = sorted(rows, key=lambda row: (-row["avg_magic"], -row["avg_total"], row["slug"]))
rows_by_wisdom = sorted(rows, key=lambda row: (-row["avg_wisdom"], -row["avg_total"], row["slug"]))
rows_by_defense = sorted(rows, key=lambda row: (-row["avg_defense"], -row["avg_total"], row["slug"]))
rows_by_aggression = sorted(rows, key=lambda row: (-row["avg_aggression"], -row["avg_total"], row["slug"]))
rows_by_mystic = sorted(rows, key=lambda row: (-row["avg_mystic"], -row["avg_total"], row["slug"]))


def format_ranked(items, key, limit=10):
    lines = []
    for index, row in enumerate(items[:limit], 1):
        lines.append(
            f"{index}. {row['name']} (`{row['slug']}`) - {row[key]}"
        )
    return lines


def format_region_rows():
    ordered = []
    for region in sorted(region_values):
        ordered.append(
            (
                region,
                round(sum(region_values[region]) / len(region_values[region]), 2),
                round(sum(region_power[region]) / len(region_power[region]), 2),
                round(sum(region_magic[region]) / len(region_magic[region]), 2),
                round(sum(region_wisdom[region]) / len(region_wisdom[region]), 2),
                round(sum(region_defense[region]) / len(region_defense[region]), 2),
                len(region_values[region]),
            )
        )
    ordered.sort(key=lambda row: (-row[1], row[0]))
    return ordered


with REPORT_CSV.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(
        fh,
        fieldnames=[
            "slug",
            "name",
            "region",
            "avg_total",
            "min_total",
            "max_total",
            "avg_power",
            "avg_defense",
            "avg_speed",
            "avg_magic",
            "avg_wisdom",
            "avg_aggression",
            "avg_mystic",
            "avg_durable",
            "legendary",
            "rare",
            "uncommon",
            "common",
            "light",
            "neutral",
            "dark",
            "chaos",
            "rare_plus_legendary",
        ],
    )
    writer.writeheader()
    writer.writerows(rows_by_strength)


total_cultures = len(rows)
total_figures = total_cultures * 20
overall_avg = round(sum(row["avg_total"] for row in rows) / total_cultures, 2)

report_lines = [
    "# Figures Statistics",
    "",
    "## Overview",
    "",
    f"- Cultures analyzed: **{total_cultures}**",
    f"- Total figures analyzed: **{total_figures}**",
    f"- Global average stat total per figure: **{overall_avg}**",
    f"- Rarity mix: `legendary {rarity_counter['legendary']}`, `rare {rarity_counter['rare']}`, `uncommon {rarity_counter['uncommon']}`, `common {rarity_counter['common']}`",
    f"- Alignment mix: `light {alignment_counter['light']}`, `neutral {alignment_counter['neutral']}`, `dark {alignment_counter['dark']}`, `chaos {alignment_counter['chaos']}`",
    "",
    "## Strongest Cultures By Average Total",
    "",
]

report_lines.extend(format_ranked(rows_by_strength, "avg_total", 15))

report_lines.extend(
    [
        "",
        "## Lowest Average Total",
        "",
    ]
)
report_lines.extend(format_ranked(list(reversed(rows_by_strength)), "avg_total", 10))

report_lines.extend(
    [
        "",
        "## Leaders By Individual Stat",
        "",
        "### Power",
        "",
    ]
)
report_lines.extend(format_ranked(rows_by_power, "avg_power", 10))
report_lines.extend(["", "### Defense", ""])
report_lines.extend(format_ranked(rows_by_defense, "avg_defense", 10))
report_lines.extend(["", "### Magic", ""])
report_lines.extend(format_ranked(rows_by_magic, "avg_magic", 10))
report_lines.extend(["", "### Wisdom", ""])
report_lines.extend(format_ranked(rows_by_wisdom, "avg_wisdom", 10))

report_lines.extend(
    [
        "",
        "## Playstyle Lean",
        "",
        "### Aggression Index",
        "",
    ]
)
report_lines.extend(format_ranked(rows_by_aggression, "avg_aggression", 10))
report_lines.extend(["", "### Mystic Index", ""])
report_lines.extend(format_ranked(rows_by_mystic, "avg_mystic", 10))

report_lines.extend(
    [
        "",
        "## Region Averages",
        "",
        "| Region | Avg Total | Avg Power | Avg Magic | Avg Wisdom | Avg Defense | Cultures |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
)

for region, avg_total, avg_power_value, avg_magic_value, avg_wisdom_value, avg_defense_value, count in format_region_rows():
    report_lines.append(
        f"| {region} | {avg_total} | {avg_power_value} | {avg_magic_value} | {avg_wisdom_value} | {avg_defense_value} | {count} |"
    )

report_lines.extend(
    [
        "",
        "## High-Rarity Density",
        "",
        "| Culture | Rare + Legendary | Share |",
        "|---|---:|---:|",
    ]
)

for row in sorted(rows, key=lambda item: (-item["rare_plus_legendary"], -item["avg_total"], item["slug"]))[:15]:
    report_lines.append(
        f"| {row['name']} | {row['rare_plus_legendary']} | {pct(row['rare_plus_legendary'], 20)}% |"
    )

REPORT_MD.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

print(f"Wrote {REPORT_MD.relative_to(ROOT)}")
print(f"Wrote {REPORT_CSV.relative_to(ROOT)}")
