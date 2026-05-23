from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EnquiryCreate(BaseModel):
    channel: str = Field(..., pattern="^(whatsapp|email|call)$", description="The channel of enquiry (whatsapp, email, call)")
    customer_name: str
    message: str

class EnquiryResponse(BaseModel):
    id: str
    job_id: str
    message: str

class FollowUpRequest(BaseModel):
    delay_minutes: int = Field(..., gt=0, description="Delay in minutes for follow-up")
    message_template: Optional[str] = None

class EscalateRequest(BaseModel):
    reason: str

class EnquiryHistoryEvent(BaseModel):
    event_type: str
    timestamp: datetime
    details: dict

class EnquiryHistoryResponse(BaseModel):
    enquiry_id: str
    status: str
    timeline: List[EnquiryHistoryEvent]

class EnquirySummary(BaseModel):
    id: str
    channel: str
    customer_name: str
    message: str
    status: str
    created_at: datetime
    sop_matched: Optional[str] = None
    suggested_response: Optional[str] = None
    escalation_reason: Optional[str] = None
    follow_up_time: Optional[datetime] = None
    follow_up_message: Optional[str] = None

class EnquiryMessage(BaseModel):
    sender: str
    text: str
    time: datetime

class EnquiryDetailResponse(BaseModel):
    id: str
    channel: str
    customer_name: str
    message: str
    status: str
    created_at: datetime
    sop_matched: Optional[str] = None
    suggested_response: Optional[str] = None
    escalation_reason: Optional[str] = None
    follow_up_time: Optional[datetime] = None
    follow_up_message: Optional[str] = None
    timeline: List[EnquiryHistoryEvent]
    messages: List[EnquiryMessage]
