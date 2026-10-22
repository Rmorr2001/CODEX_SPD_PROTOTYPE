# PHILANTHROPY — service hours

Owns original service requests, approvals, edits and history. Legacy forms/views
and their minimum0.5 validation remain unchanged. Regression contracts and
unresolved policy designs live in `test/` and the root testing map.

`api.py` adds ACTIVE-only `/api/v1/service/?year=YYYY` via AUTHENTICATE's public
role boundary. It reuses `get_academic_year_dates` and
`get_user_events_and_total_hours`: July1–June30 inclusively, only caller records,
all own event statuses, approved-only totals, descending event-date order.
`get_available_academic_years` supplies current/past options; a valid explicit
selected year is added when absent. Input must be four ASCII digits and between
1900 and current calendar year+1; malformed/extreme input returns400. Responses
are no-store and whitelist event id/title/date/hours/status, total, date range,
options, own-history URL and PHIL_CHAIR+ACTIVE review capability.

There is no React submission/approval API, notes field or invented20/40-hour
requirement. The existing10-hour helper statistic is not redefined as policy.
**Preserved limitation:** the current model stores hours in an IntegerField;
fractional legacy input truncates on storage. This read adapter displays those
actual stored integers; it does not silently migrate or repair them. The original
request form remains the write boundary and no new input precision is promised.

`test/test_read_api.py` covers roles, own-record scope, year boundaries, approval
arithmetic/statuses, malformed years, fractional storage behavior and405 writes.
Run with standalone test settings. No new configuration keys or credentials.
