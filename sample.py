#!/usr/bin/env python3
"""Sample ATProto Jetstream for lexicon usage statistics.

Collects event counts AND unique DIDs per lexicon.
Saves to JSON (for git/GitHub Pages) and POSTs to API (for DB).
"""

import asyncio
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import websockets

try:
    import urllib.request
except ImportError:
    pass

JETSTREAM_URL = "wss://jetstream2.us-east.bsky.network/subscribe"
SAMPLE_DURATION_SEC = 60
DID_CAP_PER_NSID = 10_000  # Don't track more than this many unique DIDs per lexicon


async def sample_jetstream():
    """Connect to Jetstream and sample events for SAMPLE_DURATION_SEC."""
    counts = Counter()
    dids_per_nsid = defaultdict(set)
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

                        # Track unique DIDs (capped)
                        did = event.get("did")
                        if did and len(dids_per_nsid[collection]) < DID_CAP_PER_NSID:
                            dids_per_nsid[collection].add(did)

                except asyncio.TimeoutError:
                    break

    except websockets.exceptions.ConnectionClosed:
        pass

    return counts, total, dids_per_nsid


def post_to_api(result, dids_per_nsid):
    """POST sample data to the lexistats API."""
    api_url = os.environ.get("LEXISTATS_API_URL")
    api_key = os.environ.get("LEXISTATS_API_KEY")

    if not api_url or not api_key:
        print("LEXISTATS_API_URL or LEXISTATS_API_KEY not set, skipping API push")
        return

    # Convert DID sets to lists for JSON
    unique_dids = {}
    for nsid, did_set in dids_per_nsid.items():
        unique_dids[nsid] = list(did_set)

    payload = {
        "ts": result["ts"],
        "duration_sec": result["duration_sec"],
        "total": result["total"],
        "counts": result["counts"],
        "unique_dids": unique_dids,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{api_url}/api/v1/samples",
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
            print(f"API push OK: sample_id={body.get('sample_id')}, lexicons={body.get('lexicons')}")
    except Exception as e:
        print(f"API push failed: {e}", file=sys.stderr)


def main():
    counts, total, dids_per_nsid = asyncio.run(sample_jetstream())

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

    print(f"Wrote {total} events ({len(counts)} lexicons, {sum(len(d) for d in dids_per_nsid.values())} unique DIDs) to {filename}")

    # Push to API if configured
    post_to_api(result, dids_per_nsid)


if __name__ == "__main__":
    main()
