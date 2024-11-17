
import json
import os
import redis
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
  host=os.getenv('REDIS_HOST'),
  port=os.getenv('REDIS_PORT'),
  password=os.getenv('REDIS_PASSWORD'),
  decode_responses=True)

# Stores exchange rates from USD to other currencies
def get_exchange_rates():
    return json.loads(redis_client.execute_command('JSON.GET', 'currencies'))['rates']

exchange_rates = get_exchange_rates()

# Base currency is USD for now
def get_exchange_rate(target_currency):
    return exchange_rates.get(target_currency)

def convert_currency(amount, target_currency, base_currency="USD"):
    logger.info(f"Converting {amount} from {base_currency} to {target_currency}")
    if base_currency == target_currency:
        return amount
    exchange_rate = get_exchange_rate(target_currency)
    logger.info(f"Exchange rate {base_currency}/{target_currency}: {exchange_rate}")
    if not exchange_rate:
        raise ValueError("Exchange rate not available.")
    converted_amount = amount * exchange_rate
    return converted_amount
