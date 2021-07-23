from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db import transaction
from django.db.models.signals import pre_save, pre_delete

from django.forms import inlineformset_factory
from django.utils.decorators import method_decorator

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from basketapp.models import Basket
from mainapp.models import Product
from ordersapp.models import Order, OrderItem
from ordersapp.forms import OrderItemForm


class FormValidMixin:

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            assert isinstance(self.request.user, object)
            form.instance.user = self.request.user
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

        if self.object.get_total_cost() == 0:
            self.object.delete()
        return super().form_valid(form)


class DispatchMixin:
    @method_decorator(login_required())
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class OrderList(DispatchMixin, FormValidMixin, ListView):
    model = Order
    extra_context = {'title': 'Список заказов'}

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreate(DispatchMixin, FormValidMixin, CreateView):
    model = Order
    fields = []
    success_url = reverse_lazy('order:list')
    extra_context = {'title': 'Создание заказа'}

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFormSet(self.request.POST)
        else:
            basket_items = Basket.objects.filter(user=self.request.user)
            if len(basket_items):
                OrderFormSet = inlineformset_factory(
                    Order,
                    OrderItem,
                    form=OrderItemForm,
                    extra=len(basket_items) + 1)
                formset = OrderFormSet()
                for num, form in enumerate(formset.forms):
                    if num < len(basket_items):
                        form.initial['product'] = basket_items[num].product
                        form.initial['quantity'] = basket_items[num].quantity
                        form.initial['price'] = basket_items[num].product.price
                basket_items.delete()
            else:
                formset = OrderFormSet()

        data['orderitems'] = formset
        return data


class OrderRead(DispatchMixin, DetailView):
    model = Order
    extra_context = {'title': 'Просмотр заказа'}


class OrderUpdate(DispatchMixin, FormValidMixin, UpdateView):
    model = Order
    fields = []
    success_url = reverse_lazy('order:list')
    extra_context = {'title': 'Изменение заказа'}

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFormSet(self.request.POST, instance=self.object)
        else:
            queryset = self.object.orderitems.select_related()
#            formset = OrderFormSet(instance=self.object)
            formset = OrderFormSet(instance=self.object, queryset=queryset)
            for form in formset.forms:
                if form.instance.pk:
                    form.initial['price'] = form.instance.product.price

        data['orderitems'] = formset
        return data


class OrderDelete(DispatchMixin, DeleteView):
    model = Order
    success_url = reverse_lazy('order:list')
    extra_context = {'title': 'Удаление заказа'}


def forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.SENT_TO_PROCEED
    order.save()

    return HttpResponseRedirect(reverse('order:list'))


@receiver(pre_save, sender=Basket)
@receiver(pre_save, sender=OrderItem)
def product_quantity_update_save(sender, update_fields, instance, **kwargs):
    if instance.pk:
        instance.product.quantity -= instance.quantity - sender.get_item(instance.pk).quantity
    else:
        instance.product.quantity -= instance.quantity
    instance.product.save()


@receiver(pre_delete, sender=OrderItem)
@receiver(pre_delete, sender=Basket)
def product_quantity_update_delete(sender, instance, **kwargs):
    instance.product.quantity += instance.quantity
    instance.product.save()


def get_product_price(request, pk):
    if request.is_ajax():
        product = Product.objects.filter(pk=pk).first()
        print(product)
        if product:
            return JsonResponse({'price': product.price})
        else:
            return JsonResponse({'price': 0})
