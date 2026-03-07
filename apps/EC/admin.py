from django.contrib import admin
from .models import Category,Product,Order,Cart,CartItem,Order,OrderItem,ProductImage

class ProductImageInline(admin.TabularInline):
    model=ProductImage
    extra=3
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines=[ProductImageInline]
    list_display=["name","price","stock","is_available"]
admin.site.register(Category)

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

# Register your models here.
