# IsoPois Backend

The IsoPois backend is built with FastAPI and provides a RESTful API for managing points of interest (POIs) and their associated geospatial data. It interacts with the database to perform CRUD operations and serves the frontend application.

## Development

### Environment

What the .env file should look like for the IsoPois backend:

```sh
# FastAPI prefix
PATH_PREFIX=
API_KEYS=xxxxx
# LASUR WS services
LASUR_WS_URL=https://lasur-ws-dev.epfl.ch
LASUR_WS_API_KEY=xxxxx
# France Travail
CLIENT_ID_ROME=
CLIENT_SECRET_ROME=
CLIENT_ID_JOBS=
CLIENT_SECRET_JOBS=
```
