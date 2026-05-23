import asyncio
from sqlalchemy.orm import Session
from database import Enquiry
from logger import logger

# Hardcoded SOPs
SOPS = {
    "booking": {
        "keywords": ["book", "reservation", "schedule", "appointment"],
        "response": "Thank you for reaching out! You can book an appointment directly through our online calendar at closira.com/book."
    },
    "pricing": {
        "keywords": ["price", "cost", "quote", "how much"],
        "response": "Our pricing varies based on your needs. Please visit closira.com/pricing for a detailed breakdown, or reply with your specific requirements."
    },
    "complaint": {
        "keywords": ["broken", "not working", "unhappy", "issue", "wrong", "complaint", "bad"],
        "response": "We are very sorry to hear you're experiencing issues. A team member will review this and get back to you shortly."
    },
    "after_hours": {
        "keywords": ["hours", "open", "close", "time"],
        "response": "Our business hours are Monday-Friday, 9 AM to 5 PM. If you are reaching out outside these hours, we will respond on the next business day."
    }
}

async def process_enquiry_task(enquiry_id: str, message: str, db: Session):
    """
    Simulates processing of an inbound enquiry.
    Matches against SOPs, updates DB, and logs events.
    """
    logger.info("Task processing started", extra={"enquiry_id": enquiry_id})
    
    # Simulate some processing delay
    await asyncio.sleep(2)
    
    matched_sop = None
    suggested_response = None
    
    message_lower = message.lower()
    
    for sop_name, sop_data in SOPS.items():
        if any(keyword in message_lower for keyword in sop_data["keywords"]):
            matched_sop = sop_name
            suggested_response = sop_data["response"]
            break
            
    db_enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not db_enquiry:
        logger.error("Enquiry not found during task processing", extra={"enquiry_id": enquiry_id})
        return
        
    if matched_sop:
        db_enquiry.status = "qualified"
        db_enquiry.sop_matched = matched_sop
        db_enquiry.suggested_response = suggested_response
        logger.info("SOP matched", extra={"enquiry_id": enquiry_id, "sop": matched_sop})
    else:
        # No SOP matched -> Escalate
        db_enquiry.status = "escalated"
        db_enquiry.escalation_reason = "No SOP matched for the inbound message."
        logger.warning("Escalation triggered: No SOP match", extra={"enquiry_id": enquiry_id})
        
    db.commit()
    logger.info("Task processing completed", extra={"enquiry_id": enquiry_id, "final_status": db_enquiry.status})
