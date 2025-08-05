<h1>Credit Approval System – Alemeno Assignment</h1>
<p >This project is built as a backend solution for a banking-style credit approval workflow system. It covers everything from customer registration, loan eligibility, approval decisions, to loan tracking – all powered by a REST API using Django & PostgreSQL.</p>

> Includes Excel data ingestion, Swagger docs, and Docker setup.
<h2>Challenge & What I Did ?</h2>
Problem Statement:
Given a dataset of customers and their loan history, build an API that supports:

Customer registration & loan creation

Eligibility check based on income & history

EMI calculation (Compound Interest)

Approve/Reject loans with reasons

Serve documentation via Swagger & ReDoc

My Solution:

Developed clean REST APIs with Django.

Injected Excel data for real testing scenarios.

Used PostgreSQL (Clever Cloud / NeonDB supported).

Setup Swagger/ReDoc at landing page.

Dockerized for ease of deployment.
 

<h2>Installation (Non-Docker)</h2>
1. Clone the repository - 

```
git clone https://github.com/saimahendra282/Alemeno_Assignment.git
cd Alemeno_Assignment
```
2. Create virtual environment & activate

```
python -m venv venv
source venv/bin/activate
# Windows: cd venv\Scripts\activate
```

3. Install requirements

```
pip install -r requirements.txt
```
4. rename  .env.sample file in root within:
```
SECRET_KEY=shhh_it_is_secret
DJANGO_DEBUG=True
# DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
SAI_DB=postgres://username:password@localhost:port_num/db_name
```
5.Apply Migrations
```
python manage.py makemigrations
python manage.py migrate
```
6. Inject Excel Data

```
python manage.py inject_data
```
7. Run the server

```
python manage.py runserver
```
<h2>Docker Setup (Production Ready)</h2>
1. Build the containers

```
docker-compose build
```
2.Start the services
```
docker-compose up
```
3.Inject Excel data inside the running container
```
docker-compose run web python manage.py inject_data
```

> App will be live at: http://localhost:8000/.
<h2>Tech Stack</h2>
Backend: Django, Django REST Framework

Database: PostgreSQL (via Clever Cloud / NeonDB)

Excel Parsing: openpyxl

API Docs: Swagger & ReDoc using drf-yasg

Deployment: Docker & Docker Compose

Frontend: Custom landing page with logo, buttons & layout
<h2>Project Structure</h2>

```
Alemeno_Assignment/
│
├── core/
├── templates/index.html        # Landing page       
├── credit_approval/            # Django project settings
├── customer_data.xlsx          # Input Excel
├── loan_data.xlsx              # Input Excel
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── ...

```

Anyway here is the demo video, here you can see every working api endpoint

https://github.com/user-attachments/assets/d828bfe0-6512-44b6-9986-b207f22de3a5

<h2>API Endpoints (Base URL: http://localhost:8000/api/)</h2>
1. Register Customer

POST /api/register

```
curl -X POST http://localhost:8000/api/register \
-H "Content-Type: application/json" \
-d '{"first_name":"John","last_name":"Doe","age":30,"monthly_income":80000,"phone_number":"9876543210"}'
```
2. Check Loan Eligibility

POST /api/check-eligibility

```
curl -X POST http://localhost:8000/api/check-eligibility \
-H "Content-Type: application/json" \
-d '{"customer_id":1,"loan_amount":200000,"interest_rate":12,"tenure":24}'
```
3. Create Loan

POST /api/create-loan
```
curl -X POST http://localhost:8000/api/create-loan \
-H "Content-Type: application/json" \
-d '{"customer_id":1,"loan_amount":150000,"interest_rate":14,"tenure":12}'
```
4. View Loan by ID

GET /api/view-loan/<loan_id>
```
curl http://localhost:8000/api/view-loan/4725
```
5. View All Loans by Customer
GET /api/view-loans/<customer_id>
```
curl http://localhost:8000/api/view-loans/1
```
