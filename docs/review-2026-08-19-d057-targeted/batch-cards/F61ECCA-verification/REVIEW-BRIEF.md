# Independent review brief — F61ECCA verification card

You authored neither the f61ecca repairs nor this card. Prove the instrument
fails its bar if you can. Do not reward effort.

## Bar

For each of C4, C6a, C6b, C6c, C6d, R1:

1. A positive exploit control on a mutant that reopens the named hole.
2. An observing test that the freeze blocks / refuses / stays on Sentinel.
3. Behaviour, not a source-text check.
4. Credential-shaped values synthesised at run time, never in a tracked file.

If any item does not hold, assign **severity** (Critical / High / Medium / Low /
Info). R1's severity has never been adjudicated. T2 puts that with you.

## What you may not do

Relabel an A1 verdict. Demand a production change. Treat a HOLD inside an
overall FAIL as a repair. Sign D-055. Touch a frozen harness.

## Evidence

`EXPLOIT-CONTROL.md`, `f61ecca-verify.sh`, `logs/`, `RESULTS.md`, `C6d-PROBE.md`.
Read the output, not the exit status.
