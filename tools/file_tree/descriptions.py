"""Purpose labels for the existing application, not file contents."""
domains={
 'HOME':'Public website: home, history, code of ethics, rush, and executive board.',
 'AUTHENTICATE':'Member accounts, profiles, roles, login, dashboard, and rosters.',
 'PARLEYPRO':'Chapter polls, voting, live results, and past polls.',
 'PHILANTHROPY':'Service hours, requests, approval, history, and exports.',
 'NEWMEMBER':'New-member marks, requests, approvals, dashboards, and exports.',
 'MISC':'Announcements and daylight-saving notices used across the app.',
 'SPDWEBAPP_CORE':'Django configuration and application composition: root routes, settings, ASGI, WSGI.',
 'railway_demo':'Our demo layer: runtime settings, persona entry, seed data, and tests.',
 'static':'Shared CSS and public images used by the existing site.'
}
rootdesc={
 'AGENTS.md':'Development expectations for this working branch: boundaries, size limits, documentation, and checks.',
 'README.md':'Project overview and setup, with a link to the isolated Railway demo instructions.',
 'Dockerfile':'Builds and starts the Railway demo: dependencies, static collection, migrations, fictional seeding, and Gunicorn.',
 'railway.json':'Railway build and deployment settings, including the home-page health check.',
 'requirements.txt':'The application’s original pinned Python dependencies.',
 'requirements-demo.txt':'Adds Gunicorn and WhiteNoise to the original dependency list for the demo.',
 '.dockerignore':'Excludes local/generated files and databases from the image build context.',
 '.gitignore':'Patterns for local/generated files that Git should not track.',
 'SPDWEBAPP/manage.py':'Django management-command entry point. Existing source explicitly says not to modify this file.',
 'SPDWEBAPP/secret_config.py':'Our inline-commented runtime configuration. Secret values are not included in this explorer.'
}
generic={
 'models.py':'Database models and their field/relationship definitions.',
 'views.py':'Request handlers connecting inputs, domain operations, and templates.',
 'views_functions.py':'Helpers used by this domain’s request handlers.',
 'urls.py':'URL patterns connecting paths to view functions.',
 'settings.py':'Configuration values and framework setup for this application layer.',
 'apps.py':'Django app registration.', 'admin.py':'Django admin registration and customization.',
 'forms.py':'Django forms and input contracts.', 'tests.py':'Tests for this area; inspect whether these are implemented or scaffold placeholders.',
 '__init__.py':'Python package marker.', 'wsgi.py':'WSGI application entry point.', 'asgi.py':'ASGI application entry point.'
}
