from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional
from datetime import datetime



class CustomerStancerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    

class CustomerListStancerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)    
    customers: list[CustomerStancerSchema]

    def __iter__(self):
        return iter(self.customers)
    
class PaymentStancerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    customer: Optional[CustomerStancerSchema] = None
    created: datetime
    stancer_amount: float = Field(alias="amount")
    description: Optional[str] = None
    status: Optional[str] = None
    return_url: Optional[str] = None
    payment_intent: Optional[str] = None
    
    @computed_field
    def real_amount(self) -> float:
        return self.stancer_amount / 100
    

class PaymentIntentStancerSchema(BaseModel):
    """
    <status> values:
        "require_payment_method"
        "require_authentication"
        "require_authorization"
        "authorized"
        "processing"
        "captured"
        "canceled"
        "unpaid"
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    customer : Optional[str] = None
    payment : Optional[str] = None
    status: Optional[str] = None
    amount: int
    description: Optional[str] = None
    status : Optional[str] = None
    url: str
    return_url: Optional[str] = None
    created_at: int
    date_settlement: Optional[str] = None

    @computed_field
    def real_amount(self) -> float:
        return self.amount / 100

class PaymentIntentDetailsSchema(PaymentIntentStancerSchema):
    customerStancer : Optional[CustomerStancerSchema] = None
    paymentStancer : Optional[PaymentStancerSchema] = None

class PaymentIntentListStancerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)    
    payment_intents: list[PaymentIntentStancerSchema]

    def __iter__(self):
        return iter(self.payment_intents)

