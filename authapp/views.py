from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import render, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, CreateView

from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm, ShopUserEditForm, ShopUserProfileEditForm
from django.contrib import auth
from django.urls import reverse, reverse_lazy

from authapp.models import ShopUser


@csrf_exempt
def login(request):
    title = 'вход'
    login_form = ShopUserLoginForm(data=request.POST or None)
    next = request.GET['next'] if 'next' in request.GET.keys() else ''

    if request.method == "POST" and login_form.is_valid():
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            if 'next' in request.POST.keys():
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect(reverse('index'))

    context = {
        'title': title,
        'login_form': login_form,
        'next': next
    }

    return render(request, 'authapp/login.html', context)

# class MyLoginView(LoginView):
#     authentication_form = ShopUserLoginForm
#     template_name = 'authapp/login.html'
#     extra_context = {'title': 'вход'}



class MyLogoutView(LogoutView):
    next_page = reverse_lazy('index')


class UserRegisterView(CreateView):
    model = ShopUser
    form_class = ShopUserRegisterForm
    template_name = 'authapp/register.html'
    success_url = reverse_lazy('auth:login')
    extra_context = {'title': 'регистрация'}

    def send_verify_link(self):
        verify_link = reverse('auth:verify', args=[self.object.email, self.object.activation_key])
        subject = 'account verify'
        message = f'Verify link: \n{settings.DOMAIN_NAME}{verify_link}'
        return send_mail(subject, message, settings.EMAIL_HOST_USER, [self.object.email], fail_silently=False)

    def form_valid(self, form):
        user = super(UserRegisterView, self).form_valid(form)
        self.send_verify_link()
        return user


class UserUpdateView(UpdateView):
    model = ShopUser
    form_class = ShopUserEditForm
    template_name = 'authapp/edit.html'
    success_url = reverse_lazy('auth:edit')
    extra_context = {'title': 'редактирование'}

    @method_decorator(login_required())
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['profile_form'] = ShopUserProfileEditForm(instance=self.request.user.shopuserprofile)
        return context

    # по сигналу не сохраняет форму профиля, нашел такое решение
    # def profile_post(self, request):
    #     profile_form = ShopUserProfileEditForm(request.POST, instance=self.request.user.shopuserprofile)
    #     if profile_form.is_valid():
    #         return profile_form

    def post(self, request, *args, **kwargs):
        profile_form = ShopUserProfileEditForm(request.POST, instance=self.request.user.shopuserprofile)
        if profile_form.is_valid():
            profile_form.save()
        return super(UserUpdateView, self).post(request, *args, **kwargs)


def verify(request, email, key):
    user = ShopUser.objects.filter(email=email).first()
    if user and user.activation_key == key and not user.is_activation_key_expired():
        user.is_active = True
        user.activation_key = ''
        user.activation_key_created = None
        user.save()
        auth.login(request, user, backend='backends')
        # я правильно понимаю, что контекстный процессор хранит в себе путь ко всем вариантам бэкенда
        # из AUTHENTICATION_BACKENDS? и как идет процесс выбора нужного?
    return render(request, 'authapp/verify.html')
