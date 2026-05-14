# Runbook — `SYSTEM_HALT`

When to use: a money invariant has been violated (see `SECURITY.md §8`),
suspected exploit in progress, or any other situation where you would
rather stop new financial writes than risk further loss.

## What `SYSTEM_HALT` does

It's a single Redis key (`feature_flag:system_halt`) consulted by every
money-mutating service. When set, those services raise `SystemHalted`
and refuse to commit. **Read operations remain available.**

## How to set it

```bash
# From any host that can reach Redis:
docker compose exec backend python - <<'PY'
from apps.security.feature_flags import set_flag
set_flag("system_halt", True, actor_id="oncall")
PY
```

Verify in Kibana → `event.kind:system.feature_flag.toggled`.

## How to clear it

```bash
docker compose exec backend python - <<'PY'
from apps.security.feature_flags import set_flag
set_flag("system_halt", False, actor_id="oncall")
PY
```

## Communication

* Update statuspage immediately (template `pages/SYSTEM_HALT.md`).
* Notify finance + compliance team via the on-call channel.
* Open a SEV-1 incident ticket (template `incident.md`).
