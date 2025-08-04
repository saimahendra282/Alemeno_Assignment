# Imports for Django and DRF
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

def landing_page(request):
    return render(request, 'landing.html')

# Importing models and serializers
from .models import Customer, Loan
from .serializers import (
    CustomerRegisterSerializer, CustomerResponseSerializer,
    CheckEligibilitySerializer, CheckEligibilityResponseSerializer,
    CreateLoanSerializer, CreateLoanResponseSerializer,
    LoanWithCustomerSerializer, LoanDetailSerializer
)

# Utility functions for credit score and EMI calculation
from .utils import calculate_monthly_installment, calculate_credit_score

# Swagger decorators for documentation
from drf_yasg.utils import swagger_auto_schema

from decimal import Decimal


# ----------------------- Customer Registration API -----------------------
class RegisterCustomerAPIView(APIView):
    """
    API to register a new customer in the system.
    """

    @swagger_auto_schema(
        request_body=CustomerRegisterSerializer,
        responses={201: CustomerResponseSerializer}
    )
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------- Check Loan Eligibility API -----------------------
class CheckEligibilityAPIView(APIView):
    """
    API to check if a customer is eligible for a loan.
    Based on credit score, salary vs EMI burden, and interest rate slabs.
    """

    @swagger_auto_schema(
        request_body=CheckEligibilitySerializer,
        responses={201: CheckEligibilityResponseSerializer}
    )
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer = get_object_or_404(Customer, customer_id=data['customer_id'])
        loans = Loan.objects.filter(customer=customer)

        # Calculate credit score
        credit_score = calculate_credit_score(customer, loans)

        # Check active loans only
        active_loans = loans.filter(end_date__gte=datetime.now().date())

        # Calculate total EMIs currently being paid
        sum_emis = sum([float(loan.monthly_payment) for loan in active_loans]) or 0.0
        monthly_salary = float(customer.monthly_salary)

        # Reject loan if EMI burden is too high
        if sum_emis > monthly_salary * 0.5:
            approval = False
            corrected_interest_rate = float(data['interest_rate'])  # unchanged
        else:
            interest_rate = float(data['interest_rate'])
            approved = False
            corrected_interest_rate = interest_rate

            # Interest rate slab logic based on credit score
            if credit_score > 50:
                approved = True
            elif 30 < credit_score <= 50:
                approved = interest_rate >= 12.0
                corrected_interest_rate = 12.0 if not approved else interest_rate
            elif 10 < credit_score <= 30:
                approved = interest_rate >= 16.0
                corrected_interest_rate = 16.0 if not approved else interest_rate
            else:
                approved = False  # credit score too low

            # Ensure customer hasn't crossed approved loan limit
            sum_current_loans = loans.filter(end_date__gte=datetime.now().date()).aggregate(
                total=models.Sum('loan_amount')
            )['total'] or Decimal(0)

            if float(sum_current_loans) > float(customer.approved_limit):
                approved = False
                credit_score = 0

            approval = approved

        # Calculate EMI based on corrected interest rate
        emi = calculate_monthly_installment(
            float(data['loan_amount']),
            int(data['tenure']),
            corrected_interest_rate
        )

        response_data = {
            "customer_id": customer.customer_id,
            "approval": approval,
            "interest_rate": float(data['interest_rate']),
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": data['tenure'],
            "monthly_installment": emi
        }

        return Response(response_data, status=status.HTTP_200_OK)


# ----------------------- Create New Loan API -----------------------
class CreateLoanAPIView(APIView):
    """
    API to create a new loan for a customer if eligible.
    Checks EMI burden and interest rate slab based on credit score.
    """

    @swagger_auto_schema(
        request_body=CreateLoanSerializer,
        responses={201: CreateLoanResponseSerializer}
    )
    def post(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer = get_object_or_404(Customer, customer_id=data['customer_id'])
        loans = Loan.objects.filter(customer=customer)

        # Recheck eligibility logic
        credit_score = calculate_credit_score(customer, loans)
        active_loans = loans.filter(end_date__gte=datetime.now().date())

        sum_emis = sum([loan.monthly_payment for loan in active_loans]) or Decimal(0)
        monthly_salary = customer.monthly_salary

        # EMI burden check
        if sum_emis > monthly_salary * Decimal('0.5'):
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Total EMIs exceed 50% of monthly salary.",
                "monthly_installment": 0
            }, status=status.HTTP_400_BAD_REQUEST)

        # Interest rate check based on credit score
        interest_rate = data['interest_rate']
        approved = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approved = True
        elif 30 < credit_score <= 50:
            approved = interest_rate >= 12.0
            corrected_interest_rate = 12.0 if not approved else interest_rate
        elif 10 < credit_score <= 30:
            approved = interest_rate >= 16.0
            corrected_interest_rate = 16.0 if not approved else interest_rate
        else:
            approved = False

        # Approved limit check
        sum_current_loans = active_loans.aggregate(total=models.Sum('loan_amount'))['total'] or 0
        if sum_current_loans + data['loan_amount'] > customer.approved_limit:
            approved = False

        # Calculate EMI
        emi = calculate_monthly_installment(data['loan_amount'], data['tenure'], corrected_interest_rate)

        if approved:
            # Create loan in DB
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=data['loan_amount'],
                tenure=data['tenure'],
                interest_rate=corrected_interest_rate,
                monthly_payment=emi
            )
            response_data = {
                "loan_id": loan.loan_id,
                "customer_id": customer.customer_id,
                "loan_approved": True,
                "message": "Loan approved successfully.",
                "monthly_installment": emi
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            # Loan not approved
            response_data = {
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Loan not approved due to credit rating or limits.",
                "monthly_installment": emi
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


# ----------------------- View Loan By Loan ID API -----------------------
class ViewLoanAPIView(APIView):
    """
    API to fetch a specific loan with customer details by loan ID.
    """

    @swagger_auto_schema(
        responses={201: LoanDetailSerializer}
    )
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        loan_data = {
            "loan_id": loan.loan_id,
            "customer": {
                "id": loan.customer.customer_id,
                "first_name": loan.customer.first_name,
                "last_name": loan.customer.last_name,
                "phone_number": loan.customer.phone_number,
                "age": loan.customer.age,
            },
            "loan_amount": float(loan.loan_amount),
            "interest_rate": loan.interest_rate,
            "monthly_installment": float(loan.monthly_payment),
            "tenure": loan.tenure,
        }
        return Response(loan_data, status=status.HTTP_200_OK)


# ----------------------- View All Loans for a Customer API -----------------------
class ViewLoansByCustomerAPIView(APIView):
    """
    API to fetch all loans taken by a customer.
    Includes info like repayments left and EMI details.
    """

    @swagger_auto_schema(
        responses={201: LoanWithCustomerSerializer}
    )
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)

        results = []
        for loan in loans:
            # Estimate repayments left
            repayments_left = max(0, loan.tenure - loan.emis_paid_on_time)
            results.append({
                "loan_id": loan.loan_id,
                "loan_amount": float(loan.loan_amount),
                "interest_rate": loan.interest_rate,
                "monthly_installment": float(loan.monthly_payment),
                "repayments_left": repayments_left
            })

        return Response(results, status=status.HTTP_200_OK)
