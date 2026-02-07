import re
from datetime import datetime, timedelta
from typing import Optional

PROVIDERS = [
    "aviva", "aj bell", "standard life", "legal & general", "scottish widows", "aia",
    "royal london", "vanguard", "fidelity", "quilter", "prudential", "zurich", "aegon"
]

REQUIRED_PRE_MEETING = {
    "personal_details": [
        "date of birth", "dob", "address", "postcode", "email", "phone",
        "national insurance", "ni number"
    ],
    "income_employment_tax": [
        "income", "salary", "employment", "employer", "self employed", "tax", "p60"
    ],
    "objectives_priorities": [
        "objective", "goal", "priority", "retire", "retirement", "education", "university"
    ],
    "risk_profile": [
        "risk", "capacity for loss", "attitude to risk", "volatility", "risk tolerance"
    ],
    "vulnerabilities": [
        "vulnerable", "health", "disability", "care", "dependant", "vulnerability"
    ],
}

REQUIRED_PENSIONS = {
    "current_valuation": [
        "valuation", "current value", "fund value", "plan value", "value £", "value:", "total value"
    ],
    "fund_breakdown": [
        "fund breakdown", "funds", "asset allocation", "allocation", "equity", "equities",
        "bond", "bonds", "cash", "default lifestyle", "investment strategy", "investment mix"
    ],
    "contribution_history": [
        "contribution", "contributions", "regular payment", "monthly", "employer contribution",
        "employee contribution", "salary sacrifice"
    ],
    "transfer_value": [
        "transfer value", "cetv", "cash equivalent", "transfer"
    ],
    "exit_penalties": [
        "exit penalty", "penalty", "early exit", "surrender charge", "market value reduction", "mvr"
    ],
    "transfer_restrictions": [
        "restriction", "restrictions", "scheme rules", "transfer out", "cannot transfer",
        "normal retirement age", "retirement age", "protected age", "lock in"
    ],
    "scheme_type": [
        "db", "dc", "defined benefit", "defined contribution", "sipp", "personal pension",
        "final salary", "career average"
    ],
    "guaranteed_benefits": [
        "guaranteed", "guarantee", "gar", "protected", "gmp", "death benefit",
        "spouse pension", "dependant pension", "lump sum", "benefits on death"
    ],
}

LOA_KEYWORDS = ["letter of authority", "loa", "authority", "consent"]
POLICY_KEYWORDS = ["policy number", "policy no", "plan number", "account number", "scheme reference", "member number"]

ISA_REMAINING_KEYWORDS = [
    "remaining this tax year", "allowance remaining", "unused allowance", "unutilised",
    "unutilized", "remaining allowance", "isa allowance remaining"
]

DATE_PATTERNS = [
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
    r"\b(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
]

MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

def find_any_date(text: str) -> Optional[str]:
    for pat in DATE_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

def parse_date_hint(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None

    s = date_str.strip()

    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", s)
    if m:
        d = int(m.group(1))
        mo = int(m.group(2))
        y = int(m.group(3))
        if y < 100:
            y += 2000
        try:
            return datetime(y, mo, d)
        except ValueError:
            return None

    m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3,9})[a-z]*\s+(\d{2,4})$", s)
    if m:
        d = int(m.group(1))
        mon_raw = m.group(2).lower()
        y = int(m.group(3))
        if y < 100:
            y += 2000
        mon = MONTHS.get(mon_raw[:4], MONTHS.get(mon_raw, None))
        if not mon:
            mon = MONTHS.get(mon_raw[:3], None)
        if not mon:
            return None
        try:
            return datetime(y, mon, d)
        except ValueError:
            return None

    return None

def guess_client_name(text: str) -> Optional[str]:
    patterns = [
        r"Client\s*Name\s*:\s*(.+)",
        r"Client\s*:\s*(.+)",
        r"Name\s*:\s*(.+)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            name = re.split(r"[\n\r|,]", name)[0].strip()
            if 3 <= len(name) <= 60:
                return name
    return None

def present(text: str, keywords) -> bool:
    t = text.lower()
    return any(k.lower() in t for k in keywords)

def extract_presence(text: str) -> dict:
    presence = {"pre_meeting": {}, "pensions": {}, "loa": False, "policy_number_present": False}

    for field, kws in REQUIRED_PRE_MEETING.items():
        presence["pre_meeting"][field] = present(text, kws)

    for field, kws in REQUIRED_PENSIONS.items():
        presence["pensions"][field] = present(text, kws)

    presence["loa"] = present(text, LOA_KEYWORDS)
    presence["policy_number_present"] = present(text, POLICY_KEYWORDS)

    t = text.lower()
    presence["mentions_pension"] = any(k in t for k in ["pension", "sipp", "drawdown", "defined benefit", "defined contribution"])
    presence["mentions_provider"] = any(p in t for p in PROVIDERS)
    presence["mentions_children"] = any(k in t for k in ["child", "children", "son", "daughter"])
    presence["mentions_education"] = any(k in t for k in ["education", "university", "school"])
    presence["mentions_isa"] = "isa" in t
    presence["isa_remaining_mentioned"] = present(text, ISA_REMAINING_KEYWORDS)

    return presence

def build_tasks(
    client_id: str,
    client_name: str,
    file_name: str,
    presence: dict,
    anchor_date: Optional[datetime],
) -> list:
    now = datetime.utcnow()
    base = anchor_date or now

    def due(days_from_base: int) -> str:
        return (base + timedelta(days=days_from_base)).date().isoformat()

    tasks = []

    for field, ok in presence["pre_meeting"].items():
        if not ok:
            tasks.append({
                "client_id": client_id,
                "client_name": client_name,
                "item_name": f"collect_{field}",
                "required_for": "pre_advice",
                "target": "client",
                "status": "NOT_STARTED",
                "priority": "high",
                "channel": "email",
                "due_date": due(2),
                "reason": f"Missing {field.replace('_',' ')} required before advice",
                "source_doc": file_name
            })

    for field, ok in presence["pensions"].items():
        if not ok:
            tasks.append({
                "client_id": client_id,
                "client_name": client_name,
                "item_name": f"pension_{field}",
                "required_for": "advice",
                "target": "provider",
                "status": "NOT_STARTED",
                "priority": "high",
                "channel": "email",
                "due_date": due(5),
                "reason": f"Missing pension detail: {field.replace('_',' ')} needed for suitability work",
                "source_doc": file_name
            })

    if presence["mentions_children"] and not presence["mentions_education"]:
        tasks.append({
            "client_id": client_id,
            "client_name": client_name,
            "item_name": "education_planning_check",
            "required_for": "pre_advice",
            "target": "advisor",
            "status": "NOT_STARTED",
            "priority": "medium",
            "channel": "dashboard",
            "due_date": due(7),
            "reason": "Children mentioned but no education planning captured",
            "source_doc": file_name
        })

    if presence["mentions_isa"]:
        if presence.get("isa_remaining_mentioned"):
            tasks.append({
                "client_id": client_id,
                "client_name": client_name,
                "item_name": "isa_allowance_opportunity",
                "required_for": "annual_review",
                "target": "advisor",
                "status": "NOT_STARTED",
                "priority": "low",
                "channel": "dashboard",
                "due_date": due(3),
                "reason": "ISA allowance appears to be available; proactive outreach opportunity",
                "source_doc": file_name
            })
        else:
            tasks.append({
                "client_id": client_id,
                "client_name": client_name,
                "item_name": "isa_allowance_missing_data",
                "required_for": "annual_review",
                "target": "client",
                "status": "NOT_STARTED",
                "priority": "low",
                "channel": "email",
                "due_date": due(10),
                "reason": "ISA mentioned but remaining/used allowance not captured",
                "source_doc": file_name
            })

    missing_pension_fields = sum(1 for v in presence["pensions"].values() if not v)

    if presence["mentions_pension"] and presence["mentions_provider"] and missing_pension_fields <= 3:
        if not presence["policy_number_present"]:
            tasks.append({
                "client_id": client_id,
                "client_name": client_name,
                "item_name": "policy_number_collection",
                "required_for": "meeting_pack_signoff",
                "target": "client",
                "status": "NOT_STARTED",
                "priority": "high",
                "channel": "email",
                "due_date": due(2),
                "reason": "Policy numbers become mandatory once LOA chasing begins",
                "source_doc": file_name
            })

        if not presence["loa"]:
            tasks.append({
                "client_id": client_id,
                "client_name": client_name,
                "item_name": "loa_pack_request",
                "required_for": "suitability_final",
                "target": "provider",
                "status": "NOT_STARTED",
                "priority": "high",
                "channel": "email",
                "due_date": due(7),
                "reason": "LOA required near final suitability stage; created only when pension data is largely complete",
                "source_doc": file_name
            })

    return tasks
