from django.shortcuts import redirect, render
from django.http import JsonResponse
from .models import Category, CreateUserForm, Product, Order, OrderTime
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
#################
from concurrent.futures import ThreadPoolExecutor


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
    # Xử lý song song trên danh sách sản phẩm nếu cần
    def enrich_product(product):
        product.discounted_price = product.price * 0.9  # Ví dụ: thêm thông tin giảm giá
        return product

    with ThreadPoolExecutor(max_workers=5) as executor:
        enriched_products = list(executor.map(enrich_product, products))
        
        
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
#### Xử lí luồng trong python
    def process_product(product):
        # Thêm logic xử lý từng sản phẩm tại đây, ví dụ:
        product.name = product.name.upper()
        return product

    with ThreadPoolExecutor(max_workers=10) as executor:
        processed_products = list(executor.map(process_product, products))
####
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
    ##Xử lí luồng
    def process_product(product):
        product.price_with_tax = product.price * 1.1  # Giả lập tính thuế
        return product

    with ThreadPoolExecutor(max_workers=10) as executor:
        processed_products = list(executor.map(process_product, products))
    
    ##
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
    # Tính toán song song trên từng mục trong giỏ hàng
    def calculate_item_total(item):
        return item.quantity * item.product.price  # Ví dụ tính tổng giá từng sản phẩm

    with ThreadPoolExecutor(max_workers=5) as executor:
        item_totals = list(executor.map(calculate_item_total, items))
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

###Xu li luong
    def update_order_item(order_item):##Phan duoc them
        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(update_order_item, [orderItem])
    return JsonResponse('Item was updated', safe=False)

def Information(request):
    context={}
    return render(request, 'app/information.html')


#############################################################################################
# from concurrent.futures import ThreadPoolExecutor
# from django.http import JsonResponse

# def process_product(product_id):
#     # Giả lập xử lý dữ liệu
#     print(f"Processing product {product_id}")

# def process_all_products_with_pool(request):
#     product_ids = range(1, 101)  # Giả lập danh sách ID sản phẩm

#     with ThreadPoolExecutor(max_workers=10) as executor:
#         executor.map(process_product, product_ids)

#     return JsonResponse({"status": "Products processed with ThreadPoolExecutor."})

############################################################################################################
import time
from concurrent.futures import ThreadPoolExecutor
from django.http import JsonResponse
## Thay thế bằng những cái trên
# Hàm giả lập một tác vụ nặng
def process_product(product_id):
    print(f"Processing product {product_id}...")
    time.sleep(2)  # Giả lập mất 2 giây để xử lý một sản phẩm
    print(f"Done processing product {product_id}.")

# Hàm view chính (sẽ được liên kết với một URL)
def process_all_products(request):
    product_ids = range(1, 101)  # Giả lập danh sách 100 sản phẩm (ID từ 1 đến 100)
##
    # Sử dụng ThreadPoolExecutor để quản lý các luồng
    with ThreadPoolExecutor(max_workers=10) as executor:
        # map áp dụng process_product cho từng product_id
        executor.map(process_product, product_ids)

    return JsonResponse({"status": "All products processed!"})
#######################################################
def chatbox(request):
    context={}
    return render(request, 'app/chatbox.html')
