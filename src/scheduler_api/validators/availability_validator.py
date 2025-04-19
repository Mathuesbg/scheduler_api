from http import HTTPStatus
from fastapi import HTTPException

def slot_is_valid(start, end, availabities):
    is_overlaps = any(
        availability.day == availabities.weekday
        and availability.start < end
        and availability.end > start
        for availability in availabities
    )
    
    if is_overlaps:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The time slot overlaps with an existing one',
        )
    
    is_exact_match = any(
        availability.day == availabities.weekday
        and availability.start == start
        and availability.end == end
        for availability in availabities
    )
    
    if is_exact_match:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The time slot already exists',
        )  
    
def timerange_is_valid(start, end):
    if start >= end:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Invalid time range!',
            )