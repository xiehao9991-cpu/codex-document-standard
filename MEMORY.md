# Project Memory

## Durable context

- Created on 2026-09-03 as the cross-platform source of truth for `codex-document-standard`.
- The repository root is the skill directory so it can be cloned directly into a Codex user skills directory.
- The skill is instruction-only: it contains Markdown and YAML, with no compiled binaries or platform-specific scripts.
- The intended remote repository is a private GitHub repository named `codex-document-standard` under `xiehao9991-cpu`.

## Decisions

- Use Git rather than repeated ZIP transfers so updates are versioned and reviewable.
- Use `git pull --ff-only` on secondary computers to avoid accidental merge commits.
- Keep tool or connector setup outside this repository; record only dependency locations, never secret values.

## Known constraints

- Native Word or DingTalk editing still depends on the corresponding Codex tools or connectors being installed and authorized on each computer.
- GitHub authentication must be configured independently on every computer.
