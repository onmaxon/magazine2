from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from django.conf import settings
from .models import ProductCategory, Product
from basketapp.models import Basket
import random


def get_links_menu():
    if settings.LOW_CACHE:
        key = 'links_menu'
        links_menu = cache.get(key)
        if links_menu is None:
            links_menu = ProductCategory.objects.filter(is_active=True)
            cache.set(key, links_menu)
        return links_menu
    else:
        return ProductCategory.objects.filter(is_active=True)


def get_category(pk):
    if settings.LOW_CACHE:
        key = f'category_{pk}'
        category = cache.get(key)
        if category is None:
            category = get_object_or_404(ProductCategory, pk=pk)
            cache.set(key, category)
        return category
    else:
        return get_object_or_404(ProductCategory, pk=pk)


def get_products():
    if settings.LOW_CACHE:
        key = 'products'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, category__is_active=True).select_related('category')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True, category__is_active=True).select_related('category')


def get_product(pk):
    if settings.LOW_CACHE:
        key = f'product_{pk}'
        product = cache.get(key)
        if product is None:
            product = get_object_or_404(Product, pk=pk)
            cache.set(key, product)
        return product
    else:
        return get_object_or_404(Product, pk=pk)


def get_products_oredered_by_price():
    if settings.LOW_CACHE:
        key = 'products_oredered_by_price'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, category__is_active=True).order_by('price')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True, category__is_active=True).order_by('price')


def get_products_in_category_oredered_by_price(pk):
    if settings.LOW_CACHE:
        key = f'products_in_category_oredered_by_price_{pk}'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(category__pk=pk, is_active=True, category__is_active=True).order_by('price')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(category__pk=pk, is_active=True, category__is_active=True).order_by('price')


class ProductsView(ListView):
    model = Product
    ordering = 'price'
    context_object_name = 'products'
    paginate_by = 3

    def get_template_names(self):
        if 'pk' in self.kwargs:
            return ['mainapp/products_list.html']
        else:
            return ['mainapp/products.html']

    # def get_basket(self):
    #     if self.request.user.is_authenticated:
    #         return Basket.objects.filter(user=self.request.user)
    #     else:
    #         return []

    def get_hot_product(self):
        products = get_products()
        return random.sample(list(products), 1)[0]
#        return random.sample(list(self.get_queryset()), 1)[0]

    def get_same_products(self, ):
        hot_product = self.get_hot_product()
        same_products = self.get_queryset().filter(category=hot_product.category).exclude(pk=hot_product.pk)[:3]
        return same_products

    def get_queryset(self):
        queryset = get_products_oredered_by_price()
        # queryset = super(ProductsView, self).get_queryset()
        if 'pk' in self.kwargs:
            if self.kwargs['pk'] == 0:
                return queryset
            else:
                # queryset = queryset.filter(category_id__pk=self.kwargs['pk'])
                # return queryset
                return get_products_in_category_oredered_by_price(self.kwargs['pk'])
        else:
            return queryset

    def get_category(self):
        if 'pk' in self.kwargs:
            if self.kwargs['pk'] == 0:
                category = {
                    'pk': 0,
                    'name': 'все'}
            else:
                category = get_category(self.kwargs['pk'])
#                category = get_object_or_404(ProductCategory, pk=self.kwargs['pk'])
            return category

    def get_context_data(self, **kwargs):
        context = super(ProductsView, self).get_context_data(**kwargs)
        # context['basket'] = self.get_basket()
        context['title'] = 'продукты'
        context['links_menu'] = get_links_menu()
        context['category'] = self.get_category()
        context['hot_product'] = self.get_hot_product()
        context['same_products'] = self.get_same_products()
        return context


class ProductView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'mainapp/product.html'

    # def get_basket(self):
    #     if self.request.user.is_authenticated:
    #         return Basket.objects.filter(user=self.request.user)
    #     else:
    #         return []
    def get_object(self, queryset=None):
        return get_product(self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        # context['basket'] = self.get_basket()
        context['title'] = 'продукт'
        context['links_menu'] = get_links_menu()

        return context
