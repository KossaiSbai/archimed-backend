import json
import logging
from datetime import date

from bson import ObjectId, json_util
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .models import (
    BillType,
    BillModel,
    CapitalCallModel,
    Investment,
    bill_model,
    capital_call_model,
    entity_model,
    investment_model,
    sample_collection
)
from utils import days_in_year

logger = logging.getLogger('app')


def parse_json(data):
    return json.loads(json_util.dumps(data))


def index(request):
    return JsonResponse({"message": "Hello, world. You're at the archimedapi index."})


@csrf_exempt
@api_view(['GET', 'POST'])
def bill_list(request):
    logger.info("bill_list view called with method %s by user %s", request.method, request.user)
    if request.method == 'GET':
        bills = parse_json(bill_model.find())
        logger.info("Returning %d bills for user %s", len(bills), request.user)
        return JsonResponse(bills, safe=False)
    
    elif request.method == 'POST':
        bill_data = JSONParser().parse(request)
        logger.info("Received bill data: %s", bill_data)
        try:
            validated_data = BillModel(**bill_data)
            result = bill_model.insert_one(validated_data.model_dump())
            return JsonResponse({'id': str(result.inserted_id)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Failed to validate bill data: %s", e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def bill_detail(request, pk):
    logger.info("bill_detail view called with method %s for bill id %s by user %s", request.method, pk, request.user)
    try:
        bill = bill_model.find_one({"_id": ObjectId(pk)})
        if not bill:
            logger.error("Bill with id %s does not exist, requested by user %s", pk, request.user)
            return JsonResponse({'message': 'The bill does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error("Error retrieving bill with id %s: %s", pk, e)
        return JsonResponse({'message': 'Error retrieving the bill'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'GET':
        logger.info("Returning bill data for id %s to user %s", pk, request.user)
        return JsonResponse(parse_json(bill), safe=False)

    elif request.method == 'PUT':
        bill_data = JSONParser().parse(request)
        try:
            bill_model.update_one({"_id": ObjectId(pk)}, {"$set": bill_data})
            updated_bill = bill_model.find_one({"_id": ObjectId(pk)})
            logger.info("Bill with id %s updated successfully by user %s", pk, request.user)
            return JsonResponse(parse_json(updated_bill), status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning("Bill update failed for id %s with errors: %s", pk, e)
            return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            bill_model.delete_one({"_id": ObjectId(pk)})
            logger.info("Bill with id %s deleted successfully by user %s", pk, request.user)
            return JsonResponse({'message': 'Bill was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Failed to delete bill with id %s: %s", pk, e)
            return JsonResponse({'message': 'Failed to delete the bill'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET', 'POST'])
def capital_call_list(request):
    logger.info("capital_call_list view called with method %s by user %s", request.method, request.user)
    if request.method == 'GET':
        capital_calls = parse_json(capital_call_model.find())
        logger.info("Returning %d capital calls for user %s", len(capital_calls), request.user)
        return JsonResponse(capital_calls, safe=False)
    
    elif request.method == 'POST':
        capital_call_data = JSONParser().parse(request)
        logger.info("Received capital call data: %s", capital_call_data)
        try:
            validated_data = CapitalCallModel(**capital_call_data)
            result = capital_call_model.insert_one(validated_data.model_dump())
            return JsonResponse({'id': str(result.inserted_id)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Failed to validate capital call data: %s", e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def capital_call_detail(request, pk):
    logger.info("capital_call_detail view called with method %s for capital id %s by user %s", request.method, pk, request.user)
    try:
        capital_call = capital_call_model.find_one({"_id": ObjectId(pk)})
        if not capital_call:
            logger.error("Capital call with id %s does not exist, requested by user %s", pk, request.user)
            return JsonResponse({'message': 'The capital call does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error("Error retrieving capital call with id %s: %s", pk, e)
        return JsonResponse({'message': 'Error retrieving the capital call'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'GET':
        logger.info("Returning capital call data for id %s to user %s", pk, request.user)
        return JsonResponse(parse_json(capital_call), safe=False)

    elif request.method == 'PUT':
        capital_call_data = JSONParser().parse(request)
        try:
            capital_call_model.update_one({"_id": ObjectId(pk)}, {"$set": capital_call_data})
            updated_capital_call = capital_call_model.find_one({"_id": ObjectId(pk)})
            logger.info("Capital call with id %s updated successfully by user %s", pk, request.user)
            return JsonResponse(parse_json(updated_capital_call), status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning("Capital call update failed for id %s with errors: %s", pk, e)
            return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            capital_call_model.delete_one({"_id": ObjectId(pk)})
            logger.info("Capital call with id %s deleted successfully by user %s", pk, request.user)
            return JsonResponse({'message': 'Capital call was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Failed to delete capital call with id %s: %s", pk, e)
            return JsonResponse({'message': 'Failed to delete the capital call'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def update_capital_call_with_bill(capital_call_id, bill):
    try:
        capital_call_model.update_one(
            {"_id": ObjectId(capital_call_id)},
            {"$push": {"bills": bill.inserted_id}}
        )
        logger.info("Capital call with id %s updated with new bill %s", capital_call_id, bill.inserted_id)
    except Exception as e:
        logger.error("Failed to update capital call with id %s with new bill: %s", capital_call_id, e)
        raise e


@api_view(['POST'])
def bill_investor(request):
    data = JSONParser().parse(request)
    bill_data = data.get("bill_data")
    if not bill_data:
        return JsonResponse({'error': 'bill_data is required'}, status=status.HTTP_400_BAD_REQUEST)

    year = bill_data.get("fees_year")
    investor_id = bill_data.get("to_investor_id")
    investment_id = bill_data.get("investment_id")

    if not investor_id:
        return JsonResponse({'error': 'to_investor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        investor = entity_model.find_one({"_id": ObjectId(investor_id)})
    except Exception as e:
        logger.error("Invalid investor_id %s: %s", investor_id, e)
        return JsonResponse({'error': 'Invalid investor_id'}, status=status.HTTP_400_BAD_REQUEST)

    if not investor or investor.get("type") != "investor":
        return JsonResponse({'error': 'The entity is not an investor'}, status=status.HTTP_400_BAD_REQUEST)

    bill_type = bill_data.get("type")
    if not bill_type:
        return JsonResponse({'error': 'bill type is required'}, status=status.HTTP_400_BAD_REQUEST)

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
            return JsonResponse({'error': f"{bill_type} bill for year {year} already exists for investor {investor_id}"}, status=status.HTTP_400_BAD_REQUEST)

    bill_amount = compute_bill_amount(bill_type, 0.02, investor_id, investment_id, year)
    bill_data["amount"] = bill_amount
    if bill_type == BillType.MEMBERSHIP:
        bill_data["investment_id"] = None

    try:
        bill = BillModel(**bill_data)
        inserted_result = bill_model.insert_one(bill.model_dump())
        update_capital_call_with_bill(bill_data["capital_call_id"], inserted_result)
    except Exception as e:
        logger.error("Error creating bill for investor %s: %s", investor_id, e)
        return JsonResponse({'error': 'Error creating bill'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info("Bill created successfully for investor %s", investor_id)
    return JsonResponse({'message': 'Bill created successfully'}, status=status.HTTP_201_CREATED)


def compute_bill_amount(bill_type: BillType, fee_percentage, investor_id, investment_id=None, year=None):
    if bill_type == BillType.MEMBERSHIP:
        all_investments = [investment["amount"] for investment in investment_model.find({"investor_id": investor_id})]
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
            current_date = date.today()
            current_year = current_date.year
            current_month = current_date.month
            end_of_year = date(current_year, 12, 31)
            delta = end_of_year - current_date
            days_diff = delta.days
            if current_year <= 2019 and current_month < 4:
                amounts = [days_diff / 365 * fee_percentage * amount]
                amounts.extend([fee_percentage * amount for _ in range(1, investment.get("duration", 1))])
                try:
                    return amounts[year]
                except IndexError:
                    logger.error("Year index %s out of range for amounts list", year)
                    return 0
            if current_year >= 2019 and current_month >= 4:
                amounts = [
                    days_diff / days_in_year() * fee_percentage * amount, 
                    fee_percentage * amount, 
                    (fee_percentage - 0.002) * amount, 
                    (fee_percentage - 0.004) * amount
                ]
                amounts.extend([(fee_percentage - 0.01) * amount for _ in range(4, investment.get("duration", 1))])
                try:
                    return amounts[year]
                except IndexError:
                    logger.error("Year index %s out of range for amounts list", year)
                    return 0
    return 0  # Default return value


@csrf_exempt
@api_view(['GET', 'POST'])
def investment_list(request):
    logger.info("investment_list view called with method %s by user %s", request.method, request.user)
    if request.method == 'GET':
        investments = parse_json(investment_model.find())
        logger.info("Returning %d investments for user %s", len(investments), request.user)
        return JsonResponse(investments, safe=False)
    
    elif request.method == 'POST':
        investment_data = JSONParser().parse(request)
        logger.info("Received investment data: %s", investment_data)
        try:
            validated_data = Investment(**investment_data)
            result = investment_model.insert_one(validated_data.model_dump())
            if validated_data.amount > 50000:
                membership_bill = bill_model.find_one({"type": BillType.MEMBERSHIP, "to_investor_id": validated_data.investor_id})
                if membership_bill:
                    bill_model.update_one(
                        {"_id": membership_bill["_id"]},
                        {"$set": {"amount": 0}}
                    )
            return JsonResponse({'id': str(result.inserted_id)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Failed to validate investment data: %s", e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
