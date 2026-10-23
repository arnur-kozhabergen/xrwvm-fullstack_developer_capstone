# fullstack_developer_capstone

Cars Dealership is a course demonstration application derived from IBM's
`ibm-developer-skills-network/xrwvm-fullstack_developer_capstone` starter.
It combines React, Django/SQLite, Express/MongoDB and Flask/NLTK VADER.

## Features

- Django server-side registration, login and logout; CSRF-protected writes.
- Dealership directory with state filtering and individual dealer reviews.
- CarMake/CarModel administration and idempotent loading of the supplied car data.
- Authenticated review submission; the author is taken from the server session.
- Node write access requires a private server-to-server token. Read endpoints
  intentionally expose only the supplied public synthetic course dataset.
- Flask sentiment inference uses the provided VADER lexicon, not invented labels.
- GitHub Actions checks Python/JavaScript lint, Django and React tests, real
  Mongo-backed API integration, sentiment inference and three Docker builds.

## Local configuration

Install Python dependencies from `server/requirements.txt` and the separate
`server/djangoapp/microservices/requirements.txt`. Install Node dependencies with
`npm ci` in `server/frontend` and `server/database`; build the frontend with
`npm run build`. Django uses `/djangoapp/` for JSON APIs and serves the built SPA.

Set `BACKEND_URL`, `SENTIMENT_URL`, and a private `BACKEND_WRITE_TOKEN` in the
Django process. Set the same write token in the Node process and a dedicated
`MONGO_URL` pointing to this application's Mongo database. No Mongo data is
deleted on startup: supplied records are inserted only when their IDs are absent.

Run `python manage.py migrate`, `python manage.py seed_cars`, and create a local
superuser with `python manage.py createsuperuser`. The course requires a GET
logout endpoint; this demo retains that explicit contract. Production logout
should use a CSRF-protected POST and deployment should add rate limiting.

Outside local development, set `DJANGO_DEBUG=0`, a unique private
`DJANGO_SECRET_KEY`, exact `DJANGO_ALLOWED_HOSTS` and HTTPS
`CSRF_TRUSTED_ORIGINS`. The app refuses production mode without a private key.
Secrets, databases, dependencies and built output are excluded from publication.
SQLite in a container is a single-instance, ephemeral course demonstration,
not a durable production storage architecture.

The Docker Compose file in `server/database` is a local HTTP demonstration.
It binds only `127.0.0.1:8000`, keeps Mongo and the internal services off host
ports, and uses a project-scoped volume. Export private `DJANGO_SECRET_KEY`
and `BACKEND_WRITE_TOKEN` values before running `docker compose up --build`
from that directory. Debug mode is enabled only for this loopback demo so
session cookies work over HTTP. Use the production settings above for any
public HTTPS deployment; do not publish the local Compose service directly.

## Skills Network deployment plan

`server/deployment.yaml` is a template, not a deployment-ready final manifest.
The currently observed SN runtime identity has not been confirmed to belong to
the learner. Do not deploy, push images, or select its registry namespace until
that identity is verified through the normal account interface and the exact
publication is authorized. After verification, set `SN_REGISTRY_NAMESPACE` and
render only that variable (for example, `envsubst '${SN_REGISTRY_NAMESPACE}'`).
The rendered manifest creates only the five named `fullstack-capstone-*`
resources in the verified lab namespace. Mongo and the API have internal
ClusterIP services; the web deployment is reached through the course's
documented `kubectl port-forward deployment/fullstack-capstone-web 8000:8000`
and the Skills Network toolbox's Launch Application for port 8000. A public
Ingress or LoadBalancer is not created. Before applying it, create the named
private Secret and runtime ConfigMap with the actual Code Engine sentiment URL,
the exact generated HTTPS proxy host, and that HTTPS origin. Never commit
private Secret values. Public deployment keeps Django debug disabled.

This Kubernetes demonstration intentionally has ephemeral Mongo and SQLite
storage. Restarting pods can lose demonstration accounts or newly added reviews.
It is unsuitable for durable or production data; use only synthetic course data.

## Verification

`python manage.py test djangoapp -v 2` tests authorization, CSRF, invalid and
duplicate registration, null/numeric payload rejection, service error contracts,
review author integrity and idempotent seed behavior. External services are
explicitly mocked in these Django unit/contract tests. Actual Mongo integration
runs separately with `node --test api.test.js` in the database directory. React
uses `npm test -- --watchAll=false`; sentiment uses `python -m unittest
test_sentiment -v`. Workflow output and runtime evidence must be checked after
execution; this README does not claim pending CI/deployment runs have succeeded.

## Demonstration identity and assets

The dealership and review records are the supplied course fixture. New test
accounts/reviews are synthetic demonstrations. About-page staff and contact
details are fictional and are labelled accordingly. `team-portraits.png` is an
AI-generated triptych created with the built-in imagegen tool for these fictional
profiles, not photographs of real staff. Other starter assets retain their
original provenance and repository licence. Codex assisted implementation and
testing under the user's stated AI-assistance accommodation. No Copilot work is
claimed.
