from django.urls import path
from django.contrib.auth.views import LoginView
from .views import RegisterView, HomeView, TareasView, CreacionTareasView, ListadoUsuariosView, PerfilUsuarioView, EditarTareasView, DetalleTareasView, EvaluarTareasView, CompletarTareasView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='login/login.html', redirect_authenticated_user=True, extra_context={'page_title': 'Iniciar sesión'}), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('tareas/', TareasView.as_view(), name='tareas'),
    path('tareas/<uuid:tarea_id>/editar', EditarTareasView.as_view(), name='editar_tarea'),
    path('tareas/<uuid:tarea_id>/completar', CompletarTareasView.as_view(), name='completar_tarea'),
    path('tareas/<uuid:tarea_id>/detalle', DetalleTareasView.as_view(), name='detalle_tarea'),
    path('tareas/<uuid:tarea_id>/evaluar', EvaluarTareasView.as_view(), name='evaluar_tarea'),
    path('tareas/crear/', CreacionTareasView.as_view(), name='create_tarea'),
    
    # Endpoints viejos, sin proteger
    # path('usuarios/', ListadoUsuariosView.as_view(), name='usuarios'),
    # path('usuarios/<uuid:user_id>/', PerfilUsuarioView.as_view(), name='usuario'),    

    # Nuevos endpoints, protegidos con JWT
    path('api/users/', ListadoUsuariosView.as_view(), name='usuarios'),
    path('api/users/<uuid:user_id>/', PerfilUsuarioView.as_view(), name='usuario'),
    # path('api/users/perfil/', PerfilView.as_view(), name='perfil'),
    path('api/users/auth/logout/', LogoutView.as_view(), name='logout'),
]
