import random
import string

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def random_slug():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)

 
    class Meta:
        unique_together = (['slug', 'parent'])
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' > '.join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(random_slug() + '-pickBetter' + self.name)
            return super(Category, self).save(*args, **kwargs)
        
    # def get_absolute_url(self):
    #     return reverse('model_detail', kwargs={'pk': self.pk})


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField('URL', max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=99.99)
    image = models.ImageField(upload_to='products/products/%Y/%m/%d')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('model_detail', kwargs={'pk': self.pk})
    
class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(available=True)


class ProductProxy(Product):

    objects = ProductManager()

    class Meta:
        proxy = True