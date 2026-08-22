# D-CLAIMS runbook

Instrument only. Not a HOLD.

Source worktree must have no tracked changes. Measure from a disposable clean clone:

```bash
src=$(mktemp -d)
git clone --local --no-hardlinks "$(git rev-parse --show-toplevel)" "$src"
python3 docs/review-2026-08-19-d057-targeted/batch-cards/D-CLAIMS-tests/d-claims.py \
  "$src" 1e7761be051422ad8091b203df375ddcfb7d1208
```

Variants via `D_CLAIMS_VARIANT` (`baseline`, `fix-d6`, `fix-all`, `break-s1`,
`break-s2-prefix`, `break-floors`, `break-bevents`, `break-d014`, `break-reason-split`,
`break-reason-quoted`, `break-reason-space`, `break-reason-comment`,
`break-reason-newline`, `break-reason-vt`, `break-reason-ff`, `break-reason-nbsp`,
`break-reason-ls`, `break-reason-ps`, `break-reason-bom`, `break-live-strike`,
`break-extra-tilde-open`, `break-extra-tilde-close`). Matrix via `D_CLAIMS_MATRIX`.
Pre-repair `baseline` is 0/14 REQUIRED, all CONTROL, exit 1. `D_CLAIMS_FOCUSED_COMPLETE`
is withheld until 14/14 REQUIRED and all CONTROL.
