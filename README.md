# Archimed Backend
This is the backend for the Archimed application, built with Django. The backend provides API routes for managing bills, investors, and capital calls. The base currency for all transactions is USD, and Redis is used to handle exchange rates for converting non-USD amounts.

## API Routes

### Bills

- **GET /bills/**: Retrieve a list of all bills.
- **POST /bills/**: Create a new bill.
- **GET /bills/{id}/**: Retrieve a specific bill by ID.
- **PUT /bills/{id}/**: Update a specific bill by ID.
- **DELETE /bills/{id}/**: Delete a specific bill by ID.
- **POST /create_bill/**: Create a bill for an investor.

### Capital Calls

- **GET /capital_calls/**: Retrieve a list of all capital calls.
- **POST /capital_calls/**: Create a new capital call.
- **GET /capital_calls/{id}/**: Retrieve a specific capital call by ID.
- **PUT /capital_calls/{id}/**: Update a specific capital call by ID.
- **DELETE /capital_calls/{id}/**: Delete a specific capital call by ID.

### Investments

- **GET /investments/**: Retrieve a list of all investments.
- **POST /investments/**: Create a new investment.
- **GET /investments/{id}/**: Retrieve a specific investment by ID.
- **PUT /investments/{id}/**: Update a specific investment by ID.
- **DELETE /investments/{id}/**: Delete a specific investment by ID.

### Entities

- **GET /entities/**: Retrieve a list of all entities.
- **POST /entities/**: Create a new entity.
- **GET /entities/{id}/**: Retrieve a specific entity by ID.
- **PUT /entities/{id}/**: Update a specific entity by ID.
- **DELETE /entities/{id}/**: Delete a specific entity by ID.

## Models

### Bill

- **type**: Enum, type of the bill (membership, upfront fees, yearly fees)
- **capital_call_id**: String, reference to the Capital Call model
- **to_investor_id**: String, reference to the Investor model
- **currency**: String, currency of the bill
- **amount**: Float, amount of the bill
- **status**: Enum, status of the bill (created, pending, paid, overdue, cancelled)
- **date**: Date, date of the bill
- **due_date**: Date, due date of the bill
- **investment_id**: String, reference to the Investment model (optional)
- **fees_year**: Integer, year of the fees (if applicable)

### Investor

- **name**: String, name of the investor
- **type**: Enum, type of the entity (company, fund, investor)
- **address**: String, address of the investor
- **bank_account_currency**: String, currency of the bank account
- **bank_account_number**: String, number of the bank account
- **bank_account_type**: Enum, type of the bank account (IBAN, SWIFT)
- **contact_person**: String, contact person for the investor
- **contact_person_email**: String, email of the contact person
- **contact_person_phone**: String, phone number of the contact person

### Capital Call

- **fund_entity_id**: String, reference to the Fund entity
- **investor_entities**: List of Strings, references to the Investor entities
- **date**: Date, date of the capital call
- **purpose**: String, purpose of the capital call
- **status**: Enum, status of the capital call (validated, sent, paid, overdue)
- **currency**: String, currency of the capital call
- **payment_method**: String, payment method for the capital call
- **due_date**: Date, due date of the capital call
- **bills**: List of Strings, references to the Bill models

### Investment

- **amount**: Float, amount of the investment
- **investor_id**: String, reference to the Investor model
- **duration**: Integer, duration of the investment in months
- **date**: Date, date of the investment

## Frontend Features

The frontend allows users to group and sort bills by custom criteria such as amount, capital call, and investor. This provides flexibility in managing and viewing financial data according to user preferences. Additionally, the frontend supports the creation, deletion, and viewing of bills, capital calls, entities, and investments in a user-friendly interface.
See github repository url [here](https://github.com/KossaiSbai/archimed-frontend)

## Assumptions

- The base currency for all transactions is USD.
- Redis is used to handle exchange rates for converting non-USD amounts.
- The exchange rates are extracted from the OpenExchange API and stored in Redis (see REDIS_URL environment variable). These rates are in the format USD/<currency>.

## Setup

1. Clone the repository.
2. Install the required dependencies.
3. Set up the Redis server for handling exchange rates.
4. Run the Django development server.

```bash
git clone <repository-url>
cd archimed-backend
pip install -r requirements.txt
python manage.py runserver
```


## Environment Variables

The application requires the following environment variables to be set in a `.env` file:

- **REDIS_URL**: The URL of the Redis server for handling exchange rates.
- **MONGODB_URL**: The URL of the MongoDB server for storing data.
- **REDIS_HOST**: The host of the Redis server.
- **REDIS_PORT**: The port of the Redis server.
- **REDIS_PASSWORD**: The password for the Redis server.
- **PERCENTAGE_FEE**: The percentage fee applied to transactions.

Ensure that these variables are populated accordingly in the `.env` file before running the application.

```plaintext
REDIS_URL=redis://default:your_redis_password@your_redis_host:your_redis_port
MONGODB_URL=mongodb://localhost:27017/
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_PASSWORD=your_redis_password
PERCENTAGE_FEE=0.02
```

## Overdue Bill Job

The backend includes a Celery task that marks overdue bills. This task is defined in the [tasks.py](#file:tasks.py-context) file and is scheduled to run periodically.

### Task Definition

The task `mark_overdue_invoices` connects to the MongoDB database, retrieves all pending bills with a due date earlier than the current date, and updates their status to "overdue".

### Running the Task

To run the overdue bill job, follow these steps:

1. Ensure that Celery is installed and configured correctly in your Django project. The configuration can be found in the [celery.py](#file:celery.py-context) file.
2. Start the Celery worker by running the following command:

```bash
celery -A archimedapi worker --loglevel=info
```

3. Optionally, you can start the Celery beat scheduler to run the task periodically:

```bash
celery -A archimedapi beat --loglevel=info
```

This setup ensures that overdue bills are automatically marked as overdue without manual intervention.
>>>>>>> 02053fd (Archimed backend CRUD API)
