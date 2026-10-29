# Docs PR #626 — status

`music-assistant/music-assistant.io#626` is now **clean, mergeable and
approved**. The branch `docs/dlna-receiver` was rebased by merging the current
`upstream/beta`; the only conflict was the Plugins sidebar, resolved by keeping
both `AudioMuse-AI` and `DLNA Receiver` in alphabetical order.

Remaining action: a maintainer merges the upstream PR. AI policy forbids merging
or commenting in `music-assistant/*` directly.

## What changed

- **Target players** → **Connected players**.
- Documented that an empty selection exposes every playback-capable player.
- Documented the 1.3.0 reselection step for existing installs.
- Documented `bind_ip`, `http_port`, `network_mode: host`, UDP 1900 and the
  `8298+` port range.
- Documented that Pause is forwarded to the output player and requires
  `PAUSE` support.
- Removed any claim that the provider authenticates or needs credentials.
- Kept the SSRF note accurate: `http`/`https` only; loopback/link-local/
  multicast destinations are rejected; LAN addresses are allowed.

## Verify after merge

```bash
curl -sI -o /dev/null -w '%{http_code}\n' \
  https://www.music-assistant.io/plugins/dlna-receiver/
```

Expect `200`. The provider manifest already points at that URL.
