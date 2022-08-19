from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.views.generic import DetailView
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url
from django.contrib import messages
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.http import HttpResponseRedirect, JsonResponse

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from .forms import UserForm, ProfileForm
from .decorators import authenticated_or_404
from .models import User, Profile
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer


class SuccessURLAllowedHostsMixin(object):
    success_url_allowed_hosts = set()

    def get_success_url_allowed_hosts(self):
        allowed_hosts = {self.request.get_host()}
        allowed_hosts.update(self.success_url_allowed_hosts)
        return allowed_hosts


class LoginView(SuccessURLAllowedHostsMixin, FormView):
    """
    Displays the login form and handles the login action.
    """
    form_class = AuthenticationForm
    authentication_form = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'account/login.html'
    redirect_authenticated_user = True
    extra_context = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_form_class(self):
        return self.authentication_form or self.form_class

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    # def get_context_data(self, **kwargs):
    #     context = super(LoginView, self).get_context_data(**kwargs)
    #     current_site = get_current_site(self.request)
    #     context.update({
    #         self.redirect_field_name: self.get_redirect_url(),
    #         'site': current_site,
    #         'site_name': current_site.name,
    #     })
    #     if self.extra_context is not None:
    #         context.update(self.extra_context)
    #     return context


@method_decorator(authenticated_or_404, name='dispatch')
class ProfileDetailView(DetailView):
    """
    Displays the login form and handles the login action.
    """
    form_class = ProfileForm
    template_name = 'account/profile.html'

    def get(self, request, *args, **kwargs):
        # form = self.form_class(initial=self.initial)
        # return render(request, self.template_name, {'form': form})
        return render(request, self.template_name)

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileDetailView, self).dispatch(request, *args, **kwargs)


def signup(request):
    from django.contrib.auth.forms import UserCreationForm
    from django.contrib.auth import login, authenticate
    from modules.main.account.forms import SignUpForm

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})


@login_required
def userDashboard(request):
    return render(request, 'account/dashboard.html')



@login_required
def userSettings(request):
    user_form = UserForm(request.POST or None, instance=request.user)
    profile_instance = Profile.objects.get(user=request.user)
    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=profile_instance)
    if request.method == 'POST':
        # print(user_form)
        print(profile_form.errors)
        if user_form.is_valid() and profile_form.is_valid():
            user_form_obj = user_form.save(commit=False)
            user_form_obj.save()
            profile_form.save()
            messages.success(request, 'Successfully updated user information')
        return redirect('userSettings')
    return render(request, 'account/settings.html', {
                           'user_form': user_form,
                           'profile_form': profile_form})


@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def api_login(request):
    """
    List all code snippets, or create a new snippet.
    """
    # if request.method == 'GET':
    #     tasks = Task.objects.all()
    #     serializer = TaskSerializer(tasks, many=True)
    #     return Response(data)

    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)
        # serializer = SnippetSerializer(data=data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return JsonResponse(serializer.data, status=201)
        # return JsonResponse(serializer.errors, status=400)
        return JsonResponse(data, status=201)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def api_getUserDetails(request):
    """
    List user profile details.
    """
    if request.method == 'GET':
        # tasks = Task.objects.order_by('-date_created')
        print('####################')
        print(request.user)
        user = User.objects.get(pk=request.user.pk)
        print(user)
        serializer = UserSerializer(user)
        return Response(serializer.data)


# class HelloView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         content = {'message': 'Hello, World!'}
#         return Response(content)
