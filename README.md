# Untitled Project

## Components
- [💾 Database](./database)
- [🪐 Webserver](./webserver)

## Getting Started
The following environment variables are used to configure the app. The can be defined using a root `.env` file:

```py
PUID=1000                            # Process UID for containers with mounted volumes
PGID=1000                            # Process GID for containers with mounted volumes
TZ="Europe/Madrid"                   # Only for logs (database always stores timestamps in UTC)
DB_DATA_DIR="/path/to/db/data/dir"   # Path to database data directory (read-write)
```

## How to Run Locally
Typically, you want to start the app on development with this command:
```
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

This will map (**not copy**) the sources from [webserver](./webserver), so you can modify those components and changes
should appear in the containers.

To view the app, visit [http://localhost](http://localhost).
