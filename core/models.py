from django.db import models

class Customer(models.Model):
    customer_id = models.CharField(max_length=20, primary_key=True)  # Unique customer identifier
    first_name = models.CharField(max_length=50)                     # Customer's first name
    last_name = models.CharField(max_length=50)                      # Customer's last name
    age = models.IntegerField(null=True, blank=True)                 # Optional age field
    phone_number = models.CharField(max_length=20)                   # Customer contact number
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)  # Salary before deductions
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)  # Loan limit approved for the customer

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")  # Link to customer
    loan_id = models.CharField(max_length=20, primary_key=True)                             # Unique loan identifier
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)                      # Total loan amount
    tenure = models.IntegerField()                                                          # Loan duration in months
    interest_rate = models.FloatField()                                                     # Annual interest rate
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)                  # EMI to be paid monthly
    emis_paid_on_time = models.IntegerField()                                               # Count of EMIs paid on time
    date_of_approval = models.DateField()                                                   # Date when loan was approved
    end_date = models.DateField()                                                           # Date when loan ends
