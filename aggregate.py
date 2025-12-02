#!/usr/bin/env python3
"""Aggregate all sample files into stats.json with historical trends."""

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def aggregate_samples():
    """Read all sample files and produce aggregated statistics."""
    samples_dir = Path("data/samples")
    sample_files = sorted(samples_dir.glob("sample_*.json"))

    if not sample_files:
        print("No sample files found")
        return

    total_events = 0
    collection_data = defaultdict(lambda: {"count": 0, "first_seen": None, "last_seen": None})

    # For historical trends: collect per-sample data sorted by time
    history = []

    for sample_file in sample_files:
        with open(sample_file) as f:
            sample = json.load(f)

        ts = sample["ts"]
        total_events += sample["total"]

        # Build history entry
        history.append({
            "ts": ts,
            "total": sample["total"],
            "counts": sample["counts"],
        })

        for collection, count in sample["counts"].items():
            data = collection_data[collection]
            data["count"] += count

            if data["first_seen"] is None or ts < data["first_seen"]:
                data["first_seen"] = ts
            if data["last_seen"] is None or ts > data["last_seen"]:
                data["last_seen"] = ts

    # Calculate percentages and sort by count
    collections = {}
    for collection, data in sorted(collection_data.items(), key=lambda x: -x[1]["count"]):
        collections[collection] = {
            "count": data["count"],
            "pct": round(data["count"] / total_events * 100, 2) if total_events > 0 else 0,
            "first_seen": data["first_seen"],
            "last_seen": data["last_seen"],
        }

    stats = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_samples": len(sample_files),
        "total_events": total_events,
        "collections": collections,
        "history": history,
    }

    with open("stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Aggregated {len(sample_files)} samples, {total_events} total events, {len(collections)} collections")


if __name__ == "__main__":
    aggregate_samples()
