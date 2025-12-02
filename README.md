# atstats

Lightweight ATProto lexicon usage sampler using GitHub Actions.

[![Sample Jetstream](../../actions/workflows/sample.yml/badge.svg)](../../actions/workflows/sample.yml)

**[View Live Dashboard](https://golda.github.io/atstats/)**

## What it does

Every 6 hours, samples the [Bluesky Jetstream](https://github.com/bluesky-social/jetstream) firehose for 60 seconds and records which lexicon collections are being used. Results are aggregated and published to GitHub Pages.

## Features

- Collection usage counts and percentages
- Historical trends over time
- Interactive charts showing events and top collections
- First/last seen timestamps per collection

## Data

- [stats.json](stats.json) - Raw aggregated data with history
- [Live dashboard](https://golda.github.io/atstats/) - Visual display

## Setup

To enable GitHub Pages, go to repo Settings > Pages and set source to "GitHub Actions".
