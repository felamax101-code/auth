from rest_framework import serializers
from apps.EC.models import Category,Product,Order,Cart,CartItem,Order,OrderItem,ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=["id","name","description"]
        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductImage
        fields=["id","image","is_main"]
        
class ProductSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source="category.name",read_only=True)
    is_in_stock=serializers.BooleanField(read_only=True)
    images=ProductImageSerializer(many=True,read_only=True)
    class Meta:
        model=Product
        fields=["id","name","description","price","stock","image","images","is_available",
                "is_in_stock","category","category_name","created_at"]
        def validate_price(self,value):
            if value<=0:
                raise serializers.ValidationError("Price must be greater than zero")
            return value
        def validate_stock(self,value):
            if value<=0:
                raise serializers.ValidationError("stock cannot be negative")
            return value
                
class CartItemSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="product.name",read_only=True)
    product_price=serializers.DecimalField(source="product.price",max_digits=10,decimal_places=2,read_only=True)
    subtotal=serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    class Meta:
        model=CartItem
        fields=["id","product","product_name","product_price","quantity","subtotal"]
        def validate_quantity(self,value):
            if value<=0:
                raise serializers.ValidationError("quantity must be at least 1")
        def validate (self,data):
            product=data.get("product")
            quantity=data.get("quantity")
            if not product.is_available:
                raise  serializers.ValidationError("this produt is not available")
            if not product.is_in_stock:
                raise  serializers.ValidationError("This product is out of stock")
            if quantity> product.stock:
                raise  serializers.ValidationError(f"Only {product.stock} items available in stock")
                
            return data
class CartSerializer(serializers.ModelSerializer):
    items=CartItemSerializer(many=True,read_only=True)
    total=serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    class Meta:
        model=Cart
        fields=["id","items","total"]
        
class OrderItemSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="product.name",read_only=True)
    subtotal=serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    class Meta:
        model=OrderItem
        fields=["id","product_name","quantity","price","subtotal"]
        
class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    username=serializers.CharField(source="user.username",read_only=True)
    class Meta:
        model=Order
        fields=["id","username","status","total","items","created_at"]
    