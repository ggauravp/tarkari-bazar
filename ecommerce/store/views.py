from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData , guestOrder
from django.contrib.auth.models import User  ############
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from store.models import Customer	

# Create your views here.

from django.shortcuts import render

def store(request):
	data = cartData(request)	
	cartItems = data['cartItems']

	products = Product.objects.all()
	context = {'products': products , 'cartItems': cartItems}
	return render(request, 'store/store.html', context)

def cart(request):
	data = cartData(request)	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items , 'order': order , 'cartItems': cartItems}
	return render(request, 'store/cart.html', context)


def checkout(request):
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items , 'order': order , 'cartItems': cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)	
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('productId:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False) 

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = get_object_or_404(Customer, user=request.user)
		order, created = Order.objects.get_or_create(customer= customer , complete=False)
		
	else:
		customer,order = guestOrder (request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
			Customer=Customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('payment completed', safe=False)

##########################

def register(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        if pass1 != pass2:
            return JsonResponse('wrong password', safe=False)
		
            # You may want to handle this error in a more user-friendly way
        else:
            # Create user
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            
            # Create associated customer
            customer = Customer.objects.create(user=my_user)  # Assuming Customer has a 'user' field
            customer.save()
            
            # Redirect to login page after successful registration
            return redirect('login')
    return render(request, 'store/register.html')

def login_user(request):
	if request.method == 'POST':
		username=request.POST.get('username')
		pass1=request.POST.get('pass')
		user =  authenticate(request,username=username,password=pass1)
		if user is not None:
			login(request, user)
			#messages.success(request,("you have been logged in"))
			return redirect ('store')
		else:
			#messages.info(request,"username or password doesnot match")
			return redirect('login')
	return render(request,'store/login.html')

def logout_user(request):
	logout(request)
	#messages.success(request,"you have been logged out ")
	return redirect('store')

	