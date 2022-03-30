from django.shortcuts import render
from django.http import JsonResponse
from pymongo import MongoClient
from bson import json_util
from email.message import EmailMessage
from datetime import date
import smtplib
import json
from django.views.decorators.csrf import csrf_exempt

client = MongoClient('mongodb+srv://ashwath:qwertyashwath@main.ezawg.gcp.mongodb.net/SrinivasaSiddhaStores?retryWrites=true&w=majority')
db = client.get_database('SrinivasaSiddhaStores')

def getProducts(request):
    records = db.products
    res = list(records.find())
    return JsonResponse(json.loads(json_util.dumps(res)), safe=False)

@csrf_exempt
def orders(request):
    records = db.orders

    today = date.today()
    d1 = today.strftime("%d/%m/%Y")

    data = json.loads(request.body)
    new_order = {
    'id' : 100 + records.count_documents({}),
    'name' : data['name'],
    'phone' : data['phone'],
    'email' : data['email'],
    'address': {       
        'add1' : data['add1'],  
        'add2' : data['add2'],  
        'city' : data['city'],  
        'state' : data['state'],  
        'pincode' : data['pincode']
    },
    'order_items' : data['order_items'],
    'date' : d1,
    'delivery_charges' : data['delivery'],
    'sub_total' : data['sub_total'],
    'payment': {
        'payment_id' : data['payment_id'],
        'order_id' : data['order_id'],
        'signature' : data['signature']
    },
    'delivery_details': {
        'refno': '',
        'courier': '',
        'dispatch_date': ''
    },
    'completed' : 0
    }

    records.insert_one(new_order)    
    return JsonResponse(json.loads(json_util.dumps(new_order)), safe=False)

@csrf_exempt
def mailing(request):
    
    data = json.loads(request.body)
    name = data['name']
    email = data['email']

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login('srinivasasiddhastores@gmail.com', 'nstxxexzlwzvizsx')

    msg = EmailMessage()
    msg.set_content(f'Hello {name}!\n\nThank you for being our valued customer. We hope our product will meet your expectations. Let us know if you have any questions. We hope you enjoy your new purchase! And to know further updates, check with our website:\nhttp://localhost:8000\n\n\nThankyou!')

    msg['Subject'] = 'Order Placed!'
    msg['From'] = 'srinivasasiddhastores@gmail.com'
    msg['To'] = email

    s.send_message(msg)
    s.quit()
    
    return JsonResponse({'res':'mail sent'}, safe=False)
