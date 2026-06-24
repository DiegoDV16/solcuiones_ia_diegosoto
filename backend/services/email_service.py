import os
import smtplib
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / ".env")

SMTP_HOST = os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM") or SMTP_USER or os.getenv("GMAIL_REMITENTE", "noreply@pcfactory.cl")


def is_email_configured() -> bool:
    return bool(SMTP_USER and SMTP_PASSWORD)


def send_order_receipt(to_email: str, order: dict, items: list) -> bool:
    if not is_email_configured():
        logger.warning("SMTP no configurado. No se pudo enviar el correo.")
        return False

    items_html = "".join(
        f'<tr><td style="padding:8px;border-bottom:1px solid #eee">{sku}</td>'
        f'<td style="padding:8px;border-bottom:1px solid #eee;text-align:center">{qty}</td></tr>'
        for sku, qty in items
    )
    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f5f5f5">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:20px">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)">
<tr><td style="background:#1a1a2e;padding:20px 30px">
<span style="color:#e94560;font-size:24px;font-weight:bold">PC Factoría</span>
<span style="color:#888;font-size:13px;float:right">Comprobante</span>
</td></tr>
<tr><td style="padding:30px">
<h2 style="color:#1a1a2e;margin:0 0 20px">✅ ¡Compra confirmada!</h2>
<table width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;color:#333">
<tr><td style="padding:6px 0"><strong>Orden #:</strong> {order['id']}</td></tr>
<tr><td style="padding:6px 0"><strong>Sucursal:</strong> {order.get('branch_codigo', 'N/A')} — {order.get('branch_nombre', 'N/A')}</td></tr>
<tr><td style="padding:6px 0"><strong>Dirección:</strong> {order.get('direccion', 'No especificada')}</td></tr>
<tr><td style="padding:6px 0"><strong>Fecha:</strong> {order['fecha']}</td></tr>
<tr><td style="padding:6px 0"><strong>Total:</strong> <span style="color:#e94560;font-size:18px;font-weight:bold">${order['total']:,.0f} CLP</span></td></tr>
</table>
<h3 style="margin:20px 0 10px;color:#1a1a2e">Productos</h3>
<table width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;border-collapse:collapse">
<tr style="background:#f5f5f5"><th style="padding:8px;text-align:left">Producto</th><th style="padding:8px;text-align:center">Cantidad</th></tr>
{items_html}
</table>
<p style="margin-top:20px;padding:12px;background:#e8f5e9;border-radius:6px;color:#2e7d32;font-size:14px">
🎉 ¡Gracias por tu compra! Pasado mañana puedes pasar a retirar tu pedido por la sucursal seleccionada. Recuerda llevar tu cédula de identidad y el número de orden.
</p>
</td></tr>
<tr><td style="background:#fafafa;padding:15px 30px;border-top:1px solid #eee;text-align:center;font-size:12px;color:#888">
PC Factoría Chile — <a href="https://pcfactory.cl" style="color:#e94560">pcfactory.cl</a>
</td></tr>
</table>
</td></tr></table>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"PC Factoría - ¡Compra confirmada! Orden #{order['id']}"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(f"Orden #{order['id']} - Total: ${order['total']:,.0f} CLP", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Comprobante enviado a {to_email} para orden #{order['id']}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo a {to_email}: {e}")
        return False


def _build_html_body(body: str) -> str:
    content_html = body.replace("\n", "<br>")
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f5f5f5">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:20px">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)">
<tr><td style="background:#1a1a2e;padding:20px 30px;text-align:center">
<table width="100%"><tr>
<td style="text-align:left"><span style="color:#e94560;font-size:24px;font-weight:bold">PC Factoría</span></td>
<td style="text-align:right"><span style="color:#888;font-size:13px">TechAssist IA</span></td>
</tr></table>
</td></tr>
<tr><td style="padding:30px">
<div style="font-size:15px;line-height:1.6;color:#333">{content_html}</div>
</td></tr>
<tr><td style="background:#fafafa;padding:15px 30px;border-top:1px solid #eee;text-align:center;font-size:12px;color:#888">
¡Gracias por contactarnos!<br>
PC Factoría Chile — <a href="https://pcfactory.cl" style="color:#e94560">pcfactory.cl</a>
</td></tr>
</table>
</td></tr></table>
</body>
</html>"""


def send_text_email(to_email: str, subject: str, body: str) -> bool:
    if not is_email_configured():
        logger.warning("SMTP no configurado.")
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(_build_html_body(body), "html"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Correo enviado a {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo a {to_email}: {e}")
        return False
