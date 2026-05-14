# Runbook — Pricing feed stale

Triggered by `pricing.tick.stale` for any `source_key` more than 5
minutes after the last successful tick.

## 1. Check sources

```bash
docker compose logs --tail=200 celery_beat | grep pricing
docker compose exec backend python manage.py shell -c \
  "from apps.pricing.models import PriceTick; \
   import datetime; \
   print(list(PriceTick.objects.order_by('-captured_at')[:10].values('source_key','source','captured_at')))"
```

If TGJU is down, the fallback to brsapi.ir should already be active —
look for `pricing.source.failover` events in Kibana.

## 2. Manual probe

```bash
curl -fsS https://www.tgju.org/profile/geram18 | head -c 500
curl -fsS https://brsapi.ir/Api/Market/Gold_Currency.php | head
```

## 3. Mitigations

* **If both sources are down**: turn on the `read_only_prices` feature
  flag — the UI then shows "قیمت‌ها در دسترس نیست" and trade endpoints
  reject new quotes.
* **If TGJU changed its DOM**: patch `apps/pricing/crawler.py::TgjuCrawler._parse`,
  add another fallback selector, redeploy.

## 4. Aftermath

Add a snapshot of the failure response in the ADR / changelog so the
next outage is easier.
