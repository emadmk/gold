#!/usr/bin/env bash
# Apply ILM policies + index templates to a fresh Elasticsearch instance.
# Designed to be idempotent — re-run safely.
set -euo pipefail

ES_URL="${ES_URL:-http://elasticsearch:9200}"
ES_AUTH="${ES_USER:-elastic}:${ES_PASS:-}"

put_policy() {
  local name="$1" file="$2"
  echo "→ ILM policy: $name"
  curl -sS -u "$ES_AUTH" -H 'Content-Type: application/json' \
    -XPUT "${ES_URL}/_ilm/policy/${name}" --data-binary "@${file}" \
    | sed 's/^/   /'
}

here="$(dirname "$0")"
put_policy keyhan-domain   "$here/ilm/domain.json"
put_policy keyhan-security "$here/ilm/security.json"
put_policy keyhan-aml      "$here/ilm/aml.json"
put_policy keyhan-system   "$here/ilm/system.json"
put_policy keyhan-ux       "$here/ilm/ux.json"
put_policy keyhan-logs     "$here/ilm/logs.json"

put_template() {
  local name="$1" pattern="$2" policy="$3" alias="$4"
  echo "→ index template: $name"
  curl -sS -u "$ES_AUTH" -H 'Content-Type: application/json' \
    -XPUT "${ES_URL}/_index_template/${name}" --data-binary @- <<JSON
{
  "index_patterns": ["${pattern}"],
  "template": {
    "settings": {
      "index.lifecycle.name": "${policy}",
      "index.lifecycle.rollover_alias": "${alias}",
      "number_of_shards": 1,
      "number_of_replicas": 1
    },
    "mappings": {
      "properties": {
        "@timestamp":           { "type": "date" },
        "event.id":             { "type": "keyword" },
        "event.kind":           { "type": "keyword" },
        "event.category":       { "type": "keyword" },
        "event.severity":       { "type": "keyword" },
        "event.outcome":        { "type": "keyword" },
        "actor.id":             { "type": "keyword" },
        "actor.type":           { "type": "keyword" },
        "actor.ip":             { "type": "ip" },
        "target.id":            { "type": "keyword" },
        "target.type":          { "type": "keyword" },
        "correlation.request_id": { "type": "keyword" },
        "correlation.trace_id":   { "type": "keyword" },
        "state.machine":        { "type": "keyword" },
        "state.from":           { "type": "keyword" },
        "state.to":             { "type": "keyword" },
        "state.trigger":        { "type": "keyword" },
        "data":                 { "type": "object" }
      }
    }
  }
}
JSON
}

put_template keyhan-events-domain    'keyhan-events-domain-*'    keyhan-domain   keyhan-events-domain
put_template keyhan-events-security  'keyhan-events-security-*'  keyhan-security keyhan-events-security
put_template keyhan-events-aml       'keyhan-events-aml-*'       keyhan-aml      keyhan-events-aml
put_template keyhan-events-system    'keyhan-events-system-*'    keyhan-system   keyhan-events-system
put_template keyhan-events-ux        'keyhan-events-ux-*'        keyhan-ux       keyhan-events-ux
put_template keyhan-logs             'keyhan-logs-*'             keyhan-logs     keyhan-logs

echo "OK"
