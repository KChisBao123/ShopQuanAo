from django.contrib import admin
from .models import Category, Vendor, Product, ProductImages, Color, Size

# Register your models here.
class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['title', 'price', 'in_stock', 'featured']
    filter_horizontal = ('color', 'size')

admin.site.register(Category)
admin.site.register(Vendor)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImages)
admin.site.register(Color)
admin.site.register(Size)