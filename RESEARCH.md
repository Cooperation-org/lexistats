# Lexicon Resolution Research

## Event Structure

Jetstream events have this structure:
```json
{
  "did": "did:plc:...",
  "time_us": 1764713252370248,
  "kind": "commit",
  "commit": {
    "rev": "3m6zxdcjtfd2w",
    "operation": "create",
    "collection": "app.bsky.feed.like",
    "rkey": "3m6zxdcjkm32w",
    "record": {
      "$type": "app.bsky.feed.like",
      ...
    },
    "cid": "bafyrei..."
  }
}
```

Key fields:
- `commit.collection` - The NSID (Namespaced Identifier) of the lexicon
- `commit.record.$type` - Usually matches collection, confirms the schema
- `commit.operation` - "create", "update", or "delete"

## NSID Structure

NSIDs follow reverse-DNS format: `authority.name`
- `app.bsky.feed.post` → authority is `app.bsky` (maps to domain `bsky.app`)
- `fyi.unravel.frontpage.post` → authority is `fyi.unravel` (maps to domain `unravel.fyi`)

## Resolution Approaches Tested

### 1. GitHub Raw (Official Bluesky lexicons only) ✅

**URL Pattern:**
```
https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/{nsid.replace('.', '/')}.json
```

**Example:**
- `app.bsky.feed.post` → `lexicons/app/bsky/feed/post.json`

**Results:**
- Works perfectly for all `app.bsky.*`, `chat.bsky.*`, `com.atproto.*` lexicons
- Returns 404 for third-party lexicons

### 2. Lexidex (Bluesky's experimental index) ✅

**URL Pattern:**
```
https://lexidex.bsky.dev/lexicon/{nsid}
```

**Example:**
- `app.bsky.feed.post` → `https://lexidex.bsky.dev/lexicon/app.bsky.feed.post`

**Results:**
- Human-readable pages with schema documentation
- Only indexes lexicons that have been published to atproto repos
- Known domains: bsky.app, bsky.chat, atproto.com, ozone.tools, statusphere.xyz, etc.
- Many third-party lexicons NOT indexed (blue.flashes, works.catalog, etc.)

### 3. DNS TXT Lookup (Not implemented)

Per the [Lexicon Resolution RFC](https://github.com/bluesky-social/atproto/discussions/3074):
- Query `_lexicon.{authority-domain}` for DID
- Resolve DID to PDS
- Fetch schema from PDS

**Not practical for static site generation** - requires runtime DNS lookups.

## Observed Lexicons (30-second sample)

### Official (app.bsky)
All resolvable via GitHub and Lexidex:
- `app.bsky.feed.post` - Posts
- `app.bsky.feed.like` - Likes
- `app.bsky.feed.repost` - Reposts
- `app.bsky.feed.threadgate` - Thread access controls
- `app.bsky.feed.postgate` - Post interaction controls
- `app.bsky.graph.follow` - Follows
- `app.bsky.graph.block` - Blocks
- `app.bsky.graph.listitem` - List memberships
- `app.bsky.graph.verification` - Verification badges
- `app.bsky.actor.profile` - Profile records
- `app.bsky.actor.status` - Status updates

### Third-Party (Not in GitHub, some in Lexidex)
- `blue.flashes.feed.post` - Flashes posts
- `com.blatball.team` - Blatball teams
- `fm.teal.alpha.actor.status` - Teal music status
- `fm.teal.alpha.feed.play` - Teal plays
- `fyi.unravel.frontpage.post` - Frontpage/Unravel posts
- `jp.5leaf.sync.mastodon` - Mastodon sync
- `net.anisota.beta.game.log` - Game logs
- `net.anisota.beta.game.session` - Game sessions
- `place.stream.broadcast.origin` - Stream broadcasts
- `works.catalog.album` - Music albums
- `works.catalog.artist` - Music artists
- `works.catalog.track` - Music tracks
- `works.catalog.nowPlaying` - Now playing

## Recommended Link Strategy

1. **Official Bluesky lexicons** (`app.bsky.*`, `chat.bsky.*`, `com.atproto.*`):
   - Link to GitHub: `https://github.com/bluesky-social/atproto/blob/main/lexicons/{path}.json`
   - Or Lexidex: `https://lexidex.bsky.dev/lexicon/{nsid}`

2. **Lexidex-indexed third-party**:
   - Link to Lexidex if domain is known indexed

3. **Unknown third-party**:
   - Show authority domain as hint (e.g., `unravel.fyi`)
   - Mark as "schema unavailable" or link to authority homepage

## Authority → Domain Mapping

NSID authority segments map to domains by reversing:
- `app.bsky` → `bsky.app`
- `fyi.unravel` → `unravel.fyi`
- `works.catalog` → `catalog.works`
- `fm.teal` → `teal.fm`
