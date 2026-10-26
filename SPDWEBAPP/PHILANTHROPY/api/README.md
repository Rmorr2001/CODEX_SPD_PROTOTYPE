# Service REST adapters

Mounted by CORE at `/api/v1/service/`; HTML routes stay in `PHILANTHROPY/urls.py`.
`serializers.py` defines contracts, `commands.py` adapts writes and review queries,
`reads.py` owns the academic-year snapshot, and `reports.py` delivers approved
history/statistics and the shared XLSX export. Shared validation and state changes
live in `../operations.py`. See the [domain README](../README.md) for scope,
permissions, unresolved policies and test commands.
