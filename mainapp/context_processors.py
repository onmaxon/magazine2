from basketapp.models import Basket


def basket(request):
    basket_list = []
    if request.user.is_authenticated:
#        basket_list = Basket(user=request.user).get_items_cached
        basket_list = Basket.get_items(request.user).select_related()
#        basket_list = Basket.objects.filter(user=request.user).select_related()
    return {
        'basket': basket_list
    }
