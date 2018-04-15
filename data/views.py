from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import UserForm, AirlineForm
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm


def login_profile(request):
    template = 'data/login.html'
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        else:
            user_form = AuthenticationForm()
            return render(request, template, {"user_form": user_form})

    else:
        user_form = AuthenticationForm(request, data=request.POST)
        if user_form.is_valid():
            username = request.POST.get('username', "")
            password = request.POST.get('password', "")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
        else:
            return render(request, template, {"user_form": user_form})


def logout_profile(request):
    logout(request)
    return redirect('/')


def reg_profile(request):
    template = 'data/reg.html'
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        else:
            user_form=UserForm()
            airline_form = AirlineForm()
            return render(request, template, {"user_form": user_form,
                                              "airline_form": airline_form})

    else:
        user_form = UserForm(request.POST)
        airline_form = AirlineForm(request.POST, request.FILES)
        if user_form.is_valid() and airline_form.is_valid():
            print("VALID")
            username = request.POST.get('username', "")
            email = request.POST.get('email', "")
            password = request.POST.get('password', "")

            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)
            user.save()
            form = airline_form.save(commit=False)
            form.account = user
            form.save()
            return redirect('/')
        else:
            return render(request, template, {"user_form": user_form,
                                              "airline_form": airline_form})


