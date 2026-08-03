"""Hiring index calculation."""

from typing import Union


def calculate_hiring_index(
    job_count: int,
    employee_count: Union[int, float]
) -> float:
    """
    Calculate hiring index as ratio of open jobs to employees.
    
    Hiring Index = Open Jobs / Employees in Germany
    
    Args:
        job_count: Number of open job positions
        employee_count: Number of employees in Germany
        
    Returns:
        Hiring index as a float (jobs per employee)
    """
    if employee_count == 0:
        return 0.0
    
    return float(job_count) / float(employee_count)
