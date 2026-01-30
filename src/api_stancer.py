import os
import httpx
from loguru import logger
import stancer
import datetime
from dotenv import load_dotenv
try:
    from shared.schemas import *
except ImportError:
    from schemas import *

load_dotenv(override=True)

RETURN_URL_DEFAULT = "https://example.com/return"


# --- Configuration ---

logger.info(f"Environment: {os.getenv('ENVIRONMENT')}")
if os.getenv("ENVIRONMENT") == "prod":
    stancer.Config().keys = [os.getenv("STANCER_PUBLIC_KEY_PROD"), os.getenv("STANCER_SECRET_KEY_PROD")]
    SECRET_KEY_STANCER = os.getenv("STANCER_SECRET_KEY_PROD")
    AUTH_BEARER = f"Bearer {SECRET_KEY_STANCER}"
    stancer.Config().mode = stancer.Config.LIVE_MODE
    logger.info("Stancer configured in LIVE mode")
elif os.getenv("ENVIRONMENT") == "dev":
    # Initialize API (Replace with your actual keys)
    stancer.Config().keys = [os.getenv("STANCER_PUBLIC_KEY_DEV"), os.getenv("STANCER_SECRET_KEY_DEV")]
    SECRET_KEY_STANCER = os.getenv("STANCER_SECRET_KEY_DEV")
    stancer.Config().mode = stancer.Config.TEST_MODE
    AUTH_BEARER = f"Bearer {SECRET_KEY_STANCER}"
    logger.info("Stancer configured in TEST mode")
else:
    raise Exception("ENVIRONMENT variable not set to 'dev' or 'prod'")


def get_customer(id=None, name=None, email=None, phone=None) -> CustomerStancerSchema:
    """
    Creates a new customer or returns existing if ConflictError occurs.
    """
    if id:
        response = httpx.get(f'https://api.stancer.com/v2/customers/{id}',
                             headers={'Authorization': AUTH_BEARER})
        return CustomerStancerSchema.model_validate(response.json())
    
    new_customer = stancer.Customer()
    if not (name and (phone or email)):
        raise ValueError("Name and At least one email, or phone must be provided")
    
    new_customer.name = name.ljust(4)[:64]  # Stancer requires at least 4 characters
    if email:
        new_customer.email = email.ljust(5)[:64]
    if phone:
        new_customer.mobile = phone.ljust(8)[:16]
    
    try:
        new_customer.send()
    except stancer.exceptions.ConflictError as e:
        # Extract ID from message: "... (cust_...)"
        import re
        match = re.search(r'\((cust_[A-Za-z0-9]+)\)', str(e))
        if match:
            customer_id = match.group(1)
            return get_customer(id=customer_id)
        raise e
    except stancer.exceptions.BadRequestError as e:
        # {'email': 'An email address must contain a single @'}
        # {'email_or_mobile': 'Missing email and / or mobile value'}
        logger.error(f"BadRequestError when creating customer: {e}")
        logger.info(f"Stancer API Customer data: name={name}, email={email}, phone={phone} Error : {e}")
        logger.info("Creating a new customer with valid but wrong email to bypass validation.")
        name = f"{name} - Tel: {phone} - Mail: {email}"
        email = f"fake_{int(datetime.datetime.now().timestamp())}@example.com"
        return get_customer(name=name, email=email)
    
    return new_customer


def list_customers(limit=100) -> CustomerListStancerSchema:
    response = httpx.get('https://api.stancer.com/v2/customers/',
                     headers={'Authorization': f'Bearer {SECRET_KEY_STANCER}'}, params={'limit': limit})

    customers = response.json()
    return CustomerListStancerSchema.model_validate(customers)

def get_payment(payment_id:str) -> PaymentStancerSchema:
    response = httpx.get(f'https://api.stancer.com/v2/payments/{payment_id}',
                         headers={'Authorization': AUTH_BEARER})
    return PaymentStancerSchema.model_validate(response.json())

def get_payment_intents(limit=10) -> PaymentIntentListStancerSchema:
    response = httpx.get('https://api.stancer.com/v2/payment_intents/',
                         headers={'Authorization': AUTH_BEARER}, params={'limit': limit})
    return PaymentIntentListStancerSchema.model_validate(response.json())

def get_payment_intent(payment_intent_id:str) -> PaymentIntentDetailsSchema:
    response = httpx.get(f'https://api.stancer.com/v2/payment_intents/{payment_intent_id}',
                         headers={'Authorization': AUTH_BEARER})
    paymentIntentSchema = PaymentIntentStancerSchema.model_validate(response.json())
    
    customer = get_customer(id=paymentIntentSchema.customer) if paymentIntentSchema.customer else None
    
    payment = get_payment(paymentIntentSchema.payment) if paymentIntentSchema.payment else None
    # Fetch customer details

    return PaymentIntentDetailsSchema(**paymentIntentSchema.model_dump(), customerStancer=customer, paymentStancer=payment)

def update_payment_intent(payment_intent_id:str, amount:int=None,description:str=None, return_url:str=None) -> PaymentIntentStancerSchema:
    payload = {}
    if description:
        payload["description"] = description
    if return_url:
        payload["return_url"] = return_url
    if amount:
        payload["amount"] = amount

    response = httpx.patch(f'https://api.stancer.com/v2/payment_intents/{payment_intent_id}',
                          headers={'Authorization': AUTH_BEARER, 'Content-Type': 'application/json'},
                          json=payload)
    return PaymentIntentStancerSchema.model_validate(response.json())

def create_payment_intent(amount:int, description:str, customer_id:str=None, return_url:str=None) -> PaymentIntentStancerSchema:
    payload = {
        "amount": amount,
        "description": description,
        "methods_allowed": ["card"]
    }
    if customer_id:
        payload["customer"] = customer_id
    if return_url:
        payload["return_url"] = return_url

    response = httpx.post('https://api.stancer.com/v2/payment_intents/',
                          headers={'Authorization': AUTH_BEARER, 'Content-Type': 'application/json'},
                          json=payload)
    return PaymentIntentStancerSchema.model_validate(response.json())