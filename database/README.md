# 💾 Database service
This service hosts a MariaDB server to which the rest of the services connect to.
It also handles migrations automatically.

## Users
User credentials are handled internally and do not require additional configuration. For development purposes, here is
a summary of all existing database accounts:

| User       | Pass    | Privileges                |
|------------|---------|---------------------------|
| root       | (empty) | Superuser account         |
| appuser    | (empty) | Read/write for all tables |
| appuser_ro | (empty) | Read-only for all tables  |

## Management console
In case of needing to execute a query directly against the database outside the application, you can run the
following command to get a console:
```sh
docker compose exec database console [<optional-mysql-query>]
```

## Database migrations
Database schema migrations are run every time the service starts. Other services will wait for the database to finish
the migration process to maintain consistency and compatibility across the application.

Migrations are TypeScript files stored in the `migrations` directory whose filenames must comply with the following
naming convention:
```
YYYYMMDDHHII-a-name-in-dash-case.ts
```

Migrations can also be ran on demand with the following command:
```sh
docker compose exec database run-script migrate  # Inside Docker
yarn migrate                                     # Outside Docker
```
