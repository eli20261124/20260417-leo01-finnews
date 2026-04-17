# Security Notes

This repository is intended to be safe for public GitHub hosting, but only if runtime credentials and personal data stay out of tracked files.

## Required Practices

1. Keep `.env` local only.
2. Put CI/CD credentials in GitHub Actions secrets, not in source files.
3. Use `.env.example` for placeholders only.
4. Do not commit files from `output/`.
5. Rotate any credential exposed in chat logs, terminal history, or screenshots.

## Current Secret Handling

- Runtime settings are loaded from environment variables in `main.py`.
- Scheduled automation reads secrets from GitHub Actions secrets in `.github/workflows/daily-report.yml`.
- Secret scanning runs in `.github/workflows/secret-scan.yml` on pushes, pull requests, and manual runs.

## Privacy Notes

- Public commit history can expose the author email address used for local commits.
- If you do not want your email visible on GitHub commits, enable GitHub's no-reply commit email before future commits.
- Rewriting existing public commit history is a separate cleanup task and should be done deliberately.

## Before Publishing Changes

1. Check `git status` for unexpected files.
2. Confirm `.env` is still ignored.
3. Confirm no personal email address or credential appears in tracked files.
4. If a secret was exposed, rotate it before pushing.