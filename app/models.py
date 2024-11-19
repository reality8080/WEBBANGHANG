from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
# Create your models here.
class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email','first_name','last_name', 'password1', 'password2']
        
# class Customer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=False)
#     name = models.CharField(max_length=200, null=True)
#     email = models.CharField(max_length=200, null=True)
    
#     def __str__(self):
#         return self.name

class Product(models.Model):
    category = models.ManyToManyField('Category', related_name='product')
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(max_length=200, null=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    detail = models.TextField(null=True,blank = True)
    def __str__(self):
        return self.name

    @property
    def IMAGEURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    
    def __str__(self):
        return str(self.id)

    @property
    def get_cart_items(self):
        order_items = self.ordertime_set.all()  # Use the correct reverse relationship name
        total = sum([item.quantity for item in order_items])
        return total

    @property
    def get_cart_total(self):
        order_items = self.ordertime_set.all()  # Use the correct reverse relationship name
        total = sum([item.get_total for item in order_items])
        return total

class OrderTime(models.Model):  # Consider renaming to OrderItem for clarity
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddreess(models.Model):  # Corrected the spelling from "ShippingAddreess"
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)  # Changed to auto_now_add for consistency
    
    def __str__(self):
        return self.address
class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True)
    def __str__(self):
        return self.name