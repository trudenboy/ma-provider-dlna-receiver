# Docs PR #626 — rebase and update checklist

The upstream documentation PR is approved but currently has conflicts with
`beta`, so the manifest URL
`https://www.music-assistant.io/plugins/dlna-receiver/` returns 404.

A human must perform the upstream git operations; do not push to
`music-assistant/music-assistant.io` from an AI session.

## Rebase

```bash
git fetch upstream beta
git switch docs/dlna-receiver
git rebase upstream/beta
```

Resolve conflicts in:

- `astro.config.mjs` — keep the DLNA Receiver sidebar entry in the current
  Plugins group order.
- `src/content/docs/plugins/dlna-receiver.md` — update the settings section.

## Content updates for 1.3.0

- Replace **Target players** with **Connected players**.
- Document that an empty selection exposes every playback-capable player.
- Note the 1.3.0 config change: users reselect players once.
- Document `bind_ip`, `http_port`, `network_mode: host`, UDP 1900 and the
  `8298+` port range.
- Document that Pause happens in the sender and requires a pause-capable output
  player.
- Remove any claim that the provider authenticates or needs credentials.
- Keep the SSRF note accurate: `http`/`https` only; loopback/link-local/
  multicast destinations are rejected; LAN addresses are allowed.

## Verify

```bash
pnpm install
pnpm build
```

Open the deploy preview, check `/plugins/dlna-receiver/`, the sidebar entry and
all tables/callouts.

## After merge

```bash
curl -sI -o /dev/null -w '%{http_code}\n' \
  https://www.music-assistant.io/plugins/dlna-receiver/
```

Expect `200`. The manifest already points at that URL.
