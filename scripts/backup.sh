#!/usr/bin/env bash
# Encrypted daily backup of Postgres + MinIO to a remote bucket.
#
# Requires:
#   * env: PG_HOST PG_DB PG_USER PG_PASS BACKUP_AGE_RECIPIENT BACKUP_BUCKET S3_ENDPOINT
#   * tools: pg_dump, mc (MinIO client), age, curl
set -euo pipefail

NOW="$(date +%Y%m%d-%H%M%S)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 1) Dump Postgres
PGPASSWORD="$PG_PASS" pg_dump -h "$PG_HOST" -U "$PG_USER" -d "$PG_DB" -Fc \
  | age -r "$BACKUP_AGE_RECIPIENT" > "$TMP/pg-$NOW.dump.age"

# 2) Mirror MinIO private bucket (encrypted at rest by MinIO; we still re-encrypt
#    the metadata index for off-site)
mc alias set src "$S3_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" >/dev/null
mc mirror --overwrite src/keyhan-private "$TMP/minio-$NOW/"
tar -C "$TMP" -czf "$TMP/minio-$NOW.tar.gz" "minio-$NOW"
age -r "$BACKUP_AGE_RECIPIENT" < "$TMP/minio-$NOW.tar.gz" > "$TMP/minio-$NOW.tar.gz.age"

# 3) Upload to off-site bucket
mc alias set off "$BACKUP_BUCKET_ENDPOINT" "$BACKUP_BUCKET_KEY" "$BACKUP_BUCKET_SECRET" >/dev/null
mc cp "$TMP/pg-$NOW.dump.age" "off/$BACKUP_BUCKET/postgres/"
mc cp "$TMP/minio-$NOW.tar.gz.age" "off/$BACKUP_BUCKET/minio/"

echo "Backup $NOW uploaded."
