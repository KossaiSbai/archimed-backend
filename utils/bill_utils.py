from django.http import JsonResponse
from archimedapi.models import BillType
from rest_framework import status
from datetime import date
from bson import ObjectId
from archimedapi.models import entity_model, investment_model
from utils.logger import logger
from utils.general import days_in_year

def check_existing_bill(bill_model, bill_type, investor_id, year):   
    if bill_type == BillType.MEMBERSHIP:
        existing_bill = bill_model.find_one({"type": bill_type, "to_investor_id": investor_id})
        if existing_bill:
            return JsonResponse({'error': f"{bill_type} bill already exists for investor {investor_id}"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if bill_type == BillType.UPFRONT_FEES:
            if bill_model.find_one({"type": BillType.YEARLY_FEES, "to_investor_id": investor_id}):
                return JsonResponse({'error': f"Yearly fees bill already exists for investor {investor_id} hence cannot generate an upfront fees bill"}, status=status.HTTP_400_BAD_REQUEST)
        elif bill_type == BillType.YEARLY_FEES:
            if bill_model.find_one({"type": BillType.UPFRONT_FEES, "to_investor_id": investor_id}):
                return JsonResponse({'error': f"Upfront fees bill already exists for investor {investor_id} hence cannot generate a yearly fees bill"}, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing bill for the same type and year
        if bill_model.find_one({"type": bill_type, "to_investor_id": investor_id, "fees_year": year}): 
            return JsonResponse({'error': f"{bill_type} bill already exists for investor {investor_id} for year {year}"}, status=status.HTTP_400_BAD_REQUEST)


def compute_bill_amount(bill_type: BillType, fee_percentage, investor_id, investment_id=None, year=None):
    if year:
        year = int(year)
        assert year >= 1, "Year must be a positive integer"
    if bill_type == BillType.MEMBERSHIP:
        all_investments = [investment["amount"] for investment in entity_model.find({"investor_id": investor_id})]
        if any(x > 50000 for x in all_investments):
            return 0
        else:
            return 3000
    else:
        if not investment_id:
            logger.error("Investment ID is required for bill type %s", bill_type)
            return FileNotFoundError 

        investment = investment_model.find_one({"_id": ObjectId(investment_id)})
        if not investment:
            logger.error("Investment with id %s not found", investment_id)
            return None

        amount = investment.get("amount", 0)
        if bill_type == BillType.UPFRONT_FEES:
            return amount * fee_percentage * 5
        elif bill_type == BillType.YEARLY_FEES:
            investment_date = investment.get("date")
            investment_date = date.fromisoformat(investment_date)
            current_date = date.today()
            end_of_year = date(current_date.year, 12, 31)
            delta = end_of_year - investment_date
            days_diff = delta.days
            if investment_date.year <= 2019 and investment_date.month < 4:
                amounts = [days_diff / 365 * fee_percentage * amount]
                amounts.extend([fee_percentage * amount for _ in range(1, investment.get("duration", 1))])
                try:
                    return amounts[year-1]
                except IndexError:
                    logger.error("Year index %s out of range for amounts list", year)
                    return 0
            if investment_date.year >= 2019 and investment_date.month >= 4: 
                amounts = [
                    (days_diff / days_in_year()) * fee_percentage * amount, 
                    fee_percentage * amount, 
                    (fee_percentage - 0.002) * amount, 
                    (fee_percentage - 0.004) * amount
                ]
                amounts.extend([(fee_percentage - 0.01) * amount for _ in range(4, investment.get("duration", 1))])
                try:
                    return amounts[year-1]
                except IndexError:
                    logger.error("Year index %s out of range for amounts list", year)
                    return 0
    return 0 