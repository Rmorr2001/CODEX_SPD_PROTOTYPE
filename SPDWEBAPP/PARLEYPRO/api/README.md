# Poll REST adapters

Mounted by CORE at `/api/v1/polls/`; HTML routes stay in `PARLEYPRO/urls.py`.
`urls.py` maps routes, `serializers.py` defines JSON contracts, `reads.py` returns
snapshots, and `commands.py` translates requests to public domain operations.
See the [domain README](../README.md) for permissions, rules, failure behavior
and tests. Do not add a second implementation of voting rules in this package.
