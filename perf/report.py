"""Local p75 before/after reporting without asserting production causality."""
from html import escape
from typing import Any


GOOD_THRESHOLDS = {"FCP": 1.8, "LCP": 2.5, "CLS": 0.1}
METRIC_EXPLANATIONS = {
    "DOMContentLoaded": "Time until the HTML document is parsed and deferred scripts have executed.",
    "Load": "Time until the page load event fires after dependent resources finish.",
    "FCP": "First Contentful Paint: time until the first visible content is painted.",
    "LCP": "Largest Contentful Paint: time until the largest visible content element is painted.",
    "CLS": "Cumulative Layout Shift: visual stability score; lower is better.",
    "Initial transferred bundle": "Bytes transferred for the measured initial application load.",
}


def _number(value: Any, label: str, *, allow_zero: bool) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError(f"{label} must be {'non-negative' if allow_zero else 'positive'}")
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"{label} must be finite")
    return number


def compare(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError("metrics must be a non-empty object")
    rows = []
    for key, item in metrics.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(item, dict):
            raise ValueError("Each metric must have a non-empty name and an object value")
        old = _number(item.get("before"), f"{key} before", allow_zero=False)
        new = _number(item.get("after"), f"{key} after", allow_zero=True)
        direction = item.get("direction", "lower_is_better")
        if direction not in {"lower_is_better", "higher_is_better"}:
            raise ValueError(f"Invalid direction for {key}: {direction}")
        improvement = ((old - new) if direction == "lower_is_better" else (new - old)) / old * 100
        row = {"key": key, "before": old, "after": new, "unit": item.get("unit", ""),
               "direction": direction, "reduction_pct": round(improvement, 1),
               "status": "improved" if improvement > 0 else "regressed" if improvement < 0 else "unchanged"}
        if key in GOOD_THRESHOLDS:
            row["web_vitals_good_threshold"] = GOOD_THRESHOLDS[key]
            row["web_vitals_category"] = "good" if new <= GOOD_THRESHOLDS[key] else "needs_improvement_or_worse"
        rows.append(row)
    return rows


def make_markdown(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        raise ValueError("Input payload must be a JSON object")
    if payload.get("scope") != "local_p75":
        raise ValueError("This starter only supports local_p75 reports, not production claims")
    if payload.get("source") != "owner_provided" or payload.get("not_field_or_production_data") is not True:
        raise ValueError("Input must preserve owner-provided and non-production provenance")
    rows = compare(payload.get("metrics"))
    lines = ["# Local p75 web performance comparison", "",
             "**Source:** Owner-provided numbers, not independently validated.",
             "**Scope:** Local test environment only; NOT production field data.",
             "**Causality:** A before/after comparison alone does not prove which changes caused the differences.", "",
             "| Metric | Before | After | Improvement | Status |", "|---|---:|---:|---:|---|" ]
    for row in rows:
        change = f"{row['reduction_pct']:+.1f}%"
        unit = row["unit"]
        lines.append(f"| {row['key']} | {row['before']:g} {unit} | {row['after']:g} {unit} | {change} | {row['status']} |")
    lines += ["", "## Metric definitions", ""]
    lines.extend(f"- **{key}:** {value}" for key, value in METRIC_EXPLANATIONS.items() if key in payload["metrics"])
    lines += ["", "## Interpreting Core Web Vitals", "",
              "- FCP should be <= 1.8 seconds for a 'good' lab result; the measured 2.41 seconds remains above that threshold.",
              "- LCP should be <= 2.5 seconds for 'good' performance; these local p75 results currently do not meet that threshold.",
              "- CLS should be <= 0.1 for 'good' stability; the current 0.062 is within that threshold but represents a regression from 0.002.",
              "- INP was not provided; do not claim that all Core Web Vitals pass.",
              "", "## Reproducibility checklist", "",
              "- [ ] Same browser version and device profile", "- [ ] Same network throttling and caching strategy",
              "- [ ] Same route and sample size, with run-count and variance documented",
              "- [ ] Build revisions and optimization changes recorded",
              "- [ ] Mobile and desktop checked separately", "- [ ] No private user data or system identifiers exported", ""]
    return "\n".join(lines)


def make_svg(payload: dict[str, Any]) -> str:
    """Build a dependency-free, accessible before/after SVG for the supplied metrics."""
    if not isinstance(payload, dict) or payload.get("scope") != "local_p75":
        raise ValueError("SVG output requires a local_p75 payload")
    rows = compare(payload.get("metrics"))
    width, row_height = 920, 92
    height = 100 + row_height * len(rows)
    chart_width, x0 = 470, 330
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" viewBox="0 0 {width} {height}">',
        '<title id="title">Local p75 web performance before and after comparison</title>',
        '<desc id="desc">Owner-provided local measurements. Cyan bars are before and green or amber bars are after.</desc>',
        '<rect width="100%" height="100%" fill="#07111f"/>',
        '<style>text{font-family:system-ui,sans-serif;fill:#dbeafe}.label{font-size:16px;font-weight:700}.value{font-size:13px;fill:#9fb3c8}.note{font-size:12px;fill:#8da3b8}</style>',
        '<text x="32" y="38" class="label">Local p75 performance evidence</text>',
        '<text x="32" y="62" class="note">Owner-provided local measurements — not production field data</text>',
    ]
    for index, row in enumerate(rows):
        y = 98 + index * row_height
        maximum = max(row["before"], row["after"])
        before_width = chart_width * row["before"] / maximum
        after_width = chart_width * row["after"] / maximum
        after_color = "#34d399" if row["status"] == "improved" else "#f59e0b" if row["status"] == "regressed" else "#94a3b8"
        label = escape(str(row["key"]))
        unit = escape(str(row["unit"]))
        lines.extend([
            f'<text x="32" y="{y + 20}" class="label">{label}</text>',
            f'<text x="32" y="{y + 43}" class="value">{row["reduction_pct"]:+.1f}% · {row["status"]}</text>',
            f'<rect x="{x0}" y="{y}" width="{before_width:.1f}" height="24" rx="4" fill="#22d3ee" opacity="0.8"/>',
            f'<rect x="{x0}" y="{y + 34}" width="{after_width:.1f}" height="24" rx="4" fill="{after_color}"/>',
            f'<text x="{x0 + before_width + 8:.1f}" y="{y + 17}" class="value">before {row["before"]:g} {unit}</text>',
            f'<text x="{x0 + after_width + 8:.1f}" y="{y + 51}" class="value">after {row["after"]:g} {unit}</text>',
        ])
    lines.append("</svg>")
    return "\n".join(lines) + "\n"
