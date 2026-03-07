from django.db import models
from django.conf import settings

class Category(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural ="Categories"
        

        
class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    name=models.CharField(max_length=200)
    description=models.TextField()
    stock=models.PositiveIntegerField(default=0)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    image=models.ImageField(upload_to="products/",blank=True)
    is_available=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    @property
    def is_in_stock(self):
        return self.stock>0
class ProductImage(models.Model):
    product=models.ForeignKey(
        Product,
        on_delete=models.CASCADE,related_name='images'
    )
    image=models.ImageField(upload_to='products/')
    is_main=models.BooleanField(default=False)
    def __str__(self):
        return f"Image for {self.product.name}"
    
class Cart(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}'s cart"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart =models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    @property
    def subtotal(self):
        return self.product.price * self.quantity
    
class Order(models.Model):
    STATUS_CHOICES=[
        ("pending","Pending"),
        ("processing","Processing"),
        ("shipped","Shipped"),
        ("delivered","Delivered"),
        ("cancelled","Cancelled")
        
    ]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending")
    total=models.DecimalField(max_digits=10,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    @property
    def subtotal(self):
        return self.price*self.quantity
    
    
    