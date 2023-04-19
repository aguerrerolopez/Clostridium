# Untitled Project

## Components
- [💾 Database](./database)

## Getting Started
The following environment variables are used to configure the app. The can be defined using a root `.env` file:

```py
PUID=1000                            # Process UID for containers with mounted volumes
PGID=1000                            # Process GID for containers with mounted volumes
TZ="Europe/Madrid"                   # Only for logs (database always stores timestamps in UTC)
DB_DATA_DIR="/path/to/db/data/dir"   # Path to database data directory (read-write)
```
