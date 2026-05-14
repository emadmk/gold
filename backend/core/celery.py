"""Celery entry-point."""
from __future__ import annotations

import os

from celery import Celery
from celery.signals import setup_logging, task_prerun, task_postrun, task_failure

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.dev")

app = Celery("keyhan")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@setup_logging.connect
def _setup_logging(**_kwargs: object) -> None:
    # structlog is bootstrapped by apps.audit.log
    from apps.audit.log import configure_logging

    configure_logging()


@task_prerun.connect
def _propagate_context(sender=None, task_id=None, task=None, args=None, kwargs=None, **_kw):  # type: ignore[no-untyped-def]
    """Bind correlation IDs from task headers into the structlog context."""
    from apps.audit.context import bind_celery_context

    bind_celery_context(task_id=task_id, task_name=getattr(task, "name", ""), headers=getattr(task, "request", None))


@task_postrun.connect
def _clear_context(**_kwargs: object) -> None:
    from apps.audit.context import clear_context

    clear_context()


@task_failure.connect
def _failed(sender=None, task_id=None, exception=None, **_kw):  # type: ignore[no-untyped-def]
    from apps.audit.emit import emit_event

    emit_event(
        "system.celery.task.failed",
        category="system",
        severity="error",
        outcome="failure",
        data={"task": getattr(sender, "name", ""), "task_id": task_id, "error": repr(exception)},
    )


@app.task(bind=True)
def debug_task(self) -> str:  # pragma: no cover
    return f"ok:{self.request.id}"
