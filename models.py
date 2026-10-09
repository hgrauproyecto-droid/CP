from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PaymentWebhook(BaseModel):
  source: str = Field(..., description="Origen del pago (ej. Stripe, PayPal, Banco)")
  external_reference: str = Field(..., description="ID único de la transacción original")
  amount: float = Field(..., gt=0, description="Monto monetario recibido")
  currency: str = Field(default="USD", description="Código de moneda ISO")
  raw_payload: Optional[Dict[str, Any]] = Field(
      default=None, description="Payload JSON crudo para auditoría forense"
  )


class AuditSubmission(BaseModel):
  transaction_id: str = Field(..., description="UUID de la transacción en base de datos")
  agent_verdict: str = Field(
      ..., description="Veredicto del agente: APROBADO o RECHAZADO"
  )
  audit_feedback: str = Field(..., description="Observaciones y dictamen del auditor")
