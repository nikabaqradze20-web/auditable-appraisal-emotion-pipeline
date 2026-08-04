"""Run the public synthetic examples through Pass A and Pass B."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from emotion_pipeline.pipeline import run_pipeline  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/synthetic_segments.json"))
    parser.add_argument("--output", type=Path, default=Path("demo_output.json"))
    args = parser.parse_args()

    records = json.loads(args.input.read_text(encoding="utf-8"))
    results = [run_pipeline(record) for record in records]
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Processed {len(results)} synthetic segments; all audits passed.")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

