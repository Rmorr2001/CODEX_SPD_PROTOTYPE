# HOME — public chapter presentation

Owns existing public homepage, history, recruitment, ethics and executive-board
pages. Existing views/URLs/templates remain authoritative for legacy behavior.
`api.py` adds public, read-only presentation contracts for the React public domain.

`GET /api/v1/public/home/` exposes only configured banner image and recruitment
interest URL, with nulls for missing/unsafe URLs. URLs must be local paths or
HTTP(S); executable/protocol-relative values are suppressed. No profiles, user
records, credentials or environment values are serialized. `BannerImage` and
`RushFormLink` keep their original singleton behavior. There is no new write API.

Tests and regression designs live in `test/`. Use standalone settings and run
`manage.py test HOME.test`; `test_public_api.py` covers the new public contract,
unsafe link handling, missing data and rejected mutations. React page notes live
in `frontend/src/domains/public/README.md`; screen references live in
`docs/design/screen-plan.md`. No new configuration keys are introduced.

`GET /api/v1/public/about/` returns actual distinct ACTIVE count and executive
cards in the existing `executive_board` position order. Multi-role members appear
once per position; missing positions are omitted. The card whitelist is name,
displayed position and safe image URL, without contact data. `api_about.py` owns
this presentation read model and `test/test_about_api.py` locks its boundaries.
