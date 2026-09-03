# Project Memory

## Durable context

- Created on 2026-09-03 as the cross-platform source of truth for `codex-document-standard`.
- The repository root is the skill directory so it can be cloned directly into a Codex user skills directory.
- The skill is instruction-only: it contains Markdown and YAML, with no compiled binaries or platform-specific scripts.
- The private remote repository is `https://github.com/xiehao9991-cpu/codex-document-standard` with `main` as its default branch.

## Decisions

- Use Git rather than repeated ZIP transfers so updates are versioned and reviewable.
- Clone the repository directly into each computer's Codex user skills directory so the installed skill is also the editable Git working copy.
- Use `git pull --ff-only` on secondary computers to avoid accidental merge commits.
- Keep tool or connector setup outside this repository; record only dependency locations, never secret values.

## Known constraints

- Native Word or DingTalk editing still depends on the corresponding Codex tools or connectors being installed and authorized on each computer.
- GitHub authentication must be configured independently on every computer.
