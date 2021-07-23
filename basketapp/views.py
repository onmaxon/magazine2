from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DeleteView, CreateView

from basketapp.models import Basket
from mainapp.models import Product
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import JsonResponse


class BasketView(ListView):
    model = Basket
    template_name = 'basketapp/basket.html'
    context_object_name = 'basket_items'
    ordering = 'product__price'
    extra_context = {'title': 'корзина'}

    def get_queryset(self):
        return super(BasketView, self).get_queryset().filter(user=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BasketView, self).dispatch(*args, **kwargs)


@login_required
def basket_add(request, pk):
    if 'login' in request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(reverse('products:product', args=[pk]))

    product = get_object_or_404(Product, pk=pk)
    basket = Basket.objects.filter(user=request.user, product=product).first()

    if not basket:
        basket = Basket(user=request.user, product=product)

    basket.quantity += 1
    basket.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class BasketDeleteView(DeleteView):
    model = Basket

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BasketDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


@login_required
def basket_edit(request, pk, quantity):
    if request.is_ajax():
        quantity = int(quantity)
        new_basket_item = Basket.objects.get(pk=int(pk))

        if quantity > 0:
            new_basket_item.quantity = quantity
            new_basket_item.save()
        else:
            new_basket_item.delete()

        basket_items = Basket.objects.filter(user=request.user).order_by('product__price')

        content = {
            'basket_items': basket_items,
        }

        result = render_to_string('basketapp/inc/inc_basket_list.html', content)

        return JsonResponse({'result': result})
