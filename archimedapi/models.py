from dataclasses import Field, dataclass
from bson import ObjectId
from django.db import models
from db_connection import db
from pydantic import BaseModel, ConfigDict, computed_field, field_validator
from utils import validate_input, days_in_year
from datetime import date as datetime_date, timedelta

sample_collection = db['sample']
bill_model = db['bill']
entity_model = db['entity']
capital_call_model = db['capital_call']
investment_model = db['investment']

bank_account_type_regex = {"iban": "^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$", "swift": "^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$"}
fee_percentage = 0.02

class BankAccountType(models.TextChoices):
    IBAN = 'iban'
    SWIFT = 'swift'

class EntityType(models.TextChoices):
    COMPANY = 'company'
    FUND = 'fund'
    INVESTOR = 'investor'
    
class Entity(BaseModel):
    name: str
    type: EntityType
    address: str
    bank_account_number: str
    bank_account_type: BankAccountType
    contact_person: str
    contact_person_email: str
    contact_person_phone: str

    @field_validator("bank_account_number")
    def bank_account_number(cls, value):
        if not validate_input(value, bank_account_type_regex[cls.bank_account_type]):
            raise ValueError(f"Bank account number {value} does not match {cls.bank_account_type} format")

    class Config:
        arbitrary_types_allowed = True

class Investment(BaseModel):
    amount: float
    investor_id: str
    duration: int

    @field_validator("investor_id")
    def investor_exists(cls, value):
        if not entity_model.find_one({"_id": ObjectId(value)}):
            raise ValueError(f"Entity with id {value} not found")
        return value

class BillType(models.TextChoices):
    MEMBERSHIP = 'membership'
    UPFRONT_FEES = 'upfront fees'
    YEARLY_FEES = 'yearly fees'

class BillStatus(models.TextChoices):
    CREATED = 'created'
    PENDING = 'pending'
    PAID = 'paid'    

class BillModel(BaseModel):
    type: BillType
    capital_call_id: str
    to_investor_id: str
    amount: float
    status: BillStatus = BillStatus.CREATED
    date: str = datetime_date.today().isoformat()
    due_date: str = (datetime_date.today() + timedelta(days=10)).isoformat()
    investment_id: str | None = None # if the bill type is related to an investment (upfront of yearly fees)
    fees_year: int | None = None # if the bill type is yearly/upfront fees

    @field_validator("capital_call_id")
    def capital_call_exists(cls, value):
        if not capital_call_model.find_one({"_id": ObjectId(value)}):
            raise ValueError(f"Capital call with id {value} not found")
        return value 
        
    @field_validator("investment_id")
    def investment_exists(cls, value):
        print(value)
        if not value: 
            return
        if not investment_model.find_one({"_id": ObjectId(value)}):
            raise ValueError(f"Investment with id {value} not found")  
        return value  

class CapitalCallStatus(models.TextChoices):
    VALIDATED = 'validated'
    SENT = 'sent'    
    PAID = 'paid'    
    OVERDUE = 'overdue'    

class CapitalCallModel(BaseModel):
    from_entity_id: str
    investor_entities: list[str]
    date: str
    purpose:str
    status: CapitalCallStatus
    currency: str
    payment_method: str
    due_date: str
    bills: list[str]

    @field_validator("bills")
    def bills_exist(cls, value):
        for bill_id in value:
            if not bill_model.find_one({"_id": ObjectId(bill_id)}):
                raise ValueError(f"Bill with id {bill_id} not found")
        return value    
    @field_validator("from_entity_id")
    def from_entity_exists(cls, value):
        if not entity_model.find_one({"_id": ObjectId(value)}):
            raise ValueError(f"Entity with id {value} not found")    
        return value
    @field_validator("investor_entities")
    def investors_exist(cls, value):
        for investor_id in value:
            investor = entity_model.find_one({"_id": ObjectId(investor_id)})
            print(investor)   
            if not investor:
                raise ValueError(f"Entity with id {investor_id} not found")
            if investor["type"] != EntityType.INVESTOR:
                raise ValueError(f"Entity with id {investor_id} is not an investor")
        return value    
    class Config:
        arbitrary_types_allowed = True

