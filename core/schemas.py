from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field

from core.constants import (
    ChaseTarget,
    ChaseChannel,
    ChasePriority,
    ChaseStatus,
    AdviceStage,
    ReviewStatus,
)



class AMLStatus(BaseModel):
    kyc_received: bool = False
    identity_verified: bool = False
    source_of_funds_verified: bool = False
    aml_completed: bool = False




class ClientReview(BaseModel):
    last_review_date: Optional[date] = None
    next_review_due: Optional[date] = None
    status: ReviewStatus = ReviewStatus.DUE


class Meeting(BaseModel):
    meeting_type: str  
    scheduled_date: Optional[datetime] = None
    completed: bool = False




class IngestedDoc(BaseModel):
    doc_id: str
    filename: str
    doc_type: str = "unknown"
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    summary: Optional[str] = None


class DataCompleteness(BaseModel):
    missing_fields: List[str] = []
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class ChaseItem(BaseModel):
    """
    This is the single object the state machine acts on.
    IMPORTANT: due_date is required for reminders/escalations.
    """
    item_name: str
    required_for: AdviceStage
    target: ChaseTarget

    status: ChaseStatus = ChaseStatus.NOT_STARTED
    priority: ChasePriority = ChasePriority.MEDIUM

    channel: ChaseChannel = ChaseChannel.EMAIL
    due_date: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    follow_up_count: int = 0

    
    reason: Optional[str] = None
    source_doc: Optional[str] = None
    extra: Dict[str, Any] = {}



class Pension(BaseModel):
    provider_name: str
    policy_number: Optional[str] = None

    
    valuation: Optional[float] = None
    valuation_date: Optional[date] = None
    exit_penalty: Optional[str] = None
    transfer_value: Optional[float] = None
    scheme_type: Optional[str] = None

    loa_required: bool = True
    loa_status: ChaseStatus = ChaseStatus.NOT_STARTED



class ClientProfile(BaseModel):
    client_id: str
    full_name: str
    date_of_birth: Optional[date] = None

    email: Optional[str] = None
    phone: Optional[str] = None

    annual_income: Optional[float] = None
    risk_profile: Optional[str] = None

    has_children: Optional[bool] = None
    children_ages: Optional[List[int]] = None

    isa_allowance_used: Optional[float] = None

    aml_status: AMLStatus = AMLStatus()
    review_status: ClientReview = ClientReview()

    meetings: List[Meeting] = []
    pensions: List[Pension] = []
    chase_items: List[ChaseItem] = []

    ingested_docs: List[IngestedDoc] = []
    completeness: DataCompleteness = DataCompleteness()

    current_stage: AdviceStage = AdviceStage.PRE_ADVICE
