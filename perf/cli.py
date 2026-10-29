import argparse
import json
from pathlib import Path
from .report import make_markdown, make_svg


def main() -> None:
    parser = argparse.ArgumentParser(description="Create report from owner-provided local p75 numbers")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--chart", type=Path, help="Optional accessible SVG output path")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = make_markdown(payload)
        chart = make_svg(payload) if args.chart else None
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    if args.chart and chart:
        args.chart.parent.mkdir(parents=True, exist_ok=True)
        args.chart.write_text(chart, encoding="utf-8")
    print(f"Report saved: {args.output}")


if __name__ == "__main__":
    main()
