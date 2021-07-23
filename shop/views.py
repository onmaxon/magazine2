from django.shortcuts import render


def main(request):
    context = {
        'title': 'Главная'
    }
    return render(request, 'index.html', context=context)


def contact(request):
    context = {
        'title': 'Контакты'
    }
    return render(request, 'contact.html', context=context)