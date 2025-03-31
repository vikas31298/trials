from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from ..database import get_db
from ..schedule.ScheduleModel import Schedule

router = APIRouter(prefix='/resource', tags=["Resource Reports"])

@router.get("/utilization/{resource_id}")
def get_resource_utilization(
    resource_id: int,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    try:
        today = datetime.today().date()
        
        # Default start date = Current month - 3 months (1st of that month)
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = (today.replace(day=1) - timedelta(days=90)).replace(day=1)

        # Default end date = Current month + 3 months (end of that month)
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = (today.replace(day=1) + timedelta(days=90)).replace(day=1)

        # Fetch allocations within the given period
        allocations = db.query(Schedule).filter(
            Schedule.personid == resource_id,
            Schedule.start_date <= end_date,
            Schedule.end_date >= start_date
        ).all()

        if not allocations:
            raise HTTPException(status_code=404, detail="No resource utilization found for this period")

        utilization_report = {}

        for allocation in allocations:
            start = max(start_date, allocation.start_date)
            end = min(end_date, allocation.end_date)

            current = start
            while current <= end:
                month_key = current.strftime("%Y-%m")
                
                # Ensure entry exists in report
                if month_key not in utilization_report:
                    utilization_report[month_key] = 0

                # Calculate hours for this month
                next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
                last_day_of_month = (next_month - timedelta(days=1)).day

                # If allocation starts in the middle of a month
                first_day = max(1, current.day)
                last_day = min(last_day_of_month, (allocation.end_date if allocation.end_date < next_month else next_month - timedelta(days=1)).day)

                utilization_days = last_day - first_day + 1
                utilization_report[month_key] += utilization_days * allocation.dailyhours
                
                # Move to the next month
                current = next_month

        return {
            "status": 200,
            "message": "Resource utilization report generated successfully!",
            "data": utilization_report
        }
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
