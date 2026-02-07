from datetime import datetime

def get_next_state(task):
    """
    Decide the next state of a task
    based on due date and current status.
    """

    if task["status"] == "COMPLETED":
        return "COMPLETED"

    today = datetime.utcnow()
    due = datetime.fromisoformat(task["due_date"])

    days_overdue = (today - due).days

    if days_overdue > 5:
        return "ESCALATED"
    elif days_overdue > 2:
        return "REMINDER_SENT"
    else:
        return task["status"]
