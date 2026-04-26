from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name=models.CharField(max_length=100, verbose_name="Categories")
    slug=models.CharField(max_length=100, unique=True)
    
    def save(self, *args, **kwargs): 
        if not self.slug:
            self.slug= slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    
class SizeAttribute(models.Model):

    TYPE_CHOICES = [
        ('volume', 'Объем (мл)'),
        ('diameter', 'Диаметр (см)'),
        ('height', 'Высота (см)'),
        ('width', 'Ширина (см)'),
        ('depth', 'Глубина (см)'),
        ('length', 'Длина (см)'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='size_attributes')
    attribute_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.category.name} - {self.get_attribute_type_display()}"
    class Meta:
        unique_together = ['category', 'attribute_type']
        
class ProductSize(models.Model):
    product=models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_sizes')
    size=models.ForeignKey(SizeAttribute,on_delete=models.CASCADE)
    stock=models.PositiveIntegerField(default=0)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        unique_together = ['product', 'size', 'value']
    def __str__(self):
        return f"{self.size.get_attribute_type_display()} ({self.stock} шт.) для {self.product.name}"
    
class Product(models.Model):    
    name=models.CharField(max_length=100)
    slug=models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    main_image=models.ImageField(upload_to="products/")
    GLAZE_CHOICES = [
    ('matte', 'Матовая'),
    ('glossy', 'Глянцевая'),
    ('reactive', 'Реактивная'),
    ('none', 'Без глазури'),
    ]
    glaze_type = models.CharField(max_length=20, choices=GLAZE_CHOICES, blank=True)
    def save(self, *args, **kwargs): 
        if not self.slug:
            self.slug= slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image=models.ImageField(upload_to="products/extra/")
