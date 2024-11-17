import json
import os
from dotenv import load_dotenv

from bson import ObjectId, json_util
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from utils.logger import logger
from utils.currency_conversion import convert_currency
from utils.bill_utils import check_existing_bill, compute_bill_amount

load_dotenv()

from .models import (
    BillType,
    BillModel,
    CapitalCallModel,
    Entity,
    Investment,
    bill_model,
    capital_call_model,
    investment_model,
    entity_model,
)

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
            capital_call_model.update_many({"bills": ObjectId(pk)}, {"$pull": {"bills": ObjectId(pk)}})
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
        capital_call_model.update_one({"_id": ObjectId(capital_call_id)}, {"$push": {"bills": bill.inserted_id}})
        logger.info("Capital call with id %s updated with new bill %s", capital_call_id, bill.inserted_id)
    except Exception as e:
        logger.error("Failed to update capital call with id %s with new bill: %s", capital_call_id, e)
        raise e

@api_view(['POST'])
def bill_investor(request):
    logger.info("bill_investor view called with method %s by user %s", request.method, request.user)
    data = JSONParser().parse(request)
    if not data:
        logger.error("No bill data provided by user %s", request.user)
        return JsonResponse({'error': 'bill data is required'}, status=status.HTTP_400_BAD_REQUEST)
    logger.info("Received bill data: %s", data)
    year = data.get("fees_year", 0)
    data["fees_year"] = int(year) 
    investor_id = data.get("to_investor_id")
    investment_id = data.get("investment_id")
    if not investor_id:
        logger.error("to_investor_id is missing in the request by user %s", request.user)
        return JsonResponse({'error': 'to_investor_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        investor = entity_model.find_one({"_id": ObjectId(investor_id)})
    except Exception as e:
        logger.error("Invalid investor_id %s: %s", investor_id, e)
        return JsonResponse({'error': 'Invalid investor_id'}, status=status.HTTP_400_BAD_REQUEST)
    if not investor or investor.get("type") != "investor":
        logger.error("Entity with id %s is not an investor, requested by user %s", investor_id, request.user)
        return JsonResponse({'error': 'The entity is not an investor'}, status=status.HTTP_400_BAD_REQUEST)
    bill_type = data.get("type")
    if not bill_type:
        logger.error("bill type is missing in the request by user %s", request.user)
        return JsonResponse({'error': 'bill type is required'}, status=status.HTTP_400_BAD_REQUEST)
    if bill_type == BillType.MEMBERSHIP:
        data["investment_id"] = None
    response = check_existing_bill(bill_model, bill_type, investor_id, year)
    if response and response.status_code != 200:
        logger.error("Existing bill check failed for investor %s", investor_id)
        return response
    percentage_fee = float(os.getenv("PERCENTAGE_FEE", 0.02))
    bill_amount = compute_bill_amount(bill_type, percentage_fee, investor_id, investment_id, year)
    bill_amount = convert_currency(bill_amount, investor.get("bank_account_currency"))
    data["amount"] = bill_amount
    try:
        bill = BillModel(**data)
        inserted_result = bill_model.insert_one(bill.model_dump())
        update_capital_call_with_bill(data["capital_call_id"], inserted_result)
    except Exception as e:
        logger.error("Error creating bill for investor %s: %s", investor_id, e)
        return JsonResponse({'error': 'Error creating bill '}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.info("Bill created successfully for investor %s", investor_id)
    return JsonResponse({'message': 'Bill created successfully'}, status=status.HTTP_201_CREATED)

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
                    bill_model.update_one({"_id": membership_bill["_id"]}, {"$set": {"amount": 0}})
            return JsonResponse({'id': str(result.inserted_id)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Failed to validate investment data: %s", e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def investment_detail(request, pk):
    logger.info("investment_detail view called with method %s for entity id %s by user %s", request.method, pk, request.user)
    try:
        investment = investment_model.find_one({"_id": ObjectId(pk)})
        if not investment:
            logger.error("Investment with id %s does not exist, requested by user %s", pk, request.user)
            return JsonResponse({'message': 'The investment does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error("Error retrieving investment with id %s: %s", pk, e)
        return JsonResponse({'message': 'Error retrieving the investment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method == 'GET':
        logger.info("Returning investment data for id %s to user %s", pk, request.user)
        return JsonResponse(parse_json(investment), safe=False)
    elif request.method == 'PUT':
        investment_data = JSONParser().parse(request)
        try:
            investment_model.update_one({"_id": ObjectId(pk)}, {"$set": investment_data})
            updated_investment = investment_model.find_one({"_id": ObjectId(pk)})
            logger.info("Investment with id %s updated successfully by user %s", pk, request.user)
            return JsonResponse(parse_json(updated_investment), status=status.HTTP_200_OK, safe=False)
        except Exception as e:
            logger.warning("Investment update failed for id %s with errors: %s", pk, e)
            return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST, safe=False)
    elif request.method == 'DELETE':
        try:
            investment_model.delete_one({"_id": ObjectId(pk)})
            logger.info("Investment with id %s deleted successfully by user %s", pk, request.user)
            return JsonResponse({'message': 'Investment was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Failed to delete investment with id %s: %s", pk, e)
            return JsonResponse({'message': 'Failed to delete the investment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET', 'POST'])
def entity_list(request):
    logger.info("entity_list view called with method %s by user %s", request.method, request.user)
    if request.method == 'GET':
        entities = parse_json(entity_model.find())
        logger.info("Returning %d entities for user %s", len(entities), request.user)
        return JsonResponse(entities, safe=False)
    elif request.method == 'POST':
        entity_data = JSONParser().parse(request)
        logger.info("Received entity data: %s", entity_data)
        try:
            validated_data = Entity(**entity_data)
            result = entity_model.insert_one(validated_data.model_dump())
            return JsonResponse({'id': str(result.inserted_id)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Failed to validate entity data: %s", e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE', 'PUT'])
def entity_detail(request, pk):
    logger.info("entity_detail view called with method %s for entity id %s by user %s", request.method, pk, request.user)
    try:
        entity = entity_model.find_one({"_id": ObjectId(pk)})
        if not entity:
            logger.error("Entity with id %s does not exist, requested by user %s", pk, request.user)
            return JsonResponse({'message': 'The entity does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error("Error retrieving entity with id %s: %s", pk, e)
        return JsonResponse({'message': 'Error retrieving the entity'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method == 'GET':
        logger.info("Returning entity data for id %s to user %s", pk, request.user)
        return JsonResponse(parse_json(entity), safe=False)
    elif request.method == 'PUT':
        entity_data = JSONParser().parse(request)
        try:
            entity_model.update_one({"_id": ObjectId(pk)}, {"$set": entity_data})
            updated_entity = entity_model.find_one({"_id": ObjectId(pk)})
            logger.info("Entity with id %s updated successfully by user %s", pk, request.user)
            return JsonResponse(parse_json(updated_entity), status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning("Entity update failed for id %s with errors: %s", pk, e)
            return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            entity_model.delete_one({"_id": ObjectId(pk)})
            logger.info("Entity with id %s deleted successfully by user %s", pk, request.user)
            return JsonResponse({'message': 'Entity was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Failed to delete entity with id %s: %s", pk, e)
            return JsonResponse({'message': 'Failed to delete the entity'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
