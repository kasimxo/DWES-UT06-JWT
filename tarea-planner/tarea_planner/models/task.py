import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .user import User
from django.utils import timezone

"""
Para el modelo de tarea, necesito:
- Título
- Descripción
- Fecha de entrega

Como una tarea puede estar asignada un alumno o a varios,
haré una relación ManyToMany con el modelo User

Voy a meter también un campo de "Respuesta"
Este campo sólo see podrá rellenar en la "edición" de la tarea por el alumno
También voy a meter un campo de evaluable, que será un boolean
Si la tarea es evaluable, una vez sea entregada, le aparecerá al profesor para poder ponerla apta/no apta
También voy a meter un campo de evaluación, que será nulable (para las tareas no evaluables) o apto/no apto
Y por último, la fecha de entrega, para que el alumno pueda darla por "finalizada/entregada"

Una tarea finalizada/entregada no se podrá editar por el alumno, sólo se podrá evaluar por el profesor
"""
class Task(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
        )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='created_tasks'
        )
    title = models.CharField(max_length=200)
    description = models.TextField()
    answer = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    assigned_to = models.ManyToManyField(
        User, 
        related_name='tasks',
        blank=True
        )
    is_evaluable = models.BooleanField(default=False)
    EVALUATION_CHOICES = [
        ('apto', 'Apto'),
        ('no_apto', 'No Apto'),
    ]
    evaluation = models.CharField(
        max_length=10, 
        choices=EVALUATION_CHOICES, 
        blank=True, 
        null=True
        )
    finished_at = models.DateTimeField(blank=True, null=True)   
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - Assigned to: {', '.join([ user.first_name + ' ' + user.last_name for user in self.assigned_to.all()])}"
    
    @property
    def estado_evaluacion(self):
        now = timezone.now()

        if not self.is_evaluable:
            return "No evaluable"
        if self.evaluation:
            return self.get_evaluation_display()
        if self.finished_at and self.finished_at <= now:
            return "Pendiente"
        if self.due_date and self.due_date > now:
            return "En progreso"
        if self.due_date and self.due_date <= now and self.finished_at is None:
            return "No entregada"

        return "-"
    
    @property
    def grupal(self):
        return self.assigned_to.count() > 1