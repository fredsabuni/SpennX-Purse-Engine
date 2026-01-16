# Docker Setup Guide

This guide will help you run the SpennX Dashboard API using Docker.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

## Quick Start

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update the `.env` file with your configuration:**
   ```bash
   # The default values work out of the box with Docker Compose
   DATABASE_URL=mysql+pymysql://spennx_user:spennx_password@db:3306/spennx_db
   API_HOST=0.0.0.0
   API_PORT=8000
   
   # MySQL Configuration
   MYSQL_ROOT_PASSWORD=rootpassword
   MYSQL_DATABASE=spennx_db
   MYSQL_USER=spennx_user
   MYSQL_PASSWORD=spennx_password
   MYSQL_PORT=3306
   ```

3. **Build and start the containers:**
   ```bash
   docker-compose up -d
   ```

4. **Check the logs:**
   ```bash
   docker-compose logs -f api
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MySQL: localhost:3306

## Docker Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (deletes database data)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f api

# Database only
docker-compose logs -f db
```

### Rebuild containers
```bash
docker-compose up -d --build
```

### Restart a service
```bash
docker-compose restart api
```

### Execute commands in container
```bash
# Access API container shell
docker-compose exec api bash

# Access MySQL shell
docker-compose exec db mysql -u spennx_user -p
```

## Architecture

The Docker setup includes:

- **API Service**: FastAPI application running on port 8000
- **Database Service**: MySQL 8.0 running on port 3306
- **Network**: Private network for service communication
- **Volume**: Persistent storage for MySQL data

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | `mysql+pymysql://spennx_user:spennx_password@db:3306/spennx_db` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `MYSQL_ROOT_PASSWORD` | MySQL root password | `rootpassword` |
| `MYSQL_DATABASE` | Database name | `spennx_db` |
| `MYSQL_USER` | MySQL user | `spennx_user` |
| `MYSQL_PASSWORD` | MySQL password | `spennx_password` |
| `MYSQL_PORT` | MySQL port | `3306` |

## Troubleshooting

### Container won't start
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs api
```

### Database connection issues
```bash
# Check if database is ready
docker-compose exec db mysqladmin ping -h localhost

# Verify database exists
docker-compose exec db mysql -u root -p -e "SHOW DATABASES;"
```

### Reset everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Rebuild and start fresh
docker-compose up -d --build
```

## Production Considerations

For production deployment:

1. **Use secrets management** instead of `.env` files
2. **Update passwords** to strong, unique values
3. **Configure proper networking** and firewall rules
4. **Set up SSL/TLS** with a reverse proxy (nginx/traefik)
5. **Enable logging** to external services
6. **Configure backups** for the MySQL volume
7. **Use health checks** for monitoring
8. **Set resource limits** in docker-compose.yml

## Development Mode

The docker-compose.yml includes a volume mount for hot-reloading:

```yaml
volumes:
  - ./app:/app/app
```

This allows you to edit code locally and see changes reflected in the container without rebuilding.
