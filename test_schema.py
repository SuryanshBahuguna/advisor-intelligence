from datetime import date
from core.schemas import ClientProfile, AMLStatus, ClientReview
from core.constants import AdviceStage, ReviewStatus

client = ClientProfile(
    client_id="C001",
    full_name="Sarah Mitchell",
    date_of_birth=date(1975, 3, 15),
    email="sarah@example.com",
    phone="1234567890",
    annual_income=85000,
    risk_profile="moderate",
    has_children=True,
    children_ages=[17],
    isa_allowance_used=5000,
    aml_status=AMLStatus(
        kyc_received=True,
        identity_verified=True,
        source_of_funds_verified=False,
        aml_completed=False,
    ),
    review_status=ClientReview(
        last_review_date=date(2023, 1, 10),
        next_review_due=date(2024, 1, 10),
        status=ReviewStatus.OVERDUE,
    ),
    current_stage=AdviceStage.PRE_ADVICE,
)

print(client)
