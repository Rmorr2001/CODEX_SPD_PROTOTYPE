# PARLEYPRO — chapter decisions

Owns legacy Aye/Nay ballots, motion creation/closure and saved results. Original
views, helpers, forms and routes remain unchanged. The frozen case map and
regression designs/tests are in `test/`; unresolved legacy policy stays in the
root testing documentation.

`api.py` adds read-only `/api/v1/polls/`. It requires ACTIVE through the public
AUTHENTICATE/access.py role boundary. `can_manage` additionally requires EXEC;
this is conjunction, not either role. The newest open motion is selected by
start time, with PK tie-break. Current tallies use existing
`count_all_current_votes(Brother_votes.objects)`; closed motions use their stored
counts in descending end order. Null saved counts display as zero. Response
fields contain motion metadata and aggregate tallies only, never individual
votes/users. No-store, SessionAuthentication and JSON-only API defaults apply.

No ballot, start/end mutation or new voting rule is introduced. Known legacy
mutation behavior is not silently rewritten. React links to the existing forms.
`test/test_read_api.py` covers role gates, scope, current/closed selection/order,
zero/empty data, management conjunction, privacy and rejected ballot writes.
Run it with standalone testing settings. No new credentials/config keys exist.
