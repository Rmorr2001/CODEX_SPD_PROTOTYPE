# Bundled frontend delivery

The root URL redirects to `/app/`; original home is `/legacy/`.
Owns the Django boundary beneath `/app/`; React source is in root `frontend/`.
No business rules or member records belong in this package.

`views.shell` serves only `FRONTEND_DIST_DIR/index.html`, regardless of the captured
React path. GET/HEAD are accepted; missing builds return a controlled 503 without
filesystem paths. HTML uses `Cache-Control: no-cache`. The fallback is mounted
only under `/app/`; unknown API paths and unrelated legacy URLs stay separate.

`web_settings.py` identifies the build directory from the non-secret
`FRONTEND_DIST_DIR` key. Local default: root `frontend/dist`; Docker: image-owned
`/app/frontend_dist`. Its `assets/` directory is collected under `app/assets`.
`assets.immutable_file_test` is passed to WhiteNoise as a callable and marks only
content-hashed Vite asset names immutable. HTML and unhashed assets do not match.
Never point this directory at uploads or a user-controlled request path.

`test/` exercises fixed-file selection, deep routes, missing bundles, method/route
boundaries and actual WhiteNoise cache headers using temporary synthetic files.

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py test SPDWEBAPP_CORE.frontend.test --noinput
```

See [frontend setup and browser checks](../../../frontend/README.md) and
[foundation delivery](../../../docs/migration/part-2-foundation.md). Changes to
build paths must update Vite base, Docker copy destinations and these contracts
in the same change. No runtime secret values are recorded here.
