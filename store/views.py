import hashlib
import hmac
import urllib.parse
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category

def home(request):
    featured_products = Product.objects.all()[:4]
    categories = Category.objects.all()
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    products = Product.objects.all().order_by('-id')
    categories = Category.objects.all()

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    if request.method == 'POST':
        product_id = str(request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity', 1))

        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity

        request.session['cart'] = cart
        return redirect('cart')

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            continue

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'store/cart.html', context)

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
    return redirect('cart')

def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            continue

    if request.method == 'POST':
        # Dòng này sẽ xóa toàn bộ dữ liệu giỏ hàng lưu trong session, giỏ hàng sẽ trở về trạng thái rỗng sau khi thanh toán thành công
        request.session['cart'] = {} 
        return render(request, 'store/order_success.html')

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'store/checkout.html', context)

def wishlist(request):
    wishlist_ids = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids)
    return render(request, 'store/wishlist.html', {'products': products})


def add_to_wishlist(request, product_id):
    wishlist_ids = request.session.get('wishlist', [])
    if product_id not in wishlist_ids:
        wishlist_ids.append(product_id)
        request.session['wishlist'] = wishlist_ids
    return redirect('wishlist')


def remove_from_wishlist(request, product_id):
    wishlist_ids = request.session.get('wishlist', [])
    if product_id in wishlist_ids:
        wishlist_ids.remove(product_id)
        request.session['wishlist'] = wishlist_ids
    return redirect('wishlist')

VNPAY_TMN_CODE = '2QX748P8'
VNPAY_HASH_SECRET = 'A2N8M0K1L2P3Q4R5S6T7U8V9W0X1Y2Z3'
VNPAY_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'

def create_vnpay_payment(request, order_id, amount):
    """Hàm tạo URL chuyển hướng sang VNPay Sandbox"""
    vnp_params = {
        'vnp_Version': '2.1.0',
        'vnp_Command': 'pay',
        'vnp_TmnCode': VNPAY_TMN_CODE,
        'vnp_Amount': int(amount * 100),  # VNPay tính đơn vị Đồng x 100
        'vnp_CurrCode': 'VND',
        'vnp_TxnRef': str(order_id),
        'vnp_OrderInfo': f'Thanh toan don hang {order_id}',
        'vnp_OrderType': 'billpayment',
        'vnp_Locale': 'vn',
        'vnp_ReturnUrl': request.build_absolute_uri('/vnpay-return/'),
        'vnp_IpAddr': '127.0.0.1',
        'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
    }

    # Sắp xếp các tham số theo alphabet
    sorted_params = sorted(vnp_params.items())
    query_string = urllib.parse.urlencode(sorted_params)
    
    # Tạo chuỗi Mã hóa Chữ ký an toàn (Secure Hash)
    hash_value = hmac.new(
        VNPAY_HASH_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()

    return f"{VNPAY_URL}?{query_string}&vnp_SecureHash={hash_value}"

def vnpay_return(request):
    """View nhận phản hồi từ VNPay sau khi khách bấm thanh toán (Webhook/Callback 5.3)"""
    vnp_response_code = request.GET.get('vnp_ResponseCode')
    
    if vnp_response_code == '00':  # Mã '00' nghĩa là Giao dịch Thành công
        request.session['cart'] = {}  # Xóa giỏ hàng
        return render(request, 'store/order_success.html', {'message': 'Thanh toán VNPay thành công!'})
    else:
        return redirect('checkout')