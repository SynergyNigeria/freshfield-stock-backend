import logging

from django.conf import settings
from django.utils import formats, timezone
import resend


logger = logging.getLogger(__name__)


def _money(value):
    return f"${value:,.2f}"


def _decimal(value):
    return f"{value.normalize():f}"


def send_purchase_receipt_email(order):
    resend.api_key = settings.RESEND_API_KEY

    bought_date = formats.date_format(timezone.localdate(order.created_at), "F j, Y")
    shares = _decimal(order.shares)
    price = _money(order.price_at_order)
    total = _money(order.total)

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f5f7f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#111827;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7f5;padding:32px 0;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:14px;border:1px solid #e5e7eb;overflow:hidden;">
          <tr>
            <td style="background:#06d001;padding:22px 32px;text-align:center;">
              <span style="font-size:20px;font-weight:800;color:#000;">Freshfield</span>
              <span style="font-size:13px;font-weight:600;color:rgba(0,0,0,0.6);margin-left:6px;">Stocks</span>
            </td>
          </tr>
          <tr>
            <td style="padding:32px;">
              <p style="margin:0 0 8px;font-size:22px;font-weight:800;color:#111827;">Purchase receipt</p>
              <p style="margin:0 0 24px;font-size:14px;color:#6b7280;line-height:1.5;">
                Hi {order.user.first_name or 'there'}, your stock purchase was completed successfully.
              </p>

              <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                <tr>
                  <td style="padding:12px 0;border-bottom:1px solid #eef2f0;color:#6b7280;font-size:13px;">Stock</td>
                  <td align="right" style="padding:12px 0;border-bottom:1px solid #eef2f0;color:#111827;font-size:13px;font-weight:700;">{order.stock.name} ({order.stock.ticker})</td>
                </tr>
                <tr>
                  <td style="padding:12px 0;border-bottom:1px solid #eef2f0;color:#6b7280;font-size:13px;">Shares</td>
                  <td align="right" style="padding:12px 0;border-bottom:1px solid #eef2f0;color:#111827;font-size:13px;font-weight:700;">{shares}</td>
                </tr>
                <tr>
                  <td style="padding:12px 0;border-bottom:1px solid #eef2f0;color:#6b7280;font-size:13px;">Price per share</td>
                  <td align="right" style="padding:12px 0;border-bottom:1px solid #eef2f0;color:#111827;font-size:13px;font-weight:700;">{price}</td>
                </tr>
                <tr>
                  <td style="padding:12px 0;border-bottom:1px solid #eef2f0;color:#6b7280;font-size:13px;">Total paid</td>
                  <td align="right" style="padding:12px 0;border-bottom:1px solid #eef2f0;color:#111827;font-size:13px;font-weight:800;">{total}</td>
                </tr>
                <tr>
                  <td style="padding:12px 0;color:#6b7280;font-size:13px;">Date bought</td>
                  <td align="right" style="padding:12px 0;color:#111827;font-size:13px;font-weight:700;">{bought_date}</td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [order.user.email],
            "subject": f"Purchase receipt: {order.stock.ticker}",
            "html": html,
        })
    except Exception as exc:
        logger.error("Purchase receipt email failed for order %s: %s", order.id, exc)
