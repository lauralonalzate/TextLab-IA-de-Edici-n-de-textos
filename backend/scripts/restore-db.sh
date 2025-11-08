#!/bin/bash
# Database restore script for TextLab
# Usage: ./restore-db.sh <backup-file.sql.gz>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-file.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"
POSTGRES_USER="${POSTGRES_USER:-textlab}"
POSTGRES_DB="${POSTGRES_DB:-textlab_db}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Restoring from: $BACKUP_FILE"
echo "WARNING: This will overwrite the current database!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Restore backup
gunzip < "$BACKUP_FILE" | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U "$POSTGRES_USER" "$POSTGRES_DB"

echo "Database restored successfully"

