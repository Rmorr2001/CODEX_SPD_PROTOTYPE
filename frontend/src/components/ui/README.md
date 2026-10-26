# Member UI primitives

Shared presentation only: Button (CVA/Slot), Input, Card, MemberShell and Sheet.
Sheet uses the real Radix Dialog primitive following the shadcn composition
pattern: modal focus trap/return, title, Escape, portal and overlay. These are
reviewed local components, not a claim that a generator copied a complete theme.
The service domain owns its draft, dirty/busy dismissal policy and API calls;
identity owns navigation capabilities. Do not move business rules here.

Tailwind4 scans this folder and the migrated identity/service/decisions sources.
Preflight is omitted to protect existing domain/public CSS. Render under `.spd-ui`
for semantic crimson/charcoal/neutral tokens (portal Sheets opt in themselves).
Native controls retain accessible labels and visible focus states. No configuration
keys or credentials are required. `components.json` and `src/lib/utils.ts` define
the normal aliases/class helper.

Run `npm run build --prefix frontend`, `npm run format:check --prefix frontend`,
and `npm run test:e2e --prefix frontend` from the repository root. Drawer tests
live in service/test; member shell and domain transactions are covered by their
own domain tests. See the root experience plan for migration scope/evidence.
