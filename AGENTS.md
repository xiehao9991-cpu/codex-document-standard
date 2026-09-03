# Repository Instructions

## Purpose

This repository is the private source of truth for Lan an's `codex-document-standard` Codex skill.

## Scope

- Keep the repository root directly installable as a Codex skill.
- Preserve `SKILL.md`, `agents/openai.yaml`, and files referenced from `SKILL.md`.
- Keep changes focused on document structure, visual standards, invocation metadata, and portability.
- Do not add runtime dependencies unless the skill genuinely requires executable behavior.

## Editing workflow

1. Update the smallest relevant file.
2. Keep all Markdown and YAML files UTF-8 encoded.
3. Check relative links after moving or renaming resources.
4. Validate the skill on both Windows and macOS when changing paths or platform-specific instructions.
5. Never commit credentials, tokens, private keys, `.env` files, or personal account data.

## Verification

- Confirm `SKILL.md` contains valid `name` and `description` frontmatter.
- Confirm every referenced file exists.
- Confirm `agents/openai.yaml` remains valid YAML.
- Run `git status --short` before committing and inspect the complete diff.
- Restart Codex if an updated skill is not detected automatically.
