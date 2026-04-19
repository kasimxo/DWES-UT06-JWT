from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from datetime import datetime
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.db.models import Q
from ..models import User, Task

class TareasView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        if user.role == 'student':
            tareas = Task.objects.filter(Q(assigned_to=user) | Q(created_by=user)).distinct().order_by('-due_date')
        else:
            tareas = Task.objects.filter(created_by=user).order_by('-due_date')
        return render(request, "tareas/tareas.html", {"tareas": tareas, "page_title": "Tareas"})

class CreacionTareasView(LoginRequiredMixin, View):
    
    def get(self, request):
        users = User.objects.filter(role='student').exclude(id=request.user.id)
        return render(
            request, 
            "tareas/crear_tarea.html", 
            {"users": users,
             "page_title": "Crear Tarea"})

    def post(self, request):
        print("Datos recibidos en el POST:")
        print(request.POST)
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        due_date = request.POST.get("fecha_vencimiento")
        is_evaluable = request.POST.get("es_evaluable")
        grupal = request.POST.get("grupal")
        assigned_students_ids = request.POST.getlist("usuarios_asignados")

        if not all([titulo, descripcion, due_date, assigned_students_ids]):
            messages.error(request, "Los campos título, descripción, fecha de vencimiento y usuarios asignados son obligatorios.")
            return redirect("create_tarea")

        fecha_vencimiento = datetime.strptime(due_date, "%Y-%m-%d").date()

        if fecha_vencimiento < timezone.now().date():
            messages.error(request, "La fecha de vencimiento no puede ser anterior a la fecha actual.")
            return redirect("create_tarea")
        
        try:
            tarea = Task(
                title=titulo,
                description=descripcion,
                due_date=due_date,
                is_evaluable=is_evaluable == 'true',
                created_by=request.user,
            )
            tarea.save()
            tarea.assigned_to.set(User.objects.filter(id__in=assigned_students_ids))
            messages.success(request, "Tarea creada con éxito.")
            print(f"Tarea '{titulo}' creada con éxito.")
        except Exception as e:
            messages.error(request, f"Error al crear la tarea: {str(e)}")
            print(f"Error al crear la tarea: {str(e)}")
            return redirect("create_tarea")

        return redirect("tareas")


class CompletarTareasView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tareas/completar_tarea.html"
    context_object_name = "tarea"
    pk_url_kwarg = "tarea_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Completar Tarea: {self.object.title}"
        context['users'] = User.objects.filter(role='student').exclude(id=self.request.user.id)
        return context
    
    def post(self, request, tarea_id, *args, **kwargs):
        tarea = self.get_object()
        action = request.POST.get("action")
        if action == "guardar":
            respuesta = request.POST.get("respuesta")
            tarea.answer = respuesta
            tarea.save()
            messages.success(request, "Tarea guardada con éxito.")
            return redirect("tareas")
        elif action == "entregar":
            respuesta = request.POST.get("respuesta")
            tarea.answer = respuesta
            tarea.finished_at = timezone.now()
            tarea.save()
            messages.success(request, "Tarea entregada con éxito.")
            return redirect("tareas")

class EditarTareasView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tareas/editar_tarea.html"
    context_object_name = "tarea"
    pk_url_kwarg = "tarea_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Editar Tarea: {self.object.title}"
        context['users'] = User.objects.filter(role='student').exclude(id=self.request.user.id)
        return context
    
    def post(self, request, tarea_id, *args, **kwargs):
        tarea = self.get_object()
        action = request.POST.get("action")
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        due_date = request.POST.get("fecha_vencimiento")
        is_evaluable = request.POST.get("es_evaluable")
        grupal = request.POST.get("grupal")
        assigned_students_ids = request.POST.getlist("usuarios_asignados")

        if not all([titulo, descripcion, due_date, assigned_students_ids]):
            messages.error(request, "Los campos título, descripción, fecha de vencimiento y usuarios asignados son obligatorios.")
            return redirect("editar_tarea", tarea_id=tarea.id)

        fecha_vencimiento = datetime.strptime(due_date, "%Y-%m-%d").date()

        if fecha_vencimiento < timezone.now().date():
            messages.error(request, "La fecha de vencimiento no puede ser anterior a la fecha actual.")
            return redirect("editar_tarea", tarea_id=tarea.id)
        
        try:
            tarea.title = titulo
            tarea.description = descripcion
            tarea.due_date = due_date
            tarea.is_evaluable = is_evaluable == 'true'
            tarea.save()
            tarea.assigned_to.set(User.objects.filter(id__in=assigned_students_ids))
            messages.success(request, "Tarea editada con éxito.")
        except Exception as e:
            messages.error(request, f"Error al editar la tarea: {str(e)}")
            return redirect("editar_tarea", tarea_id=tarea.id)

        return redirect("tareas")
           

class DetalleTareasView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tareas/detalle_tarea.html"
    context_object_name = "tarea"
    pk_url_kwarg = "tarea_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Tarea: {self.object.title}"
        context['users'] = User.objects.filter(role='student').exclude(id=self.request.user.id)
        return context

class EvaluarTareasView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tareas/evaluar_tarea.html"
    context_object_name = "tarea"
    pk_url_kwarg = "tarea_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Evaluar tarea: {self.object.title}"
        context['users'] = User.objects.filter(role='student').exclude(id=self.request.user.id)
        return context
    
    def post(self, request, tarea_id, *args, **kwargs):
        tarea = self.get_object()
        action = request.POST.get("calificacion")
        if action in ['apto', 'no_apto']:
            tarea.evaluation = action
            tarea.save()
            messages.success(request, "Tarea evaluada con éxito.")
        else:
            messages.error(request, "Error al evaluar la tarea.")
        return redirect("tareas")
