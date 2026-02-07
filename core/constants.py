from enum import Enum


class ChaseTarget(str, Enum):
    CLIENT = "client"
    PROVIDER = "provider"
    INVESTMENT_FIRM = "investment_firm"


class ChaseChannel(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    DASHBOARD = "dashboard" 


class ChasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ChaseStatus(str, Enum):
    
    NOT_STARTED = "not_started"
    REQUESTED = "requested"
    FOLLOW_UP_SENT = "follow_up_sent"
    ESCALATED = "escalated"
    RECEIVED = "received"
    COMPLETED = "completed" 


class AdviceStage(str, Enum):
    """
    Expanded stages so our chaser can be stage-aware.
    This matches the workflow discussion: pre-meeting pack → advice → suitability → implementation → reviews.
    """
    PRE_ADVICE = "pre_advice"                  
    MEETING_PACK_SIGNOFF = "meeting_pack_signoff"  
    ADVICE = "advice"                          
    SUITABILITY_FINAL = "suitability_final"     
    POST_ADVICE = "post_advice"                
    ANNUAL_REVIEW = "annual_review"


class ReviewStatus(str, Enum):
    DUE = "due"
    OVERDUE = "overdue"
    COMPLETED = "completed"
