from django.db import models
from datetime import datetime

import math

def calculate_monthly_installment(principal, tenure_in_months, annual_interest_rate):
    # Calculates EMI using compound interest formula
    if annual_interest_rate == 0:
        return principal / tenure_in_months

    r = annual_interest_rate / 12 / 100
    n = tenure_in_months
    emi = principal * r * (1 + r)**n / ((1 + r)**n - 1)
    return round(emi, 2)

def calculate_credit_score(customer, loans_queryset):
    # Calculates credit score based on various factors

    sum_current_loans = loans_queryset.filter(end_date__gte=datetime.now().date()).aggregate(
        total=models.Sum('loan_amount')
    )['total'] or 0

    if sum_current_loans > customer.approved_limit:
        return 0  # Breaching approved limit results in score 0

    num_loans = loans_queryset.count()
    total_emis = loans_queryset.aggregate(total=models.Sum('tenure'))['total'] or 1
    total_onschedule_emis = loans_queryset.aggregate(
        total_on_time=models.Sum('emis_paid_on_time')
    )['total_on_time'] or 0
    paid_on_time_ratio = total_onschedule_emis / total_emis

    current_year = datetime.now().year
    current_year_loans = loans_queryset.filter(date_of_approval__year=current_year).count()
    approved_volume = loans_queryset.aggregate(total=models.Sum('loan_amount'))['total'] or 0

    score = 0
    score += min(30, paid_on_time_ratio * 30)  # Timely payment factor
    score += min(20, max(0, 20 - num_loans))  # Fewer loans means better score
    score += min(20, current_year_loans * 4)  # Recent activity adds value
    score += min(30, max(0, 30 - (float(approved_volume) / float(customer.approved_limit)) * 30))

    return int(min(100, score))
