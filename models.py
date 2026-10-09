from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PaymentWebhook(BaseModel):
  source: str = Field(..., description="Origen del pago (ej. Stripe, Banco)")
  external_reference: str = Field(..., description="ID único de la transacción")
  amount: float = Field(..., gt=0, description="Monto del pago")
  currency: str = Field(default="USD", description="Moneda")
  raw_payload: Optional[Dict[str, Any]] = Field(
      default=None, description="Datos crudos"
  )


class AuditSubmission(BaseModel):
  transaction_id: str = Field(..., description="UUID de la transacción")
  agent_verdict: str = Field(..., description="APROBADO o RECHAZADO")
  audit_feedback: str = Field(..., description="Dictamen del agente")
