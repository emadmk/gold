#!/usr/bin/env bash
# Import Kibana saved objects (dashboards + index patterns + saved searches).
set -euo pipefail

KIBANA_URL="${KIBANA_URL:-http://kibana:5601}"

# Wait for Kibana
for i in $(seq 1 60); do
  if curl -sf "${KIBANA_URL}/api/status" >/dev/null; then break; fi
  sleep 2
done

curl -sS -XPOST "${KIBANA_URL}/api/saved_objects/_import?overwrite=true" \
  -H 'kbn-xsrf: true' \
  -F file=@"$(dirname "$0")/saved_objects/dashboards.ndjson"
echo "Kibana saved objects imported."
