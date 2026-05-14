"""Invoice PDF generation (weasyprint).

Renders a Persian, RTL-aware invoice template and stashes the bytes on
`Order.invoice_pdf`. Imported lazily so weasyprint's heavy native deps
don't block test envs that don't need it.
"""
from __future__ import annotations

from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Order


def render_html(order: Order) -> str:
    return render_to_string("invoices/order.html", {
        "order": order,
        "now": timezone.now(),
        "items": list(order.items.all()),
    })


def generate_invoice(order: Order) -> Order:
    """Render the invoice PDF and save it to `order.invoice_pdf`."""
    try:
        from weasyprint import HTML  # type: ignore[import-not-found]
    except Exception:
        return order
    html = render_html(order)
    pdf_bytes = HTML(string=html).write_pdf()
    order.invoice_pdf.save(f"{order.order_number}.pdf", ContentFile(pdf_bytes), save=True)
    return order
