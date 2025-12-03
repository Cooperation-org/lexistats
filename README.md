# lexistats

Lightweight ATProto lexicon usage sampler using GitHub Actions.

[![Sample Jetstream](../../actions/workflows/sample.yml/badge.svg)](../../actions/workflows/sample.yml)

**[View Live Dashboard](https://cooperation-org.github.io/lexistats/)**

## What it does

Every 6 hours, samples the [Bluesky Jetstream](https://github.com/bluesky-social/jetstream) firehose for 60 seconds and records which lexicon collections are being used. Results are aggregated and published to GitHub Pages.

## Features

- Lexicon usage counts and percentages (events/sec for fair comparison)
- Historical trends over time
- Interactive charts showing network activity
- Links to lexicon schemas (GitHub for official, Lexidex for third-party)
- Grouped by authority domain

## Data

- [stats.json](stats.json) - Raw aggregated data with history
- [Live dashboard](https://cooperation-org.github.io/lexistats/) - Visual display

## Setup

To enable GitHub Pages, go to repo Settings > Pages and set source to "GitHub Actions".
