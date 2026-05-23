from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from database import init_db, get_db, Enquiry, SessionLocal
from schemas import (
    EnquiryCreate,
    EnquiryResponse,
    FollowUpRequest,
    EscalateRequest,
    EnquiryHistoryResponse,
    EnquiryDetailResponse,
    EnquirySummary,
)
from tasks import process_enquiry_task
from logger import logger
import uuid
import datetime

app = FastAPI(
    title="Closira Backend Intern Assignment",
    description="REST API backend simulating Closira’s customer enquiry-handling workflow.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    seed_demo_data()
    logger.info("Application startup and DB initialized.")


def seed_demo_data():
    db = SessionLocal()
    try:
        if db.query(Enquiry).count() > 0:
            return

        seed_enquiries = [
            Enquiry(
                channel="whatsapp",
                customer_name="Nina Patel",
                message="I want to book a demo for next Tuesday.",
                status="qualified",
                sop_matched="booking",
                suggested_response="Thank you for reaching out! You can book an appointment directly through our online calendar at closira.com/book.",
            ),
            Enquiry(
                channel="email",
                customer_name="Amina Shah",
                message="My product is broken and not working.",
                status="escalated",
                escalation_reason="Customer reported a product issue and needs human review.",
            ),
            Enquiry(
                channel="call",
                customer_name="Marcus Cole",
                message="How much does your plan cost?",
                status="qualified",
                sop_matched="pricing",
                suggested_response="Our pricing varies based on your needs. Please visit closira.com/pricing for a detailed breakdown, or reply with your specific requirements.",
            ),
            Enquiry(
                channel="whatsapp",
                customer_name="Olivia Reed",
                message="Can you help me with onboarding?",
                status="new",
                follow_up_time=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
                follow_up_message="Hi Olivia, I’m checking in on your onboarding setup and can help with the next steps.",
            ),
        ]

        db.add_all(seed_enquiries)
        db.commit()
        logger.info("Seed data initialized.")
    finally:
        db.close()


def build_timeline(enquiry: Enquiry):
    timeline = []

    timeline.append(
        {
            "event_type": "created",
            "timestamp": enquiry.created_at,
            "details": {"channel": enquiry.channel, "message": enquiry.message},
        }
    )

    if enquiry.sop_matched:
        timeline.append(
            {
                "event_type": "sop_matched",
                "timestamp": enquiry.created_at,
                "details": {
                    "sop": enquiry.sop_matched,
                    "suggested_response": enquiry.suggested_response,
                },
            }
        )

    if enquiry.status == "escalated":
        timeline.append(
            {
                "event_type": "escalated",
                "timestamp": enquiry.created_at,
                "details": {"reason": enquiry.escalation_reason},
            }
        )

    if enquiry.follow_up_time:
        timeline.append(
            {
                "event_type": "follow_up_scheduled",
                "timestamp": enquiry.follow_up_time,
                "details": {
                    "scheduled_for": enquiry.follow_up_time,
                    "template": enquiry.follow_up_message,
                },
            }
        )

    return timeline


def build_detail_messages(enquiry: Enquiry):
    messages = [
        {
            "sender": "customer",
            "text": enquiry.message,
            "time": enquiry.created_at,
        }
    ]

    if enquiry.sop_matched and enquiry.suggested_response:
        messages.append(
            {
                "sender": "system",
                "text": enquiry.suggested_response,
                "time": enquiry.created_at,
            }
        )

    if enquiry.status == "escalated" and enquiry.escalation_reason:
        messages.append(
            {
                "sender": "system",
                "text": f"Escalated: {enquiry.escalation_reason}",
                "time": enquiry.created_at,
            }
        )

    if enquiry.follow_up_time:
        messages.append(
            {
                "sender": "system",
                "text": enquiry.follow_up_message or "A follow-up has been scheduled.",
                "time": enquiry.follow_up_time,
            }
        )

    return messages


@app.post("/enquiry", response_model=EnquiryResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_enquiry(
    enquiry: EnquiryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create a new inbound customer enquiry.
    Returns a job ID immediately and processes in the background.
    """
    job_id = f"job_{uuid.uuid4().hex[:8]}"

    new_enquiry = Enquiry(
        channel=enquiry.channel,
        customer_name=enquiry.customer_name,
        message=enquiry.message,
        status="new",
    )
    db.add(new_enquiry)
    db.commit()
    db.refresh(new_enquiry)

    logger.info("Enquiry created", extra={"enquiry_id": new_enquiry.id, "job_id": job_id})

    background_tasks.add_task(process_enquiry_task, new_enquiry.id, new_enquiry.message, db)

    return EnquiryResponse(
        id=new_enquiry.id,
        job_id=job_id,
        message="Enquiry received and processing started.",
    )


@app.get("/enquiries", response_model=List[EnquirySummary])
def list_enquiries(db: Session = Depends(get_db)):
    enquiries = db.query(Enquiry).order_by(Enquiry.created_at.desc()).all()
    return enquiries


@app.get("/enquiry/{id}", response_model=EnquiryDetailResponse)
def get_enquiry(id: str, db: Session = Depends(get_db)):
    enquiry = db.query(Enquiry).filter(Enquiry.id == id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    return EnquiryDetailResponse(
        id=enquiry.id,
        channel=enquiry.channel,
        customer_name=enquiry.customer_name,
        message=enquiry.message,
        status=enquiry.status,
        created_at=enquiry.created_at,
        sop_matched=enquiry.sop_matched,
        suggested_response=enquiry.suggested_response,
        escalation_reason=enquiry.escalation_reason,
        follow_up_time=enquiry.follow_up_time,
        follow_up_message=enquiry.follow_up_message,
        timeline=build_timeline(enquiry),
        messages=build_detail_messages(enquiry),
    )


@app.post("/enquiry/{id}/follow-up")
def schedule_follow_up(id: str, request: FollowUpRequest, db: Session = Depends(get_db)):
    """
    Schedule a follow-up for an open enquiry.
    """
    enquiry = db.query(Enquiry).filter(Enquiry.id == id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    follow_up_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=request.delay_minutes)

    enquiry.follow_up_time = follow_up_time
    if request.message_template:
        enquiry.follow_up_message = request.message_template

    db.commit()
    logger.info("Follow-up scheduled", extra={"enquiry_id": id, "delay_minutes": request.delay_minutes})

    return {"message": "Follow-up scheduled", "follow_up_time": follow_up_time}


@app.post("/enquiry/{id}/escalate")
def escalate_enquiry(id: str, request: EscalateRequest, db: Session = Depends(get_db)):
    """
    Mark an enquiry as escalated to a human agent.
    """
    enquiry = db.query(Enquiry).filter(Enquiry.id == id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    enquiry.status = "escalated"
    enquiry.escalation_reason = request.reason
    db.commit()

    logger.info("Enquiry escalated manually", extra={"enquiry_id": id, "reason": request.reason})

    return {"message": "Enquiry escalated successfully", "enquiry_id": id}


@app.get("/enquiry/{id}/history", response_model=EnquiryHistoryResponse)
def get_enquiry_history(id: str, db: Session = Depends(get_db)):
    """
    Return the full conversation history and status timeline.
    """
    enquiry = db.query(Enquiry).filter(Enquiry.id == id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    return EnquiryHistoryResponse(
        enquiry_id=enquiry.id,
        status=enquiry.status,
        timeline=build_timeline(enquiry),
    )


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Return API status and database connectivity.
    """
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        logger.error("DB health check failed", extra={"error": str(e)})
        db_status = "failed"

    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
