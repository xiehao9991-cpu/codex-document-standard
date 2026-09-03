# Codex Document Standard

Private source of truth for Lan an's reusable Codex document-formatting skill.

## Repository layout

```text
codex-document-standard/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    └── style-standard.md
```

Repository maintenance files such as `README.md`, `AGENTS.md`, and `MEMORY.md` are not part of the skill workflow.

## Install on macOS

```bash
mkdir -p "$HOME/.codex/skills"
gh auth login
gh repo clone xiehao9991-cpu/codex-document-standard "$HOME/.codex/skills/codex-document-standard"
```

If Codex does not detect the skill automatically, restart the desktop app.

## Install on Windows

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
gh auth login
gh repo clone xiehao9991-cpu/codex-document-standard "$env:USERPROFILE\.codex\skills\codex-document-standard"
```

## Update a computer

Run this in Terminal or PowerShell:

```bash
git -C "$HOME/.codex/skills/codex-document-standard" pull --ff-only
```

On Windows PowerShell, use:

```powershell
git -C "$env:USERPROFILE\.codex\skills\codex-document-standard" pull --ff-only
```

Restart Codex if the updated behavior is not visible.

## Publish an update

Edit the skill in one clone, then run:

```bash
git add SKILL.md agents references
git diff --cached
git commit -m "Update document standard"
git push
```

Pull the change on the other computer. Avoid editing the same lines on both computers before syncing.

## Security

Keep this repository private. Never commit credentials, tokens, private keys, or `.env` files.
