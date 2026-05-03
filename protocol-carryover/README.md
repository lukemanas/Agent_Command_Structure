# Protocol Carryover — Cleaned Set

Source documents from the Tank governance project, scrubbed for forward use as a protocol spec independent of the original substrate (fishtank/tank/attend daemon, Redis transport, Tailscale mesh).

## What was changed during the carryover scrub

1. **Substrate references stripped or generalized.** Specific implementation names (fishtank, tank, tk, attend, Redis, Tailscale, Headscale, WireGuard, AES-256-GCM, GitHub-as-tracker) replaced with protocol-level concepts (messaging substrate, persistent mailbox, network identity layer, ACL system, issue tracker). Where a concrete reference is preserved, it is marked as a "reference implementation example."

2. **"Working code" tense fixed.** PMF doc and others previously claimed Tank's architecture as built and running. Recast as designed reference architecture pending implementation. The adversarial-review document already validated this state.

3. **Risk-tier model unified to two tiers (low / high).** The 4-tier model (CRITICAL / HIGH / MODERATE / LOW) appearing in the older governance.md was superseded by the binary model in the MVP design. The 4-tier table is preserved as a "post-MVP cadence model" rather than load-bearing.

4. **Capability profile count unified to three (analyst / planner / actor).** The MVP design's "binary profiles are sufficient" line conflicted with its own three-profile table. The protocol spec assumes three; the binary statement was removed.

5. **OAP / IAP terminology aligned.** Premises v2 used "IAP" (NIMS-purist); every other doc used "OAP." Premises updated to OAP with a footnote noting the NIMS lineage.

6. **Stop hook P42 reworded.** Was: "Stop hooks halt affected agents immediately." Now framed as halt authority + redirect authority abstractly, since "stop hook" was a Claude Code runtime primitive.

7. **MVP design "Demobilization — Not Yet Designed" filled in.** The audit-event-schema.md doc (March 30) defines demob events; the demob protocol text was extracted and inlined.

8. **MVP design "Audit trail design lives in COP (TBD)" replaced.** The TBD pointed to the same later doc; a one-line forward reference was substituted.

9. **MVP design "TBD: depends on Tailscale/Redis decision" sections removed.** Both substrate options are gone; the sections were rewritten at protocol level (network identity layer + situational awareness store, both adopter-supplied).

10. **MVP Checklist replaced by Protocol Invariants list.** The original list mixed substrate tasks with protocol invariants; only the invariants survived.

## What was deliberately NOT changed

- **`adversarial-review-governance-vision-2026-03-28.md`** — Preserved as written. The substrate references serve the critique. A header note flags it as the as-of-March-28 stress test.
- **`ics-research.md`** — Already substrate-free (it's primary research on the ICS framework).
- **Footnote citations and external sources** — Unchanged across all docs.

## Reading order

1. `governance-protocol-plan.md` — what the protocol actually is (5 components)
2. `2026-03-17-governance-mvp-design.md` — the architecture
3. `audit-event-schema.md` — the audit format (one of the 5 components, fully written)
4. `governance-premises-v2.md` — formal premises (the why)
5. `ics-research.md` — the ICS source material
6. `governance.md` — short ICS-as-governance argument
7. `research-product-market-fit.md` — the case for the protocol existing
8. `research-compliance-mapping.md` — regulatory crosswalk
9. `adversarial-review-governance-vision-2026-03-28.md` — most recent stress test

## Known remaining work

- Compliance mapping doc has 100+ "Tank Mechanism" cells that were originally substrate-coupled. The scrub generalized them to "protocol mechanism" but a fresh pass against a real reference implementation will tighten coverage claims.
- Demobilization phase design was inlined from the audit schema's demob events but never had a dedicated design session — it deserves one before the spec is published.
- The COP architecture in MVP design was rewritten to be substrate-neutral but is the thinnest section of the spec.
