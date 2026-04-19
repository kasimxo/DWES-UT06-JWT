# Tarea Planner

## Índice

- [Introducción](#introducción)
- [Requerimientos](#requerimientos)
- [Instalación y uso](#instalación-y-uso)
- [Arquitectura](#arquitectura)
- [Modelado de datos](#modelado-de-datos)
    - [User](#user)
    - [Task](#task)
- [Vistas](#vistas)
- [Esquema ER](#esquema-er)
- [Base de datos](#base-de-datos)
    - [Psycopg2-binary](#psycopg2-binary)
    - [Configuración PostgreSQL](#configuración-postgresql)
- [Migraciones](#migraciones)
- [Gitignore](#gitignore)
- [Posibles mejoras](#posibles-mejoras)
- [Créditos](#créditos)

## Introducción

Aplicación web desarrollada con Django para la gestión de tareas. Permite la creación de tareas, asignación a usuarios, trabajar en ellas, editarlas, entregarlas y evaluarlas.

Estas acciones dependen del tipo de usuario, distinguiendo profesores y alumnos.

## Requerimientos

Para ejecutar la aplicación en el dispositivo local es necesario tener Python y PostgreSQL.

## Instalación y uso

Pasos para poder utilizar la aplicación:

1. Clonar el repositorio: "git clone ..."
2. Crear y activar un entorno virtual: "python -m venv venv && source venv/bin/activate"
3. Instalar las dependencias de requirements.txt: "pip install -r requirements.txt"
4. Configurar el archivo .env: "cp .env.example .env"
5. Ejecutar las migraciones: "python manage.py migrate"
7. Ejecutar el servidor: "python manage.py runserver"

## Arquitectura

El proyecto se divide en dos aplicaciones, config y tarea_planner. La aplicación config es la raíz, que funciona como la capa de configuración y arranque, mientras que el resto de la lógica de negocio, modelos, vistas y urls se han desarrollado dentro de tarea_planner. Esta división permite mantener el proyecto limpio y respetar la separación de responsabilidades.

Dentro de la aplicación tarea_planner se ha optado por separa las vistas y modelos en archivos fraccionados, evitando el uso de archivos demasiado grandes con poca legibilidad. Estos archivos se agrupan dentro de sus correspondientes directorios (views/, models/) y funcionan como módulos de python, incluyendo un archivo __init__.py.  

## Modelado de datos

En este punto se definen los modelos utilizados en la aplicación, justificando las decisiones tomadas.

### User

El modelo de usuario hereda de AbstractUser, el modelo estándar de Django, lo que permite utilizar funcionalidades nativas como la autenticación, los permisos o la gestión de la sesión del usuario.

Se ha optado por no utilizar el campo username y en su lugar utilizar el correo electrónico como identificador único del usuario. Esta decisión está basada en el análisis del caso de uso de los usuarios, ya que los profesores o alumnos pueden compartir un mismo nombre y esta solución permite evitar el uso de formatos especiales como "{nombre}{1ª letra apellido 1}".

Para ello, se ha implementado un UserManager personalizado, que permite la correcta creación de usuarios al utilizar el email como identificador principal.

La clave primaria de este modelo es un identificador de tipo UUID, lo que mejora la seguridad con respecto a ids secuenciales y permite exponer estos identificadores en las urls de forma segura.

La distinción entre profesores y alumnos se hace a través de un parámetro, denominado "role". No es necesario crear distintos modelos para cada uno de estos roles debido a que no tienen propiedades distintas y las diferencias de comportamiento se gestionan a nivel de lógica de aplicación. 

### Task

En la aplicación se utiliza un único modelo de tarea. Después de estudiar los requerimientos técnicos a fondo (tareas individuales o grupales, evaluables y no evaluables) no se encontró una necesidad real que justifique la creación de modelos distintos, ya que habría compartido atributos y comportamiento. El uso de varios modelos habría introducido complejidad innecesaria, duplicidad de código y dificultad de mantenimiento, lo que se evita con un único modelo.

La clave principal de este modelo es también un campo UUID, por los mismos motivos listados anteriormente. Además, las tareas tienen una relación M2M con los usuarios, atrevés de la propiedad "assigned_to". Esto permite, al mismo tiempo, crear una tarea individual (relacionada con un único usuario) y grupal (relacionada con varios usuarios).

También tienen otra relación con la tabla de usuarios, ya que se guarda una referencia al usuario creador con la propiedad "created_by". Este campo, definido como FK, tiene el atributo de "on_delete=CASCADE", de modo que si se borra el usuario creador de la base de datos, se eliminan también sus tareas.

Un aspecto interesante de este modelo es la definición de propiedades adicionale mediante el uso de la etiqueta @property. Estas propiedades son inferidas a partir de otras, por ejemplo, una tarea es grupal si tiene más de un usuario asignado (la validación de esta propiedad se hace mediante la lógica de la aplicación en el momento de creación/edición). Estas propiedades son útiles en las vistas y formularios, pero no resulta necesario guardarlas en la base de datos.

## Vistas

Se han desarrollado las siguientes vistas:

| Archivo html | Archivo Python | Finalidad | Imagen |
| - | - | - | - |
| base.html | - | Base sobre la que se incrustan el resto de vistas. Permite reutilizar un mismo layout. | - |
| header.html | - | Componente utilizado a modo de cabecera en todas las vistas. Unifica la navegación en la aplicación. | ![cabecera](docs/cabecera.png) |
| messages.html | - | Componente utilizado para mostrar los mensajes enviados desde el servidor al cliente. Los muestra como un toast en la esquina inferior derecha que pueden ser eliminados por el usuario. | ![mensajes](docs/mensajes.png) |
| home.html | home.py | Landing page para los usuarios no autenticados. Serviría para mostrar información sobre la aplicación. Actualmente permite acceder al formulario de inicio de sesión y al de registro de usuairo. | ![home](docs/home.png) |
| login.html | - | Formulario de inicio de sesión. Utiliza la lógica propia de django. | ![login](docs/login.png) |
| register.html | register.py | Formulario de registro de usuarios. Permite crear usuarios con rol de profesor y alumno. | ![register](docs/register.png)|
| completar_tarea.html | tareas.py | Vista detalle de una tarea que permite a los usuarios de tipo alumno responder a la tarea, guardar el trabajo hecho y, en el momento que quieran, entregarla. | ![completar tarea](docs/completar_tarea.png) |
| crear_tarea.html | tareas.py | Formulario de creación de tarea. Dependiendo de si el usuario es de tipo profesor o alumno podrá hacer tareas evaluables o no. | ![crear tarea](docs/crear_tarea.png) |
| detalle_tarea.html |  tareas.py | Vista detalle de una tarea. Permite visualizar los datos de una tarea así como la respuesta dada por el alumno. | ![detalle tarea](docs/detalle_tarea.png)|
| editar_tarea.html | tareas.py | Formulario de edición de una tarea. Permite (a un profesor o al usuario creador de la tarea) editar los datos de la misma. | ![editar tarea](docs/editar_tarea.png)|
| evaluar_tarea.html | tareas.py | Formulario de evaluación de la tarea. Muestra el título, descripción y respuesta de una tarea y permite evaluar la misma. | ![evaluar tarea](docs/evaluar_tarea.png)|
| tareas.html | tareas.py| Vista con el listado de todas las tareas. Incluye botones para navegar a la edición, visualización y evaluación de las tareas. | ![tareas](docs/tareas.png) |
| listado_usuarios.html | usuarios.py | Vista que contiene el listado de todos los usuarios de la aplicación. | ![listado usuarios](docs/listado_usuarios.png)|
| perfil_usuario.html | usuarios.py | Vista detalle de un usuario. Muestra sus datos principales, incluyendo el tipo de usuario. | ![perfil usuario](docs/perfil_usuario.png) |

## Esquema ER

El siguiente esquema ER ha sido extraído de DBeaver y muestra la relación entre las distintas entidades de la base de datos de la aplicación.

![Esquema ER](<docs/MyOng - public - tarea_planner_task.png>)

## Base de datos

La base de datos utilizada en este proyecto es PostgreSQL. A continuación se detallan las caracteristicas de la misma.

### Psycopg2-binary

La conexión con la base de datos se hace mediante el paquete psycopg2-binary. La utilización del paquete *-binary permite evitar la compilación o uso de librerías adicionales, ya que está listo para ser usado. Esta versión de la librería se recomienda para el desarrollo y el testing, pero su uso se desaconseja en un entorno de producción, en el que se debería usar el paquete original.

Puedes leer más sobre las características y diferencias aquí https://pypi.org/project/psycopg2-binary/

### Configuración PostgreSQL

La configuración se detalla en el archivo settings.py, en el que se define la base de datos utilizada ("django.db.backends.postgresql") y los distintos parámetros para la conexión, como el nombre, usuario, contraseña o puerto. 

Los valores de estas propiedades se guardan en un archivo .env para evitar la exposición de datos sensibles, utilizando el paquete dotenv y la función load_dotenv. También sería válida la utilización de variables del sistema o del entorno.

## Migraciones

En un principio se crearon modelos básicos sobre los que se ejecutó una migración inicial. Durante el desarrollo del proyecto, conforme se han modificado estos modelos o sus relaciones, se han realizado posteriores migraciones para reflejar los cambios. 

En el proyecto se incluyen las migraciones necesarias para ejecutar el proyecto sin erroes.

## Gitignore

El archivo .gitignore utilizado en este proyecto ha sido extraído de gitignore.io, configurado específicamente para un proyecto django.

## Posibles mejoras

- Añadir validaciones de tipos de usuario y permisos al acceder a algunas vistas. 
Actualmente la única comprobación que se hace al intentar acceder a una vista es si el usuario está logueado, por lo que resulta posible para un usuario de tipo alumno acceder a la edición o evaluación de una tarea a través de la url con el identificador de la tarea. Idealmente se crearía un sistema de validación que sea fácilmente reutilizable entre vistas para poder especificar el tipo de usuario que puede acceder a ella.
- Configurar un trabajo periódico (cron). Dado que las tareas tienen una fecha de entrega, podría resultar útil configurar un trabajo autómatico que se ejecute en el servidor de forma periódica (una vez al día, una vez por hora) y marque aquellas tareas para las que haya llegado la fecha de entrega y no tengan respuesta como no entregadas. Para eso sería necesario añadir el estado de las tarea al modelo.
- Completar la landing page. Mejorar el estilo que tiene y añadir más información, como una descripción de la aplicación y un listado de ventajas de usarla.

## Créditos

El icono que se utiliza como logo/favicon en la aplicación está basado en 
<a href="https://www.flaticon.es/icono-gratis/agenda_16096501?term=agenda&page=1&position=56&origin=style&related_id=16096501" title="icono agenda">este icono creado por susannanovaIDR - Flaticon</a>.