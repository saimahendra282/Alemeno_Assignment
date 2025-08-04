from rest_framework import serializers
from .models import Customer, Loan

class CustomerRegisterSerializer(serializers.ModelSerializer):
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, source='monthly_salary')  # Maps to model field
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'phone_number', 'monthly_income']
    
    def create(self, validated_data):
        monthly_salary = validated_data['monthly_salary']
        approved_limit = round(36 * monthly_salary, -5)  # Calculates and rounds limit to nearest lakh
        validated_data['approved_limit'] = approved_limit
        return Customer.objects.create(**validated_data)

class CustomerResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()  # Combines first and last name
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, source='monthly_salary')
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()  # ID of the customer applying
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)  # Requested loan amount
    interest_rate = serializers.FloatField()  # Offered interest rate
    tenure = serializers.IntegerField(min_value=1)  # Loan period in months

class CheckEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()  # ID of the applicant
    approval = serializers.BooleanField()  # Eligibility result
    interest_rate = serializers.FloatField()  # Original interest rate
    corrected_interest_rate = serializers.FloatField()  # Adjusted if needed
    tenure = serializers.IntegerField()  # Tenure in months
    monthly_installment = serializers.DecimalField(max_digits=15, decimal_places=2)  # EMI value

class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()  # ID of loan applicant
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)  # Requested amount
    interest_rate = serializers.FloatField()  # Proposed interest rate
    tenure = serializers.IntegerField(min_value=1)  # Duration in months

class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)  # ID assigned to loan if created
    customer_id = serializers.IntegerField()  # Customer associated
    loan_approved = serializers.BooleanField()  # Was the loan granted
    message = serializers.CharField()  # Status message
    monthly_installment = serializers.DecimalField(max_digits=15, decimal_places=2)  # EMI if approved

class LoanDetailSerializer(serializers.ModelSerializer):
    monthly_installment = serializers.DecimalField(max_digits=15, decimal_places=2)  # EMI value
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']

class LoanWithCustomerSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()  # Unique loan identifier
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)  # Total loan amount
    interest_rate = serializers.FloatField()  # Rate of interest
    monthly_installment = serializers.DecimalField(max_digits=15, decimal_places=2)  # Monthly EMI
    tenure = serializers.IntegerField()  # Duration in months
    customer = serializers.SerializerMethodField()  # Nested customer details

    def get_customer(self, obj):
        c = obj.customer
        return {
            "id": c.customer_id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "phone_number": c.phone_number,
            "age": c.age,
        }
