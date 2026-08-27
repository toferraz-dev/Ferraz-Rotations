# Rotation rationale

The rotation YAMLs used to carry their reasoning inline — measurements,
rejected alternatives, bug post-mortems — and had grown to roughly half
comment by line count. That made the actual priority list hard to read.

The reasoning moved here, verbatim and unedited. The YAML kept a short comment
at each point and a pointer to its file.

| rotation | rationale |
|---|---|
| FerrazBalance.yaml | [Balance.md](Balance.md) |
| FerrazBalanceRaid.yaml | [BalanceRaid.md](BalanceRaid.md) |
| FerrazDestruction.yaml | [Destruction.md](Destruction.md) |
| FerrazFeral.yaml | [Feral.md](Feral.md) |
| FerrazFeralRaid.yaml | [FeralRaid.md](FeralRaid.md) |
| FerrazGuardianElune.yaml | [GuardianElune.md](GuardianElune.md) |
| FerrazRestoDruid.yaml | [RestoDruid.md](RestoDruid.md) |
| FerrazRestoDruidRaid.yaml | [RestoDruidRaid.md](RestoDruidRaid.md) |

## How to use it

Each entry is headed by the line it explains — a config key, a variable, a
list name, or the spell line itself — and gives the file and the line number
the comment sat at before the move.

**Before changing any line in a rotation, search this directory for it.** Most
of what is recorded here is something that was already tried and reverted, and
several of these bugs were fixed two, three and four times because the reason
was not written down anywhere.

Line numbers are from the pre-move files and drift as the YAMLs change. The
anchor text is what to search on, not the number.

## Related

- `.agents/SIMIA_EXPERT_PROMPT.md` — how Simia rotation YAML actually behaves
- `.agents/SIMC_METHODOLOGY.md` — how a change gets measured before it is kept
