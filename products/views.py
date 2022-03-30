from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import razorpay
client = razorpay.Client(auth=("rzp_test_6YBqanCDHfp17o", "PO5u5iHXTSk8TfvupciZvvIs"))

# context = {
#     'products': [],
#     'cart_number': 0,
#     'cart_items': [{},{}],
#     'delivery': 50,
#     'sub_total': 50
# }
# def session_handler(request):
    
# request.session('context')

def home(request):
    context = request.session.get('context', {
    'products': [],
    'cart_number': 0,
    'cart_items': [],
    'delivery': 50,
    'sub_total': 50
    })
    res = requests.get('https://srinivasasiddha.herokuapp.com/backend/getProducts')
    products = res.json()
    context['products'] = products
    request.session['context'] = context
    return render(request,'products/index.html', context)

def about(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']        
        json_data = {
        'email': email,
        'password': password
        }
        api_url = 'https://srinivasasiddha.herokuapp.com/backend/login'

        r = requests.post(url=api_url, json=json_data)

        # if 'msg' in r.json().keys():
        if r.status_code!=200:
            print(r.json()['msg'])
        else:
            return redirect('/')
            

    return render(request,'products/about.html', {'title': 'About'})

def product(request,pid):
    product_item = {}
    context = request.session.get('context')

    #To find the specific product
    for item in context['products']:
        if item['id']==pid:
            product_item = item
            break
    
    
    item_added = 0

    #To find whether the item is already added to the cart 
    for product in context['cart_items']:
            if product['id']==pid:
                item_added = 1
                break

    #Add to Cart on click
    if request.method == 'POST':
        item_added = 1
        context['cart_number'] += 1
        cart_product = {
            'id': product_item['id'],
            'product_name': product_item['product_name'],
            'company': product_item['company'],
            'price': product_item['price'],
            'qty': 1,
            'total': product_item['price'],
        }
        context['sub_total']+= int(product_item['price'])
        context['cart_items'].append(cart_product)
        print(context)

    #Update if that product is added or not
    product_item['item_added'] = item_added

    data = {
    'product_item': product_item,
    'products': context['products'],
    'cart_number': context['cart_number']
    }

    request.session['context'] = context
    return render(request,'products/product.html',data)

def cart(request):
    context = request.session.get('context')
    # print(context['cart_items'])
    return render(request,'products/cart.html',context)

def calculation(request):
    
    context = request.session.get('context', {
    'products': [],
    'cart_number': 0,
    'cart_items': [],
    'delivery': 50,
    'sub_total': 50
    })
    data = json.loads(request.body)
    pid = data['product_id']
    action = data['action']

    #To find the specific product and perform calculation
    products = context['cart_items']
    for i in range(len(products)):
        if products[i]['id']==pid:
            #addition
            if(action=="add"):
                products[i]['qty']+=1
                products[i]['total'] = str(int(products[i]['total']) + int(products[i]['price']))
                context['sub_total']+= int(products[i]['price'])
            #subtraction
            elif(action=="sub"):
                if products[i]['qty']>1:
                    products[i]['qty']-=1
                    products[i]['total'] = str(int(products[i]['total']) - int(products[i]['price']))
                    context['sub_total']-= int(products[i]['price'])
            #remove
            elif(action=="remove"):
                context['sub_total']-=int(products[i]['total'])
                del products[i]
            
            break

    context['cart_items'] = products 
    request.session['context'] = context  
    print(context['sub_total'])
    return JsonResponse('Item added', safe=False)

def thankyou(request):
    if 'context' in request.session:
        del request.session['context']
        if 'order' in request.session:
            del request.session['order']
    return render(request,'products/thankyou.html')

def user(request):
    context = request.session.get('context', {
    'products': [],
    'cart_number': 0,
    'cart_items': [],
    'delivery': 50,
    'sub_total': 50
    })

    if request.method == 'POST':
        name = request.POST['name']
        phone = request.POST['phone']
        email = request.POST['email']       
        add1 = request.POST['add1']  
        add2 = request.POST['add2']  
        city = request.POST['city']  
        state = request.POST['state']  
        pincode = request.POST['pincode']  

        json_data = {
        'name': name,
        'phone': phone,
        'email': email,
        'add1': add1,
        'add2': add2,
        'city': city,
        'state': state,
        'pincode': pincode,
        'order_items': context['cart_items'],
        'delivery': context['delivery'],
        'sub_total': context['sub_total'],
        'payment_id': 0
        }

        request.session['order'] = json_data
        
        return redirect('/paymentgateway')
    data = {
        'neccessary': 0
    }
    return render(request,'products/user.html',data)

@csrf_exempt
def payment(request,val):
    #if success
    #store in db
    api_url = 'https://srinivasasiddha.herokuapp.com/backend/orders'

    res = val.split("$")
    
    order = request.session['order']
    order['payment_id'] = res[0]
    order['order_id'] = res[1]
    order['signature'] = res[2]
    request.session['order'] = order
    json_data = order
    r = requests.post(url=api_url, json=json_data)

    #send mail
    api_url2 = 'https://srinivasasiddha.herokuapp.com/backend/mailing'
    json_data2 = {
        'name': json_data['name'],
        'email': json_data['email']
    }
    r = requests.post(url=api_url2, json=json_data2)

    #remove context
    if 'context' in request.session:
        del request.session['context']
        del request.session['order']

    return render(request,'products/success.html')

def paymentgateway(request):
    context = request.session.get('context')
    order = request.session.get('order')

    DATA = {
        "amount": context['sub_total']*100,
        "currency": "INR",
        "payment_capture": 1
    }
    payment_order = client.order.create(data=DATA)
    order_id = payment_order["id"]

    res = {
        'sub_total': context['sub_total']*100,
        'name': order['name'],
        'phone': order['phone'],
        'email': order['email'],
        'api_key': "rzp_test_6YBqanCDHfp17o",
        'order_id': order_id
    }

    return render(request,'products/payment.html',res)

    json_data = {
    'id': orderid
    }
    api_url = 'https://srinivasasiddha.herokuapp.com/backend/cancelorder'
    res = requests.post(url=api_url, json=json_data)
    order = res.json()
    payment_id = order['payment']['payment_id']
    resp = client.payment.refund(payment_id)
    print(resp)
    return redirect('/delorders')