from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from apps.EC.models import Category,Product,Cart,CartItem,Order,OrderItem
from apps.EC.serializers import OrderSerializer,OrderItemSerializer,CartSerializer,ProductSerializer,CategorySerializer,CartItemSerializer

class CategoryView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        categories=Category.objects.all()
        serializer=CategorySerializer(categories,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,request):
        if not request.user.is_staff:
            return Response(
                {
                    "detail":"Only admins can create categories"
                },status=status.HTTP_403_FORBIDDEN
            )
        serializer=CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status.HTTP_400_BAD_REQUEST)

class ProductView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        products=Product.objects.filter(is_available=True)
        category=request.query_params.get("category")
        if category:
            products=products.filter(category=category)
        search=request.query_params.get("search")
        if search:
            products=products.products.filter(name__icontains=search)
        serializer=ProductSerializer(products,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,request):
        if not request.user.is_staff:
            return Response(
                {
                    "detail":"Only admins can create products"
                },status=status.HTTP_403_FORBIDDEN
            )
        serializer=ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status.HTTP_400_BAD_REQUEST)
class ProductDetailView(APIView):
    permission_classes=[IsAuthenticated]
    def get_object(self,pk):
        try:
            return Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return None
         
    def get(self,request,pk):
        product=self.get_object(pk)
        if not product:
            return Response(
                {
                    "detail":"Product not found"
                },status=status.HTTP_404_NOT_FOUND
            )
        serializer=ProductSerializer(product)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def put(self,request,pk):
        if not request.user.is_staff:
            return Response(
                {
                    "detail":"Only admins can update products"
                },status=status.HTTP_403_FORBIDDEN)
        product =self.get_object(pk)
        if not product:
            return Response(
                {
                    "detail":"Product not found"
                },status=status.HTTP_404_NOT_FOUND)
        serializer=ProductSerializer(product,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        if not request.user.is_staff:
            return Response(
                {
                    "detail":"Only admins can delete products"
                },status=status.HTTP_403_FORBIDDEN)
        product =self.get_object(pk)
        if not product:
            return Response(
                {
                    "detail":"Product not found"
                },status=status.HTTP_404_NOT_FOUND)
            
        product.delete()
        return Response(
            {"detail":"Product delete"},status=status.HTTP_204_NO_CONTENT
        )
        
class CartView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        cart,created=Cart.objects.get_or_create(user=request.user)
        serializer=CartSerializer(cart)
        return Response(serializer.data,status=status.HTTP_200_OK)
class CartItemView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        cart,created=Cart.objects.get_or_create(user=request.user)
        serializer=CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product=serializer.validated_data["product"]
            quantity=serializer.validated_data["quantity"]
            cart_item,created=CartItem.objects.get_or_create(cart=cart,product=product,defaults={"quantity":quantity})
            if not created:
                cart_item.quantity+=quantity
                cart_item.save()
            return Response(
                CartSerializer(cart).data,
                status=status.HTTP_200_OK
            )  
        return Response (status=status.HTTP_400_BAD_REQUEST)  
    def delete(self,request,pk):
        cart,created=Cart.objects.get_or_create(user=request.user) 
        try:
            cart_item=CartItem.objects.get(id=pk,cart=cart)
            cart_item.delete()
            return Response(
                {
                    "detail":"item removed in cart"},
                    status=status.HTTP_400_NO_CONTENT
                )
        except CartItem.DoesNotExist:
            return Response(
                {
                    "detail":"item not found in cart"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
             
class CheckoutView(APIView):
    

    def post(self, request):
        # get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # check cart has items
        if not cart.items.exists():
            return Response(
                {"detail": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # create order
        order = Order.objects.create(
            user=request.user,
            total=cart.total,
            status='pending'
        )

        # create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price  # save current price
            )
            # reduce stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # clear the cart after checkout
        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
            
    
