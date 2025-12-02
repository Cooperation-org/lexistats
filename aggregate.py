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
        duration = sample.get("duration_sec", 60)
        total_events += sample["total"]

        # Build history entry with events per second for comparability
        eps = sample["total"] / duration if duration > 0 else 0
        counts_per_sec = {k: v / duration for k, v in sample["counts"].items()} if duration > 0 else {}

        history.append({
            "ts": ts,
            "duration_sec": duration,
            "total": sample["total"],
            "eps": round(eps, 1),  # events per second
            "counts": sample["counts"],
            "counts_per_sec": {k: round(v, 2) for k, v in counts_per_sec.items()},
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
