import queue
from unicodedata import category
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import ProfileForm, RegistrationForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.

class ProductView(View):
    def get(self, request):
        topwear = Product.objects.filter(category='TW')
        bottomwear = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        context = {'topwear':topwear, 'bottomwear':bottomwear, 'mobiles': mobiles}
        return render(request,'home.html', context)


class ProductDetail(View):
    def get(self, request,id):
        product = Product.objects.get(pk=id)
        item_already = False
        if request.user.is_authenticated:
            item_already= Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request,'productdetail.html',{'product':product,'item_in_cart':item_already})

def mobile(request):
    mobiles = Product.objects.filter(category='M')
    return render(request,'mobile.html',{'mobiles':mobiles})

def topwear(request):
    topwear = Product.objects.filter(category='TW')
    return render(request,'topwear.html',{'topwear':topwear})

def bottomwear(request):
    bottomwear = Product.objects.filter(category='BW')
    return render(request,'bottomwear.html',{'bottomwear':bottomwear})

class Registration(View):
    def get(self,request):
        form = RegistrationForm()
        return render(request,'signup.html',{'form':form})

    def post(self,request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Sign Up Successfully , Please Login.')
            form.save()
        return render(request,'signup.html',{'form':form})

@method_decorator(login_required, name='dispatch')
class Profile(View):
    def get(self,request):
        form = ProfileForm()
        return render (request, 'profile.html', {'form':form, 'active':'btn-primary'})

    def post(self,request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            data = Customer(user=user, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            data.save()
            messages.success(request,'Profile Updated Successfully.')
        
        return render(request, 'profile.html',{'form':form,'active':'btn-primary'})

@login_required
def address(request):
    address = Customer.objects.filter(user=request.user)
    return render(request,'address.html', {'address':address, 'active':'btn-primary'})


def addtocart(request):
    user = request.user
    id = request.GET.get('prod_id')
    product = Product.objects.get(id=id)
    if user.is_authenticated:
        cart = Cart(user=user, product=product)
        cart.save()
        return redirect('cart')
    else:
        return redirect('login')

@login_required
def showcart(request):
    if request.user.is_authenticated:
        user = request.user
        cart =  Cart.objects.filter(user=user)
        amount= 0.0
        shipping_amount = 70.0
        total_amount =0.0
        cart_prod = [pd for pd in Cart.objects.all() if pd.user == user]
        if cart_prod:
            for i in cart_prod:
                amt = (i.quantity * i.product.discounted_price)
                amount += amt
                total_amount =amount + shipping_amount
            return render(request, 'addtocart.html', {'carts':cart, 'totalamount':total_amount,'amount':amount})
        else:
            return render(request,'empty.html')

@login_required
def plus_Cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        cart.quantity +=1
        cart.save()
        amount= 0.0
        shipping_amount = 70.0
        total_amount =0.0
        cart_prod = [pd for pd in Cart.objects.all() if pd.user == request.user]
        for i in cart_prod:
            amt = (i.quantity * i.product.discounted_price)
            amount += amt
            
        data = {
            'quantity':cart.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)

@login_required
def minus_Cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        cart.quantity -=1
        cart.save()
        amount= 0.0
        shipping_amount = 70.0
        total_amount =0.0
        cart_prod = [pd for pd in Cart.objects.all() if pd.user == request.user]
        for i in cart_prod:
            amt = (i.quantity * i.product.discounted_price)
            amount += amt
            
        data = {
            'quantity':cart.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)

@login_required
def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        
        cart.delete()
        amount= 0.0
        shipping_amount = 70.0
        
        cart_prod = [pd for pd in Cart.objects.all() if pd.user == request.user]
        for i in cart_prod:
            amt = (i.quantity * i.product.discounted_price)
            amount += amt
            
        data = {
            'amount':amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)

@login_required
def checkout(request):
    user = request.user
    address = Customer.objects.filter(user=user)
    item = Cart.objects.filter(user=user)
    amount= 0.0
    shipping_amount = 70.0
    cart_prod = [pd for pd in Cart.objects.all() if pd.user == user]
    if cart_prod:
        for i in cart_prod:
            amt = (i.quantity * i.product.discounted_price)
            amount += amt
        total_amount= amount+ shipping_amount

    return render(request,'checkout.html',{'address':address,'totalamount':total_amount,'items':item})

@login_required
def paymentdone(request):
    user = request.user
    customer_id = request.GET.get('custid')
    customer =  Customer.objects.get(id=customer_id)
    cart = Cart.objects.filter(user= user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect('order')

@login_required
def order(request):
    order = OrderPlaced.objects.filter(user= request.user)
    return render(request,'order.html',{'orders':order})
