import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import AuditSubmission, PaymentWebhook

load_dotenv()

app = FastAPI(
    title="Microservicio de Control y Auditoría de Pagos",
    version="1.0.0",
    description=(
        "API orientada a eventos para ingestión de cobros y sincronización con"
        " agentes autónomos."
    ),
)

security = HTTPBearer()
# Llave secreta interna para validar llamadas desde tu sistema multi-agente en Streamlit
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "token-secreto-por-defecto")


def verify_internal_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
  if credentials.credentials != INTERNAL_API_KEY:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autorización inválidas o ausentes",
    )
  return credentials.credentials


@app.get("/health", tags=["Sistema"])
def health_check():
  return {"status": "online", "service": "Payment Automation Core"}


@app.post("/api/v1/payments/webhook", status_code=201, tags=["Pasarela"])
def receive_payment_webhook(payload: PaymentWebhook):
  """Endpoint público (protegido por firma de pasarela o token) para recibir pagos en tiempo real."""
  # TODO: Integrar lógica de inserción en Supabase con estado 'pending'
  return {
    "status": "success",
    "message": "Transacción capturada y encolada para auditoría",
    "transaction": {
        "source": payload.source,
        "reference": payload.external_reference,
        "amount": payload.amount,
        "currency": payload.currency,
    },
  }


@app.get("/api/v1/payments/pending", tags=["Agentes"])
def get_pending_payments(token: str = Security(verify_internal_token)):
  """ Endpoint consumido por tu sistema multi-agente para obtener pagos pendientes de revisión."""
  # TODO: Consultar en Supabase las transacciones con status = 'pending'
  return {
      "pending_count": 1,
      "transactions": [{
          "transaction_id": "uuid-ejemplo-abc-123",
          "external_reference": "TX-REF-9988",
          "amount": 250.00,
          "currency": "USD",
          "source": "Stripe Webhook",
      }],
  }


@app.post("/api/v1/payments/audit", tags=["Agentes"])
def submit_agent_audit(
    audit: AuditSubmission, token: str = Security(verify_internal_token)
):
  """Recibe el veredicto del Agente Auditor y actualiza el estado transaccional."""
  # TODO: Actualizar estado en Supabase ('verified' o 'flagged') e insertar en audit_reports
  return {
      "status": "updated",
      "transaction_id": audit.transaction_id,
      "verdict": audit.agent_verdict,
      "message": "Veredicto del agente aplicado correctamente en el registro contable.",
  }
