# Screen review gates

Each screen is built and reviewed separately against the parent
[screen plan](../screen-plan.md). An image is visual direction, not authority for
business rules, permissions, sample numbers, or functionality.

For each screen, record:

1. Screen ID, React route, spec link, concept image/panel and implementation files.
2. Builder's actual checks and desktop/mobile screenshot paths.
3. Independent reviewer findings: correctness, existing domain contracts,
   authorization, request/error states, accessibility, functional navigation,
   tests, and file-size limits. Identify concrete blockers versus optional polish.
4. Independent comparison agent's verdict after opening both the concept image
   and real rendered screenshots: **PASS**, **REVISE**, or **BLOCKED**. Assess
   red/black identity, hierarchy, composition, spacing, mobile layout, contrast,
   and relevant content. Record intentional adaptations to existing behavior.
5. Builder fixes and evidence for each required revision. Re-review changed
   behavior and recapture affected screenshots before closing findings.
6. Final decision and remaining limitations. A screenshot alone cannot prove
   authentication, authorization, persistence or a successful transaction.

Proceed to the next page only after required findings are resolved. Do not mark
unrun checks as passed. Local seeded checks are not live Railway checks. Keep
runtime data synthetic and credentials out of screenshots, source and logs.

Reports use `S01.md`, etc. Evidence lives under `../evidence/` or a clearly
identified reproducible local artifact path; reports must identify which applies.
