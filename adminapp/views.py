from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render

from authapp.models import ShopUser
from mainapp.models import Product, ProductCategory
from authapp.forms import ShopUserRegisterForm
from adminapp.forms import ShopUserAdminEditForm, ProductCategoryEditForm, ProductEditForm

from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView, DeleteView, CreateView


class DispatchMixin:
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class UsersListView(DispatchMixin, ListView):
    model = ShopUser
    template_name = 'adminapp/users.html'
    context_object_name = 'objects'
    paginate_by = 2
    extra_context = {'title': 'админка/пользователи'}

    # def get_context_data(self, **kwargs):
    #     context = super(UsersListView, self).get_context_data(**kwargs)
    #     context['title'] = 'админка/пользователи'
    #     return context


class UserCreateView(DispatchMixin, CreateView):
    model = ShopUser
    template_name = 'adminapp/user_update.html'
    success_url = reverse_lazy('admin_staff:users')
    fields = '__all__'
    extra_context = {'title': 'пользователи/создание'}


class UserUpdateView(DispatchMixin, UpdateView):
    model = ShopUser
    template_name = 'adminapp/user_update.html'
    success_url = reverse_lazy('admin_staff:users')
    fields = '__all__'
    extra_context = {'title': 'пользователи/редактирование'}

    def get_form(self, form_class=None):
        form = super().get_form()
        for field_name, field in form.fields.items():
            if not field_name.startswith('is_'):
                field.widget.attrs['class'] = 'form-control'
        return form


class UserDeleteView(DeleteView):
    model = ShopUser
    success_url = reverse_lazy('admin_staff:users')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_active:
            self.object.is_active = False
        else:
            self.object.is_active = True
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class CategoriesListView(DispatchMixin, ListView):
    model = ProductCategory
    template_name = 'adminapp/categories.html'
    context_object_name = 'objects'
    paginate_by = 2
    extra_context = {'title': 'админка/категории'}


class CategoryCreateView(DispatchMixin, CreateView):
    model = ProductCategory
    template_name = 'adminapp/category_update.html'
    success_url = reverse_lazy('admin_staff:categories')
    fields = '__all__'
    extra_context = {'title': 'категории/создание'}


class CategoryUpdateView(DispatchMixin, UpdateView):
    model = ProductCategory
    template_name = 'adminapp/category_update.html'
    success_url = reverse_lazy('admin_staff:categories')
    fields = '__all__'
    extra_context = {'title': 'категории/редактирование'}

    def get_form(self, form_class=None):
        form = super().get_form()
        for field_name, field in form.fields.items():
            if not field_name.startswith('is_'):
                field.widget.attrs['class'] = 'form-control'
        return form


class CategoryDeleteView(DeleteView):
    model = ProductCategory
    success_url = reverse_lazy('admin_staff:categories')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_active:
            self.object.is_active = False
        else:
            self.object.is_active = True
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class ProductsListView(DispatchMixin, ListView):
    model = Product
    template_name = 'adminapp/products.html'
    context_object_name = 'objects'
    ordering = ('-is_active', 'name')
    paginate_by = 3
    extra_context = {'title': 'админка/продукт'}

    def get_queryset(self):
        queryset = super(ProductsListView, self).get_queryset()
        queryset = [p for p in queryset if p.category_id == self.kwargs['pk']]
        return queryset


class ProductCreateView(DispatchMixin, CreateView):
    model = Product
    template_name = 'adminapp/user_update.html'
    # success_url = reverse_lazy('admin_staff:users')
    fields = '__all__'
    extra_context = {'title': 'продукт/создание'}

    def get_success_url(self):
        return reverse_lazy('admin_staff:products', kwargs={'pk': self.object.category_id})

    def get_form(self, form_class=None):
        category = get_object_or_404(ProductCategory, pk=self.kwargs['pk'])
        form = super().get_form()
        for field_name, field in form.fields.items():
            if field_name == 'category':
                field.initial = category
            if not field_name.startswith('is_'):
                field.widget.attrs['class'] = 'form-control'
        return form


class ProductUpdateView(DispatchMixin, UpdateView):
    model = Product
    template_name = 'adminapp/product_update.html'
    fields = '__all__'
    extra_context = {'title': 'продукт/редактирование'}

    def get_success_url(self):
        return reverse_lazy('admin_staff:products', kwargs={'pk': self.object.category_id})

    def get_form(self, form_class=None):
        form = super().get_form()
        for field_name, field in form.fields.items():
            if not field_name.startswith('is_'):
                field.widget.attrs['class'] = 'form-control'
        return form


class ProductDeleteView(DeleteView):
    model = Product

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_active:
            self.object.is_active = False
        else:
            self.object.is_active = True
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('admin_staff:products', kwargs={'pk': self.object.category_id})

