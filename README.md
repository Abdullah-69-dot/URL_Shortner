# Distributed URL Shortener

A production-grade URL shortening service built with Django and Django REST Framework, featuring **Consistent Hashing** for database sharding and **Redis-based Caching**.

## Features
- **Scalable Architecture**: Database sharding using Consistent Hashing.
- **Consistent Hashing**: SHA-256 based ring with 150 virtual nodes per shard for balanced distribution.
- **Redis Caching**: Cache-aside strategy for lightning-fast URL retrieval.
- **Atomic Analytics**: Real-time access counting using Redis atomics.
- **Sharded Database Router**: Automated query routing based on short code hints.
- **Global Error Handling**: Middleware for consistent JSON error responses.
- **Comprehensive Logging**: Middleware for request/response tracking and shard routing logs.

## Tech Stack
- **Framework**: Django 5.x, Django REST Framework
- **Database**: PostgreSQL 15 (3 Shards), SQLite (Default/Admin)
- **Cache**: Redis 7
- **Infrasructure**: Docker, Docker Compose
- **Configuration**: Dotenv for environment management

## Getting Started

### Prerequisites
- Docker & Docker Compose

### Run with Docker
1. Clone the repository.
2. Initialize environment variables (example provided in `.env`).
3. Build and start the services:
   ```bash
   docker-compose up --build
   ```
4. Apply migrations to all shards:
   ```bash
   docker-compose exec web python manage.py migrate --database=shard_1
   docker-compose exec web python manage.py migrate --database=shard_2
   docker-compose exec web python manage.py migrate --database=shard_3
   ```

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/shorten` | Create a new short URL |
| **GET** | `/api/shorten/{shortCode}` | Retrieve long URL (increments Access Count) |
| **PUT** | `/api/shorten/{shortCode}` | Update a long URL |
| **DELETE** | `/api/shorten/{shortCode}` | Delete a short URL |
| **GET** | `/api/shorten/{shortCode}/stats` | Get usage statistics |
| **GET** | `/health/` | Service health check |

### Example Usage (cURL)
```bash
# Shorten a URL
curl -X POST http://localhost:8000/api/shorten \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.google.com"}'

# Get Stats
curl http://localhost:8000/api/shorten/{abc123}/stats
```

## Architecture Deep-Dive

### Consistent Hashing
We use a consistent hashing ring to distribute short codes across $N$ shards. By mapping each physical shard to 150 virtual nodes on the ring, we achieve an even distribution of keys. Adding a new shard requires remapping only $\approx 1/N$ of the total keys, minimizing data migration overhead.

### Caching Strategy
- **Read Path**: The application first checks Redis. On a MISS, it queries the responsible database shard, populates the cache, and returns the result.
- **Write/Update Path**: On updates or deletions, the cache is immediately invalidated to ensure data consistency (Cache-Aside).

### Atomic Counters
To handle high-concurrency access tracking, we use Redis `INCR` commands. These counts can be synchronized back to the database shards periodically to ensure persistence without bottlenecking the read path.

## Running Tests
```bash
python manage.py test
```
*(Or run separately: `python manage.py test core` and `python manage.py test urls_app`)*
