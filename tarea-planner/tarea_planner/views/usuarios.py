from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic.detail import DetailView
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from tarea_planner.serializers import UserSerializer

User = get_user_model()

class ListadoUsuariosView(generics.ListCreateAPIView):
    """
    GET: Listar todos los socios (requiere autenticación)
    POST: Crear nuevo socio (requiere autenticación)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
"""
class ListadoUsuariosView(LoginRequiredMixin, View):

    def get(self, request):
        usuarios = User.objects.all()
        return render(request, "usuarios/listado_usuarios.html", {"usuarios": usuarios, "page_title": "Listado de Usuarios"})
"""

class PerfilUsuarioView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtener detalle de un socio
    PUT/PATCH: Actualizar socio
    DELETE: Eliminar socio
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

"""
class PerfilUsuarioView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "usuarios/perfil_usuario.html"
    context_object_name = "usuario"
    pk_url_kwarg = "user_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Perfil de {self.object.get_full_name()}"
        return context
"""

class LogoutView(APIView):
    """
    POST: Invalidar el refresh token (logout)
    Requiere enviar el refresh token en el body
    """

    # authentication_classes = [JWTAuthentication]  # No requiere autenticación para acceder a este endpoint
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            print("test")
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # Añade a lista negra
            
            return Response(
                {'mensaje': 'Logout exitoso, token invalidado'}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )