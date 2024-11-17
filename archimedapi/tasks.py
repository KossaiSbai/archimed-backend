import datetime
import os
from celery import shared_task
import pymongo
from utils.logger import logger

@shared_task
def mark_overdue_invoices():
    url = os.environ.get('MONGODB_URL')
    client = pymongo.MongoClient(url)
    db = client['archimed']
    bill_model = db['bill']
    overdue_invoices = bill_model.find({
        "due_date": {"$lt": datetime.datetime.now().strftime('%Y-%m-%d')},
        "status": "pending"
    })
    overdue_invoices_list = list(overdue_invoices)
    logger.info(f"Marking {len(overdue_invoices_list)} invoices as overdue")
    for invoice in overdue_invoices_list:
        logger.info(f"Marking invoice {invoice['_id']} as overdue")
        bill_model.update_one({"_id": invoice["_id"]}, {"$set": {"status": "overdue"}})