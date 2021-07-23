import ordersapp.views as ordersapp
from django.urls import path

app_name = "ordersapp"

urlpatterns = [
    path('', ordersapp.OrderList.as_view(), name='list'),
    path('forming/complete/<int:pk>/', ordersapp.forming_complete, name='forming_complete'),
    path('create/', ordersapp.OrderCreate.as_view(), name='create'),
    path('read/<int:pk>/', ordersapp.OrderRead.as_view(), name='read'),
    path('update/<int:pk>/', ordersapp.OrderUpdate.as_view(), name='update'),
    path('delete/<int:pk>/', ordersapp.OrderDelete.as_view(), name='delete'),
    path('product/<int:pk>/price/', ordersapp.get_product_price),
]
