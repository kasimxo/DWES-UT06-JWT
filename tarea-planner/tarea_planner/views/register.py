from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views import View
from .usuarios import User

User = get_user_model()

class RegisterView(View):

    def get(self, request):
        return render(request, "register/register.html", {"page_title": "Registrar Usuario"})
    
    def post(self, request):

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if not all([first_name, last_name, email, password, role]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("register")

        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            user.save()
            messages.success(request, "Usuario registrado con éxito.")
            print(f"Usuario {email} {password} registrado con éxito.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Error al registrar el usuario: {str(e)}")
            return redirect("register")

