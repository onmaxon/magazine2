from django.urls import path
from .views import ProductsView, ProductView

app_name = 'mainapp'

urlpatterns = [
    path('', ProductsView.as_view(), name='products'),
    path('category/<int:pk>/', ProductsView.as_view(), name='category'),
    # path('category/<int:pk>/page/<int:page>', ProductsView.as_view(), name='page'),
    path('product/<int:pk>/', ProductView.as_view(), name='product'),
]
