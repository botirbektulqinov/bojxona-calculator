from datetime import date, datetime

def today_date() -> date:
    return datetime.now().date()
