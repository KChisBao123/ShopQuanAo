from django.db import models
from userauth.models import User

# Create your models here.
class Category(models.Model):
    cid = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100, verbose_name='Tên danh mục')
    image = models.ImageField(upload_to='category', verbose_name='Ảnh đại diện')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Vendor(models.Model):
    vid         = models.CharField(max_length=100, unique=True)
    title       = models.CharField(max_length=100, verbose_name="Tên brand")
    image       = models.ImageField(upload_to=user_directory_path, verbose_name="Logo brand")
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả brand")
    user        = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Color(models.Model):
    title      = models.CharField(max_length=100)
    color_code = models.CharField(max_length=10)

    def __str__(self):
        return self.title

class Size(models.Model):
    title = models.CharField(max_length=100)   # Ví dụ: S, M, L, XL

    def __str__(self):
        return self.title

class Product(models.Model):
    pid            = models.CharField(max_length=100, unique=True)
    title          = models.CharField(max_length=100, verbose_name="Tên sản phẩm")
    image          = models.ImageField(verbose_name="Ảnh chính")
    description    = models.TextField(null=True, blank=True, verbose_name="Mô tả")
    specifications = models.TextField(null=True, blank=True)

    price     = models.IntegerField(verbose_name="Giá bán")
    old_price = models.IntegerField(verbose_name="Giá cũ")

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)

    in_stock = models.BooleanField(default=True, verbose_name='Còn hàng')
    featured = models.BooleanField(default=False, verbose_name='Sản phẩm nổi bật')

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    color = models.ManyToManyField(Color, blank=True)
    size  = models.ManyToManyField(Size,  blank=True)


    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title
    
    def get_percentage(self):
        if self.old_price > 0:
            return round((self.old_price - self.price)/self.old_price * 100)
        return 0

class ProductImages(models.Model):
    images  = models.ImageField(upload_to="product-images", verbose_name="Ảnh phụ")
    related_name="p_images"
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="p_images")
    date    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"