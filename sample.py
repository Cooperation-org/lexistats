#!/usr/bin/env python3
"""Sample ATProto Jetstream for lexicon usage statistics."""

import asyncio
import json
from collections import Counter
from datetime import datetime, timezone

import websockets


JETSTREAM_URL = "wss://jetstream2.us-east.bsky.network/subscribe"
SAMPLE_DURATION_SEC = 60


async def sample_jetstream():
    """Connect to Jetstream and sample events for SAMPLE_DURATION_SEC."""
    counts = Counter()
    total = 0
    start_time = asyncio.get_event_loop().time()

    try:
        async with websockets.connect(JETSTREAM_URL) as ws:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= SAMPLE_DURATION_SEC:
                    break

                try:
                    msg = await asyncio.wait_for(
                        ws.recv(),
                        timeout=SAMPLE_DURATION_SEC - elapsed + 1
                    )
                    event = json.loads(msg)

                    if "commit" in event and "collection" in event["commit"]:
                        collection = event["commit"]["collection"]
                        counts[collection] += 1
                        total += 1

                except asyncio.TimeoutError:
                    break

    except websockets.exceptions.ConnectionClosed:
        pass

    return counts, total


def main():
    counts, total = asyncio.run(sample_jetstream())

    ts = datetime.now(timezone.utc)
    filename = f"data/samples/sample_{ts.strftime('%Y%m%d_%H%M%S')}.json"

    result = {
        "ts": ts.isoformat(),
        "duration_sec": SAMPLE_DURATION_SEC,
        "total": total,
        "counts": dict(counts),
    }

    with open(filename, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Wrote {total} events to {filename}")


if __name__ == "__main__":
    main()
