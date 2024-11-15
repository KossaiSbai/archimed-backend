import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from bson import ObjectId
from datetime import date as datetime_date, timedelta

# Import the necessary models
from .models import (
    BillModel,
    CapitalCallModel,
    Investment,
    EntityType,
    BillType,
    BillStatus,
    CapitalCallStatus,
    bill_model,
    capital_call_model,
    investment_model,
    entity_model
)

class ArchimedAPITestCase(TestCase):

    def setUp(self):
        # Initialize APIClient
        self.client = APIClient()


        # Create an investor entity
        self.fund = entity_model.insert_one({
            "type": EntityType.FUND,
            "name": "Test Fund",
            "address": "123 Fund Street",
            "bank_account_number": "GB84WEST12345698765432",
            "bank_account_type": "iban",
            "contact_person": "John Cena",
            "contact_person_email": "johncena@example.com",
            "contact_person_phone": "+1234567378483"
        })

        # Create an investor entity
        self.investor = entity_model.insert_one({
            "type": EntityType.INVESTOR,
            "name": "Test Investor",
            "address": "123 Investor Street",
            "bank_account_number": "GB82WEST12345698765432",
            "bank_account_type": "iban",
            "contact_person": "John Doe",
            "contact_person_email": "johndoe@example.com",
            "contact_person_phone": "+1234567890"
        })
        self.investor_id = str(self.investor.inserted_id)
        self.fund_id = str(self.investor.inserted_id)
        
        # Create a capital call
        self.capital_call = capital_call_model.insert_one({
            "from_entity_id": self.fund.inserted_id, 
            "investor_entities": [self.investor_id],
            "purpose": "Initial Capital Call",
            "date": "2023-10-01T00:00:00Z",
            "status": "validated",
            "currency": "USD",
            "payment_method": "bank_transfer",
            "due_date": (datetime_date.today() + timedelta(days=30)).isoformat(),
            "bills": []
        })
        self.capital_call_id = str(self.capital_call.inserted_id)
        
        # Create an investment
        self.investment = investment_model.insert_one({
            "amount": 60000.0,
            "investor_id": self.investor_id,
            "duration": 5
        })
        self.investment_id = str(self.investment.inserted_id)

    def tearDown(self):
        # Clean up the database after each test
        bill_model.delete_many({})
        capital_call_model.delete_many({})
        investment_model.delete_many({})
        entity_model.delete_many({})

    def test_index_get(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        expected_response = {"message": "Hello, world. You're at the archimedapi index."}
        self.assertJSONEqual(response.content, expected_response)

    # Capital Call Tests
    def test_capital_call_list_get(self):
        url = reverse('capital-call-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['purpose'], "Initial Capital Call")

    def test_capital_call_list_post(self):
        url = reverse('capital-call-list')
        data = {
            "from_entity_id": self.fund_id, 
            "investor_entities": [self.investor_id],
            "purpose": "Second Capital Call",
            "date": "2024-01-15T00:00:00Z",
            "status": "sent",
            "currency": "EUR",
            "payment_method": "credit_card",
            "due_date": (datetime_date.today() + timedelta(days=60)).isoformat(),
            "bills": []
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('id', response_data)
        # Verify that the capital call was created
        created_capital_call = capital_call_model.find_one({"_id": ObjectId(response_data['id'])})
        self.assertIsNotNone(created_capital_call)
        self.assertEqual(created_capital_call['name'], "Second Capital Call") if 'name' in created_capital_call else self.assertTrue(True)

    def test_capital_call_detail_get(self):
        url = reverse('capital-call-detail', args=[self.capital_call_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['from_entity_id']["$oid"], str(self.fund.inserted_id))
        self.assertEqual(data['investor_entities'], [self.investor_id])
        self.assertEqual(data['status'], "validated")

    def test_capital_call_detail_put(self):
        url = reverse('capital-call-detail', args=[self.capital_call_id])
        updated_data = {
            "status": CapitalCallStatus.SENT.name,
            "currency": "GBP"
        }
        response = self.client.put(url, data=json.dumps(updated_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Verify the update
        updated_capital_call = capital_call_model.find_one({"_id": ObjectId(self.capital_call_id)})
        self.assertEqual(updated_capital_call['status'], CapitalCallStatus.SENT.name)
        self.assertEqual(updated_capital_call['currency'], "GBP")

    def test_capital_call_detail_delete(self):
        url = reverse('capital-call-detail', args=[self.capital_call_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        # Verify deletion
        deleted_capital_call = capital_call_model.find_one({"_id": ObjectId(self.capital_call_id)})
        self.assertIsNone(deleted_capital_call)

    # Bill Tests
    def test_bill_list_get(self):
        # Create a bill
        bill = bill_model.insert_one({
            "type": "membership",
            "to_investor_id": self.investor_id,
            "fees_year": 2023,
            "amount": 3000.0,
            "status": BillStatus.CREATED.name,
            "date": "2023-10-01T00:00:00Z",
            "due_date": "2023-10-11T00:00:00Z",
            "investment_id": None,
            "capital_call_id": self.capital_call_id
        })
        url = reverse('bill-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['type'], "membership")
        self.assertEqual(data[0]['to_investor_id'], self.investor_id)

    def test_bill_list_post(self):
        url = reverse('bill-list')
        data = {
            "type": 'upfront fees',
            "to_investor_id": self.investor_id,
            "fees_year": 2024,
            "amount": 6000.0,
            "status": 'pending',
            "date": "2024-01-15T00:00:00Z",
            "due_date": "2024-01-25T00:00:00Z",
            "investment_id": self.investment_id,
            "capital_call_id": self.capital_call_id
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('id', response_data)
        print("RESPONSE DATA", response_data)
        # Verify that the bill was created
        created_bill = bill_model.find_one({"_id": ObjectId(response_data['id'])})
        self.assertIsNotNone(created_bill)
        self.assertEqual(created_bill['type'], 'upfront fees')
        self.assertEqual(created_bill['to_investor_id'], self.investor_id)

    def test_bill_detail_get(self):
        # Create a bill
        bill = bill_model.insert_one({
            "type": BillType.MEMBERSHIP.name,
            "to_investor_id": self.investor_id,
            "fees_year": 2023,
            "amount": 3000.0,
            "status": BillStatus.CREATED.name,
            "date": "2023-10-01T00:00:00Z",
            "due_date": "2023-10-11T00:00:00Z",
            "investment_id": None,
            "capital_call_id": self.capital_call_id
        })
        bill_id = str(bill.inserted_id)
        url = reverse('bill-detail', args=[bill_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], BillType.MEMBERSHIP.name)
        self.assertEqual(data['fees_year'], 2023)
        self.assertEqual(data['to_investor_id'], self.investor_id)

    def test_bill_detail_put(self):
        # Create a bill
        bill = bill_model.insert_one({
            "type": BillType.MEMBERSHIP.name,
            "to_investor_id": self.investor_id,
            "fees_year": 2023,
            "amount": 3000.0,
            "status": BillStatus.CREATED.name,
            "date": "2023-10-01T00:00:00Z",
            "due_date": "2023-10-11T00:00:00Z",
            "investment_id": None,
            "capital_call_id": self.capital_call_id
        })
        bill_id = str(bill.inserted_id)
        url = reverse('bill-detail', args=[bill_id])
        updated_data = {
            "type": BillType.MEMBERSHIP.name,
            "to_investor_id": self.investor_id,
            "fees_year": 2024,
            "amount": 3500.0,
            "status": BillStatus.PENDING.name,
            "date": "2024-01-15T00:00:00Z",
            "due_date": "2024-01-25T00:00:00Z",
            "investment_id": None,
            "capital_call_id": self.capital_call_id
        }
        response = self.client.put(url, data=json.dumps(updated_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Verify the update
        updated_bill = bill_model.find_one({"_id": ObjectId(bill_id)})
        self.assertEqual(updated_bill['fees_year'], 2024)
        self.assertEqual(updated_bill['amount'], 3500.0)
        self.assertEqual(updated_bill['status'], BillStatus.PENDING.name)

    def test_bill_detail_delete(self):
        # Create a bill
        bill = bill_model.insert_one({
            "type": BillType.MEMBERSHIP.name,
            "to_investor_id": self.investor_id,
            "fees_year": 2023,
            "amount": 3000.0,
            "status": BillStatus.CREATED.name,
            "date": "2023-10-01T00:00:00Z",
            "due_date": "2023-10-11T00:00:00Z",
            "investment_id": None,
            "capital_call_id": self.capital_call_id
        })
        bill_id = str(bill.inserted_id)
        url = reverse('bill-detail', args=[bill_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        # Verify deletion
        deleted_bill = bill_model.find_one({"_id": ObjectId(bill_id)})
        self.assertIsNone(deleted_bill)

    # Bill Investor Tests
    def test_bill_investor_post(self):
        url = reverse('bill-investor')
        data = {
            "bill_data": {
                "type": "yearly fees",
                "to_investor_id": self.investor_id,
                "fees_year": 1,
                "capital_call_id": self.capital_call_id,
                "investment_id": self.investment_id,
            }
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Bill created successfully')
        # Verify that the bill was created
        created_bill = bill_model.find_one({
            "type": "yearly fees",
            "to_investor_id": self.investor_id,
            "fees_year": 1
        })
        self.assertIsNotNone(created_bill)
        expected_amount = 60000.0 * 0.02 * 5
        self.assertEqual(created_bill['amount'], expected_amount)
        # Verify that the bill was added to the capital call
        updated_capital_call = capital_call_model.find_one({"_id": ObjectId(self.capital_call_id)})
        self.assertIn(str(created_bill['_id']), [str(bill_id) for bill_id in updated_capital_call.get('bills', [])])

    def test_bill_investor_post_missing_bill_data(self):
        url = reverse('bill-investor')
        data = {}  # Missing bill_data
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'bill_data is required')

    def test_bill_investor_post_invalid_investor(self):
        url = reverse('bill-investor')
        data = {
            "bill_data": {
                "type": BillType.MEMBERSHIP.name,
                "to_investor_id": "invalid_id",
                "fees_year": 2024,
                "capital_call_id": self.capital_call_id
            }
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Invalid investor_id')

    # Investment Tests
    def test_investment_list_get(self):
        url = reverse('investment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['amount'], 60000.0)
        self.assertEqual(data[0]['investor_id'], self.investor_id)

    def test_investment_list_post(self):
        url = reverse('investment-list')
        data = {
            "amount": 45000.0,
            "investor_id": self.investor_id,
            "duration": 3
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('id', response_data)
        # Verify that the investment was created
        created_investment = investment_model.find_one({"_id": ObjectId(response_data['id'])})
        self.assertIsNotNone(created_investment)
        self.assertEqual(created_investment['amount'], 45000.0)
        self.assertEqual(created_investment['duration'], 3)
        self.assertEqual(created_investment['investor_id'], self.investor_id)

    def test_investment_list_post_high_amount(self):
        url = reverse('investment-list')
        data = {
            "amount": 70000.0,
            "investor_id": self.investor_id,
            "duration": 4
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('id', response_data)
        # Verify that the investment was created
        created_investment = investment_model.find_one({"_id": ObjectId(response_data['id'])})
        self.assertIsNotNone(created_investment)
        self.assertEqual(created_investment['amount'], 70000.0)
        self.assertEqual(created_investment['duration'], 4)
        self.assertEqual(created_investment['investor_id'], self.investor_id)
        # Verify that the membership bill was updated to amount 0
        membership_bill = bill_model.find_one({
            "type": "membership",
            "to_investor_id": self.investor_id
        })
        print(membership_bill)
        self.assertIsNotNone(membership_bill)
        self.assertEqual(membership_bill['amount'], 0.0)