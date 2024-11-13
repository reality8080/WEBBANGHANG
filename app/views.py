from django.shortcuts import redirect, render
from django.http import JsonResponse
from .models import Category, CreateUserForm, Product, Order, OrderTime
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.ordertime_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
    id = request.GET.get('id')
    products = Product.objects.filter(id=id)
    categories = Category.objects.filter(is_sub = False)    
    context = {'products': products,'categories' : categories,'items': items, 'order': order}
    return render(request, 'app/detail.html', context)
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tài khoản đã được tạo thành công! Bạn có thể đăng nhập.')
            return redirect('login')  # Chuyển hướng đến trang đăng nhập
    context = {'form': form}    
    return render(request, 'app/register.html', context)
def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']  # Đồng bộ với 'name' của input trong form
        keys = Product.objects.filter(name__icontains=searched)  # Sử dụng 'icontains' để không phân biệt chữ hoa/chữ thường
        return render(request, 'app/search.html', {'searched': searched, 'keys': keys})
    else:
        return render(request, 'app/search.html', {})
def category(request):  
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')  # Lấy slug của danh mục đang chọn
    
    if active_category:
        products = Product.objects.filter(category__slug=active_category)
    else:
        products = Product.objects.all()  # Nếu không có danh mục nào được chọn, hiển thị tất cả sản phẩm

    context = {
        'categories': categories,
        'products': products,
        'active_category': active_category  # Đảm bảo biến này được truyền đúng
    }
    return render(request, 'app/category.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Tên người dùng hoặc mật khẩu không chính xác.')

    return render(request, 'app/login.html')

def logoutPage(request):
    logout(request)
    return redirect('login')

def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.ordertime_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
    categories = Category.objects.filter(is_sub = False)
    products = Product.objects.all()
    context = {'categories':categories,'products': products}
    return render(request, 'app/home.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.ordertime_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    
    context = {'items': items, 'order': order}
    return render(request, 'app/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.ordertime_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}  
    
    context = {'items': items, 'order': order}
    return render(request, 'app/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user

    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderTime.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was updated', safe=False)

def Information(request):
    context={}
    return render(request, 'app/information.html')
#######################################################
def chatbox(request):
    context={}
    return render(request, 'app/chatbox.html')