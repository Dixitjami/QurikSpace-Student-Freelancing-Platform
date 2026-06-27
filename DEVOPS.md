# DevOps Setup

This project includes Docker containerization and a GitHub Actions workflow for the Django freelancing platform.

## Docker

Build the image:

```bash
docker build -t django-freelancing-platform .
```

Run the container:

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY=change-this-secret-key \
  -e DEBUG=0 \
  -e ALLOWED_HOSTS=127.0.0.1,localhost \
  django-freelancing-platform
```

For local Docker Compose usage:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8000
```

## GitHub Actions

The workflow is stored at:

```text
.github/workflows/django-ci.yml
```

On every push or pull request to `main` or `master`, it:

1. Installs Python dependencies.
2. Runs `python manage.py check`.
3. Runs `python manage.py test`.
4. Builds the Docker image.

## Deployment Environment Variables

Use these variables on a production server or cloud platform:

```text
SECRET_KEY=your-production-secret-key
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@host:5432/dbname
```

If `DATABASE_URL` is not set, the app uses the local SQLite database.

For production, PostgreSQL is strongly recommended because container-local
SQLite data is not durable across replacements or horizontal scaling.

## Docker Hub Publishing

The GitHub Actions workflow publishes successful `main` branch builds as:

```text
dixit1114/student-freelancing-platform:latest
dixit1114/student-freelancing-platform:<commit-sha>
```

Create these GitHub repository secrets before pushing to `main`:

```text
DOCKERHUB_USERNAME=dixit1114
DOCKERHUB_TOKEN=<Docker Hub access token>
```

Use a Docker Hub access token, not your Docker Hub password.

## Production Checklist

1. Copy the variable names from `.env.example` into the hosting provider's
   secret/environment settings. Do not upload a production `.env` file.
2. Set `DEBUG=0`, a unique `SECRET_KEY`, production `ALLOWED_HOSTS`, and
   `CSRF_TRUSTED_ORIGINS` including the `https://` scheme.
3. Set `DATABASE_URL` to a persistent PostgreSQL database.
4. Keep HTTPS redirect and secure-cookie settings enabled.
5. Run migrations during release/startup before serving traffic.
