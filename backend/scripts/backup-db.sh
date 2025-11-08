#!/bin/bash
# Database backup script for TextLab
# Usage: ./backup-db.sh [backup-name]

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
POSTGRES_USER="${POSTGRES_USER:-textlab}"
POSTGRES_DB="${POSTGRES_DB:-textlab_db}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
BACKUP_NAME="${1:-backup-$(date +%Y%m%d-%H%M%S)}"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_NAME"

# Create backup
docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | \
  gzip > "$BACKUP_DIR/$BACKUP_NAME.sql.gz"

echo "Backup created: $BACKUP_DIR/$BACKUP_NAME.sql.gz"

# Remove backups older than 7 days
find "$BACKUP_DIR" -name "backup-*.sql.gz" -mtime +7 -delete

echo "Old backups cleaned up"

