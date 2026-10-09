import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import AuditSubmission, PaymentWebhook
from supabase import Client, create_client

load_dotenv()

app = FastAPI(
    title="API de Conciliación de Pagos",
    version="1.0.0",
)

security = HTTPBearer()
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "secreto-por-defecto")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
  raise RuntimeError("Faltan las credenciales de Supabase.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
  if credentials.credentials != INTERNAL_API_KEY:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
    )
  return credentials.credentials


@app.get("/health")
def health():
  return {"status": "online"}


@app.post("/api/v1/payments/webhook", status_code=201)
def receive_payment(payload: PaymentWebhook):
  """Recibe y registra un nuevo pago pendiente de conciliación."""
  try:
    data = {
        "source": payload.source,
        "external_reference": payload.external_reference,
        "amount": payload.amount,
        "currency": payload.currency,
        "status": "pending",
        "raw_payload": payload.raw_payload,
    }
    res = supabase.table("transactions").insert(data).execute()
    return {"status": "success", "transaction": res.data[0] if res.data else data}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/payments/pending")
def get_pending(token: str = Security(verify_token)):
  """Lista los pagos pendientes para que los agentes los auditen."""
  try:
    res = (
        supabase.table("transactions")
        .select("*")
        .eq("status", "pending")
        .execute()
    )
    return {"pending_count": len(res.data), "transactions": res.data}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/payments/audit")
def submit_audit(audit: AuditSubmission, token: str = Security(verify_token)):
  """Actualiza el estado del pago según el veredicto del agente."""
  try:
    new_status = (
        "verified"
        if audit.agent_verdict.strip().upper().startswith("APROBADO")
        else "flagged"
    )

    supabase.table("transactions").update({"status": new_status}).eq(
        "id", audit.transaction_id
    ).execute()

    audit_data = {
        "transaction_id": audit.transaction_id,
        "agent_verdict": audit.agent_verdict,
        "audit_feedback": audit.audit_feedback,
    }
    supabase.table("audit_reports").insert(audit_data).execute()

    return {"status": "updated", "new_status": new_status}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
