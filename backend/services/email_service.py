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

    lines = [
        f"<h2>PC Factory - Comprobante de Compra</h2>",
        f"<p><strong>Orden #:</strong> {order['id']}</p>",
        f"<p><strong>Sucursal:</strong> {order.get('branch_codigo', 'N/A')} - {order.get('branch_nombre', 'N/A')}</p>",
        f"<p><strong>Dirección:</strong> {order.get('direccion', 'No especificada')}</p>",
        f"<p><strong>Fecha:</strong> {order['fecha']}</p>",
        f"<p><strong>Total:</strong> ${order['total']:,.0f} CLP</p>",
        "<h3>Productos:</h3>",
        "<ul>",
    ]
    for sku, qty in items:
        lines.append(f"<li>{sku} (x{qty})</li>")
    lines.append("</ul>")
    lines.append("<p>¡Gracias por tu compra! El pedido está listo para retiro.</p>")

    html_body = "\n".join(lines)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"PC Factory - Comprobante Orden #{order['id']}"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
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


def send_text_email(to_email: str, subject: str, body: str) -> bool:
    if not is_email_configured():
        logger.warning("SMTP no configurado.")
        return False
    html_body = body.replace("\n", "<br>")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(f"<pre>{html_body}</pre>", "html"))
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
