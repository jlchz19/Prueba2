print('[DEBUG] Inicio absoluto de app_simple.py')
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import os
from config import Config
# Importaciones opcionales para PDF
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[WARNING] ReportLab no está instalado. Las funciones de PDF no estarán disponibles.")

from io import BytesIO
import threading
import time

# Importaciones para el scheduler
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    import atexit
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("[WARNING] APScheduler no está instalado. Las alertas automáticas no funcionarán.")

# Importaciones opcionales para email
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import smtplib
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("[WARNING] Módulos de email no disponibles.")

def enviar_notificacion_email(usuario, alerta):
    """Envía notificación por email cuando se crea una alerta"""
    if not EMAIL_AVAILABLE:
        print("[WARNING] No se puede enviar email - módulos no disponibles")
        return False
    
    try:
        # Configuración del servidor SMTP (Gmail como ejemplo)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Estas credenciales deberían estar en variables de entorno
        import os
        email_usuario = os.getenv('EMAIL_USER', 'jlchz19@gmail.com')
        email_password = os.getenv('EMAIL_PASSWORD', 'otldbykdcyoxmazb')
        
        # Crear mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = email_usuario
        mensaje['To'] = usuario.email
        mensaje['Subject'] = f"Nueva Alerta AgroGest: {alerta.titulo}"
        
        # Obtener información del animal si existe
        animal_info = ""
        if alerta.animal_id:
            animal = Animal.query.get(alerta.animal_id)
            if animal:
                animal_info = f"\nAnimal: {animal.identificacion} - {animal.nombre or 'Sin nombre'}"
        
        # Crear mensaje HTML profesional
        tipo_emojis = {
            'animal': '🐄',
            'vacuna': '💉',
            'produccion': '🥛',
            'empleado': '👨‍🌾',
            'general': '📋'
        }
        
        emoji_tipo = tipo_emojis.get(alerta.tipo_alerta, '📋')
        
        cuerpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 300;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .alert-card {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #007bff;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .alert-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #007bff;
                    margin-bottom: 10px;
                }}
                .info-row {{
                    display: flex;
                    margin: 10px 0;
                    align-items: center;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #495057;
                    min-width: 120px;
                }}
                .info-value {{
                    color: #212529;
                }}
                .badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    background-color: #007bff;
                    color: white;
                    border-radius: 15px;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-top: 1px solid #dee2e6;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #007bff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Alerta AgroGest</h1>
                    <p>Sistema de Gestión Ganadera</p>
                </div>
                
                <div class="content">
                    <p>Hola <strong>{usuario.nombre} {usuario.apellido}</strong>,</p>
                    
                    <p>Se ha programado una nueva alerta en tu sistema AgroGest:</p>
                    
                    <div class="alert-card">
                        <div class="alert-title">
                            {emoji_tipo} {alerta.titulo}
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">📝 Descripción:</span>
                            <span class="info-value">{alerta.descripcion}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">📅 Fecha:</span>
                            <span class="info-value">{alerta.fecha_programada.strftime('%d/%m/%Y %H:%M')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">🏷️ Tipo:</span>
                            <span class="badge">{alerta.tipo_alerta.title()}</span>
                        </div>
                        
                        {f'<div class="info-row"><span class="info-label">🐄 Animal:</span><span class="info-value">{animal_info.replace("Animal: ", "")}</span></div>' if animal_info else ''}
                    </div>
                    
                    <p>Esta alerta se enviará automáticamente en la fecha y hora programada.</p>
                    
                    <p>¡Mantén tu ganado siempre bajo control con AgroGest!</p>
                </div>
                
                <div class="footer">
                    <div class="logo">🐄 AgroGest</div>
                    <p style="margin: 5px 0; color: #6c757d; font-size: 14px;">
                        Sistema Profesional de Gestión Ganadera
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        mensaje.attach(MIMEText(cuerpo_html, 'html'))
        
        # Enviar email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_usuario, email_password)
        texto = mensaje.as_string()
        server.sendmail(email_usuario, usuario.email, texto)
        server.quit()
        
        print(f"[INFO] Email enviado a {usuario.email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] No se pudo enviar email: {e}")
        # Log más detallado del error
        import traceback
        print(f"[DEBUG] Traceback completo: {traceback.format_exc()}")
        return False

from sqlalchemy import func
from sqlalchemy.orm import aliased, load_only, defer
from sqlalchemy.sql.expression import extract
from werkzeug.utils import secure_filename
import pandas as pd
import config # Importar el archivo de configuración
from flask import make_response
import io
from functools import wraps
from types import SimpleNamespace
import base64
from dotenv import load_dotenv

# Importación opcional de WeasyPrint
WEASYPRINT_AVAILABLE = False
HTML = None
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

# Integración opcional con Google Gemini (configuración perezosa)
GEMINI_AVAILABLE = False
genai = None
def _check_gemini():
    """Configura Gemini en tiempo de petición si hay API key.
    Devuelve el módulo genai si está listo, de lo contrario None.
    """
    global GEMINI_AVAILABLE, genai
    try:
        if genai is None:
            import google.generativeai as _genai
            genai = _genai
        # Recargar variables desde .env por si se actualizó sin reiniciar
        try:
            load_dotenv(override=False)
        except Exception:
            pass
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            # Configurar en cada llamada es seguro; genai hace override sin problema
            genai.configure(api_key=api_key)
            GEMINI_AVAILABLE = True
            return genai
        else:
            GEMINI_AVAILABLE = False
            return None
    except Exception:
        GEMINI_AVAILABLE = False
        genai = None
        return None

app = Flask(__name__)
# Cargar configuración desde el archivo config.py
app.config.from_object(config.DevelopmentConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finca_ganadera.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Asegurar que el directorio de uploads existe
UPLOAD_FOLDER = os.path.join('static', 'animales')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos de la base de datos
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='activo')  # activo, inactivo
    rol = db.Column(db.String(20), default='usuario')  # admin, usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Finca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.Float)  # en hectáreas
    tipo_produccion = db.Column(db.String(50))  # leche, carne, doble propósito, etc.
    propietario = db.Column(db.String(100))
    telefono = db.Column(db.String(30))
    email = db.Column(db.String(120))
    fecha_fundacion = db.Column(db.Date)
    descripcion = db.Column(db.Text)
    ubicacion = db.Column(db.String(200))  # municipio, departamento, país
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))  # Dueño de la finca
    animales = db.relationship('Animal', backref='finca', lazy=True)
    potreros = db.relationship('Potrero', backref='finca', lazy=True)
    empleados = db.relationship('Empleado', backref='finca', lazy=True)
    vacunas = db.relationship('Vacuna', backref='finca', lazy=True)
    producciones = db.relationship('Produccion', backref='finca', lazy=True)
    inventarios = db.relationship('Inventario', backref='finca', lazy=True)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identificacion = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100))  # Nuevo campo para nombre del animal
    tipo = db.Column(db.String(20), nullable=False)  # vaca, cochino, etc.
    raza = db.Column(db.String(50), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    peso_nacimiento = db.Column(db.Float)  # Peso al nacer
    estado = db.Column(db.String(20), default='activo')  # activo, vendido, muerto
    potrero_id = db.Column(db.Integer, db.ForeignKey('potrero.id'))  # Potrero asignado (para bovinos principalmente)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'))  # Ubicación específica según tipo de animal
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    imagen = db.Column(db.String(200))  # Ruta de la imagen
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    padre_id = db.Column(db.Integer, db.ForeignKey('animal.id'))
    madre_id = db.Column(db.Integer, db.ForeignKey('animal.id'))
    sexo = db.Column(db.String(10))  # Macho o Hembra
    
    # Información adicional para registro completo
    color_señas = db.Column(db.String(200))  # Color y señas particulares
    ubicacion_actual = db.Column(db.String(100))  # Ubicación específica (corral, paridera, etc.)
    
    # Información genética y reproductiva (genérica para todos los animales)
    numero_crias_camada = db.Column(db.Integer)  # Número de crías por camada/parto
    peso_promedio_crias = db.Column(db.Float)  # Peso promedio de las crías
    produccion_diaria = db.Column(db.Float)  # Producción diaria (leche, huevos, etc.)
    unidad_produccion = db.Column(db.String(20))  # Unidad de producción (litros, huevos, kg)
    
    # Historial reproductivo (para hembras de cualquier especie)
    fecha_servicio = db.Column(db.Date)  # Fecha de servicio/inseminación/monta
    semental_utilizado = db.Column(db.String(100))  # ID del semental/macho utilizado
    fecha_estimada_parto = db.Column(db.Date)  # Fecha estimada de parto/nacimiento
    fecha_real_parto = db.Column(db.Date)  # Fecha real de parto/nacimiento
    crias_nacidas_vivas = db.Column(db.Integer)  # Crías nacidas vivas (lechones, terneros, corderos, etc.)
    crias_nacidas_muertas = db.Column(db.Integer)  # Crías nacidas muertas
    peso_promedio_crias_nacimiento = db.Column(db.Float)  # Peso promedio de crías al nacer
    numero_partos = db.Column(db.Integer, default=0)  # Número total de partos
    
    # Historial reproductivo (para machos reproductores de cualquier especie)
    fecha_inicio_semental = db.Column(db.Date)  # Fecha de inicio como reproductor
    numero_servicios_exitosos = db.Column(db.Integer, default=0)  # Servicios/montas exitosos
    promedio_crias_por_camada = db.Column(db.Float)  # Promedio de crías por camada de sus parejas
    
    # Información de venta/compra
    fecha_venta = db.Column(db.Date)
    comprador = db.Column(db.String(100))
    peso_venta = db.Column(db.Float)
    precio_venta = db.Column(db.Float)
    
    # Información de fallecimiento
    fecha_fallecimiento = db.Column(db.Date)
    causa_fallecimiento = db.Column(db.String(200))
    disposicion_final = db.Column(db.String(100))  # Incineración, entierro, etc.
    
    # Observaciones generales
    observaciones = db.Column(db.Text)
    
    # Relaciones
    historial_alimentacion = db.relationship('HistorialAlimentacion', backref='animal', lazy=True, cascade='all, delete-orphan')
    historial_salud = db.relationship('HistorialSalud', backref='animal', lazy=True, cascade='all, delete-orphan')
    notas = db.relationship('NotaAnimal', backref='animal', lazy=True, cascade='all, delete-orphan')
    historial_potreros = db.relationship('HistorialPotrero', backref='animal', lazy=True, cascade='all, delete-orphan')
    potrero = db.relationship('Potrero', backref='animales', lazy=True)

# Nuevos modelos para el registro completo

class HistorialAlimentacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_alimento = db.Column(db.String(100), nullable=False)  # Pre-inicio, Inicio, Crecimiento, Engorde
    marca = db.Column(db.String(100))
    composicion = db.Column(db.Text)
    cantidad_diaria = db.Column(db.Float)
    unidad = db.Column(db.String(20))  # kg, litros, etc.
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    observaciones = db.Column(db.Text)

class HistorialSalud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=False)  # enfermedad, lesión, desparasitación, etc.
    descripcion = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    tratamiento = db.Column(db.Text)
    dias_tratamiento = db.Column(db.Integer)
    resultado = db.Column(db.String(50))  # Total, Parcial, Sin recuperación
    observaciones = db.Column(db.Text)


# --- Nuevos modelos: módulo reproductivo avanzado ---
class ServicioReproductivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo_servicio = db.Column(db.String(30), nullable=False)  # monta natural, inseminacion
    semental_id = db.Column(db.Integer, db.ForeignKey('animal.id'))  # opcional
    semental_nombre = db.Column(db.String(100))
    responsable = db.Column(db.String(100))  # empleado/veterinario
    observaciones = db.Column(db.Text)

class DiagnosticoPrenez(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    resultado = db.Column(db.String(20), nullable=False)  # preñada, vacía, dudoso
    metodo = db.Column(db.String(50))  # palpación, eco, laboratorio
    semanas_gestacion = db.Column(db.Integer)
    observaciones = db.Column(db.Text)

class Parto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    crias_vivas = db.Column(db.Integer)
    crias_muertas = db.Column(db.Integer)
    peso_promedio_crias = db.Column(db.Float)
    dificultades = db.Column(db.String(200))
    observaciones = db.Column(db.Text)

class Potrero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    area = db.Column(db.Float, nullable=False)  # en hectáreas
    capacidad = db.Column(db.Integer, nullable=False)  # número máximo de animales
    tipo_pasto = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='disponible')  # disponible, ocupado, mantenimiento
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)

class Ubicacion(db.Model):
    """Modelo para ubicaciones específicas según tipo de animal"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_ubicacion = db.Column(db.String(50), nullable=False)  # corral, gallinero, cochiquera, establo, etc.
    tipo_animal = db.Column(db.String(50), nullable=False)  # Bovino, Porcino, Aviar, Equino, etc.
    capacidad = db.Column(db.Integer, nullable=False)  # número de animales
    area = db.Column(db.Float)  # en metros cuadrados
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='disponible')  # disponible, ocupado, mantenimiento
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    
    # Relación con animales
    animales_ubicacion = db.relationship('Animal', backref='ubicacion_asignada', lazy=True, foreign_keys='Animal.ubicacion_id')

class Vacuna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_vacuna = db.Column(db.String(100), nullable=False)
    fecha_aplicacion = db.Column(db.Date, nullable=False)
    fecha_proxima = db.Column(db.Date, nullable=False)
    observaciones = db.Column(db.Text)
    aplicada_por = db.Column(db.String(100), nullable=False)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    numero_lote = db.Column(db.String(50))
    fecha_vencimiento = db.Column(db.Date)
    # Agregar relación para acceder a animal desde vacuna
    animal = db.relationship('Animal', backref='vacunas', lazy=True)
    # Nuevo: relación con empleado (veterinario)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleado.id'))
    veterinario = db.relationship('Empleado', backref='vacunas_aplicadas', lazy=True)
    # Nuevos campos para datos del veterinario
    veterinario_nombre = db.Column(db.String(100))
    veterinario_apellido = db.Column(db.String(100))
    veterinario_cargo = db.Column(db.String(100))
    veterinario_telefono = db.Column(db.String(30))

class Empleado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    fecha_contratacion = db.Column(db.Date, nullable=False)
    salario = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='activo')  # activo, inactivo
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)

class Produccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_produccion = db.Column(db.String(50), nullable=False)  # leche, carne, etc.
    cantidad = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)  # litros, kg, etc.
    fecha = db.Column(db.Date, nullable=False)
    calidad = db.Column(db.String(20), default='buena')  # buena, regular, mala
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    # Agregar relación para acceder a animal desde produccion
    animal = db.relationship('Animal', backref='producciones', lazy=True)



class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.Date)
    categoria = db.Column(db.String(50), nullable=False)  # alimento, medicina, equipos, etc.
    tipo_animal = db.Column(db.String(20))  # vaca, cochino, etc.
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)

# Historial de movimientos de inventario
class MovimientoInventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventario_id = db.Column(db.Integer, db.ForeignKey('inventario.id'), nullable=False)
    tipo_movimiento = db.Column(db.String(20), nullable=False)  # entrada, salida, ajuste
    cantidad = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.String(200))

class MovimientoInventarioAnimal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventario_id = db.Column(db.Integer, db.ForeignKey('inventario.id'), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.String(200))
    observaciones = db.Column(db.Text)
    inventario = db.relationship('Inventario', lazy=True)
    animal = db.relationship('Animal', lazy=True)

# --- Costos y Rentabilidad ---
class CentroCosto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)

class Gasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    centro_costo_id = db.Column(db.Integer, db.ForeignKey('centro_costo.id'))
    categoria = db.Column(db.String(50), nullable=False)  # alimento, medicina, mano_obra, mantenimiento, otros
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text)
    potrero_id = db.Column(db.Integer, db.ForeignKey('potrero.id'))
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'))
    centro_costo = db.relationship('CentroCosto', lazy=True)

class Ingreso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    concepto = db.Column(db.String(100), nullable=False)  # venta leche, venta animal, otros
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text)

# Notas o comentarios en animales
class NotaAnimal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    nota = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class HistorialPotrero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    potrero_id = db.Column(db.Integer, db.ForeignKey('potrero.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.String(200))  # Motivo o comentario del cambio
    
    # Eliminar la siguiente línea para evitar conflicto de backref:
    # animal = db.relationship('Animal', backref='historial_potreros', lazy=True)
    potrero = db.relationship('Potrero', lazy=True)

# Usar el decorador de Flask-Login en lugar del personalizado
# El decorador personalizado se mantiene para compatibilidad pero no se usa
def login_required_custom(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_finca_alertas(finca_id):
    """Recopila alertas importantes para una finca específica."""
    alertas = []
    today = date.today()
    limite_proximidad = today + timedelta(days=15)

    # Alerta 1: Vacunas próximas a vencer
    vacunas_proximas = Vacuna.query.join(Animal).filter(
        Vacuna.finca_id == finca_id,
        Vacuna.fecha_proxima >= today,
        Vacuna.fecha_proxima <= limite_proximidad
    ).order_by(Vacuna.fecha_proxima).all()

    for vacuna in vacunas_proximas:
        animal = Animal.query.get(vacuna.animal_id)
        dias_faltantes = (vacuna.fecha_proxima - today).days
        alertas.append({
            'tipo': 'vacuna',
            'mensaje': f"Vacuna '{vacuna.tipo_vacuna}' para el animal '{animal.identificacion}' vence en {dias_faltantes} días.",
            'url': url_for('vacunas')
        })

    # Alerta 2: Inventario por caducar
    inventario_por_caducar = Inventario.query.filter(
        Inventario.finca_id == finca_id,
        Inventario.fecha_vencimiento.isnot(None),
        Inventario.fecha_vencimiento >= today,
        Inventario.fecha_vencimiento <= limite_proximidad
    ).order_by(Inventario.fecha_vencimiento).all()
    
    for item in inventario_por_caducar:
        dias_faltantes = (item.fecha_vencimiento - today).days
        alertas.append({
            'tipo': 'inventario_caduca',
            'mensaje': f"El producto '{item.producto}' caduca en {dias_faltantes} días.",
            'url': url_for('inventario')
        })

    # Alerta 3: Bajo inventario (ej. cantidad < 10)
    bajo_inventario = Inventario.query.filter(
        Inventario.finca_id == finca_id,
        Inventario.cantidad < 10
    ).all()

    for item in bajo_inventario:
         alertas.append({
            'tipo': 'inventario_bajo',
            'mensaje': f"Bajo stock de '{item.producto}': quedan {item.cantidad} {item.unidad}.",
            'url': url_for('inventario')
        })

    return alertas

# Rutas principales
@app.route('/')
def home():
    return render_template('presentacion.html')

@app.route('/descargas')
def descargas():
    """Ruta deshabilitada. La app móvil ya no es parte del proyecto."""
    return ("Recurso no disponible", 404)

@app.route('/dashboard')
@login_required
def index():
    user_id = session['user_id']
    if 'finca_id' not in session:
        # Dashboard global si no hay finca seleccionada
        total_fincas = Finca.query.filter_by(usuario_id=user_id).count()
        total_animales = db.session.query(db.func.count(Animal.id)).join(Finca).filter(Finca.usuario_id == user_id).scalar()
        total_empleados = db.session.query(db.func.count(Empleado.id)).join(Finca).filter(Finca.usuario_id == user_id).scalar()
        total_potreros = db.session.query(db.func.count(Potrero.id)).join(Finca).filter(Finca.usuario_id == user_id).scalar()
        
        # Gráfico de animales por finca
        animales_por_finca = db.session.query(Finca.nombre, db.func.count(Animal.id)).join(Animal, Animal.finca_id == Finca.id).filter(Finca.usuario_id == user_id).group_by(Finca.nombre).order_by(Finca.nombre).all()
        finca_labels = [row[0] for row in animales_por_finca]
        finca_data = [row[1] for row in animales_por_finca]
        
        # Actividad Reciente Global (ultimos 5 animales en todas las fincas)
        animales_recientes = Animal.query.join(Finca).filter(Finca.usuario_id == user_id).order_by(Animal.id.desc()).limit(5).all()

        return render_template('index.html', 
                               no_finca=True,
                               total_fincas=total_fincas,
                               total_animales=total_animales,
                               total_empleados=total_empleados,
                               total_potreros=total_potreros,
                               finca_labels=finca_labels,
                               finca_data=finca_data,
                               animales_recientes=animales_recientes,
                               today=date.today(),
                               date=date
                               )

    finca_id = session.get('finca_id')
    finca = Finca.query.get_or_404(finca_id)

    # Recopilar alertas para la finca
    alertas = get_finca_alertas(finca_id)

    # Estadísticas para la finca seleccionada
    total_animales = Animal.query.filter_by(finca_id=finca_id).count()
    total_potreros = Potrero.query.filter_by(finca_id=finca_id).count()
    total_empleados = Empleado.query.filter_by(finca_id=finca_id).count()
    total_vacunas = Vacuna.query.filter_by(finca_id=finca_id).count()
    
    # --- Datos de Rendimiento y Finanzas ---

    # 1. Valor total del inventario
    valor_total_inventario = db.session.query(
        db.func.sum(Inventario.cantidad * Inventario.precio_unitario)
    ).filter(Inventario.finca_id == finca_id).scalar() or 0.0

    # 2. KPIs
    # KPI: Producción media por vaca
    hoy = date.today()
    
    # KPI: Producción media por vaca
    total_leche_mes_actual = db.session.query(
        db.func.sum(Produccion.cantidad)
    ).filter(
        Produccion.finca_id == finca_id,
        Produccion.tipo_produccion == 'leche',
        db.func.extract('month', Produccion.fecha) == hoy.month,
        db.func.extract('year', Produccion.fecha) == hoy.year
    ).scalar() or 0

    numero_vacas = Animal.query.filter_by(finca_id=finca_id, tipo='vaca', estado='activo').count()
    produccion_media_vaca = total_leche_mes_actual / numero_vacas if numero_vacas > 0 else 0

    # 3. Producción reciente
    AnimalAlias = aliased(Animal)
    produccion_reciente = db.session.query(
        Produccion, AnimalAlias.identificacion
    ).join(
        AnimalAlias, Produccion.animal_id == AnimalAlias.id
    ).filter(
        Produccion.finca_id == finca_id
    ).order_by(Produccion.fecha.desc()).limit(5).all()

    # 4. Costos/Ingresos del mes (básico)
    primer_dia_mes = hoy.replace(day=1)
    gastos_mes = db.session.query(db.func.sum(Gasto.monto)).filter(
        Gasto.finca_id == finca_id,
        Gasto.fecha >= primer_dia_mes,
        Gasto.fecha <= hoy
    ).scalar() or 0.0
    ingresos_mes = db.session.query(db.func.sum(Ingreso.monto)).filter(
        Ingreso.finca_id == finca_id,
        Ingreso.fecha >= primer_dia_mes,
        Ingreso.fecha <= hoy
    ).scalar() or 0.0
    margen_mes = ingresos_mes - gastos_mes

    # --- Fin de Datos de Rendimiento ---

    # --- Datos para la columna lateral ---

    # Carga de potreros
    potreros = Potrero.query.filter_by(finca_id=finca_id).order_by(Potrero.nombre).all()
    potreros_carga = []
    for p in potreros:
        ocupantes = Animal.query.filter_by(potrero_id=p.id).count()
        carga_percent = (ocupantes / p.capacidad * 100) if p.capacidad > 0 else 0
        
        if carga_percent > 90:
            color = 'danger'
        elif carga_percent > 70:
            color = 'warning'
        else:
            color = 'success'

        potreros_carga.append({
            'nombre': p.nombre,
            'ocupantes': ocupantes,
            'capacidad': p.capacidad,
            'carga_percent': round(carga_percent, 1),
            'color': color
        })

    # Bajo inventario para widget dedicado
    bajo_inventario_items = Inventario.query.filter(
        Inventario.finca_id == finca_id,
        Inventario.cantidad < 10 # Umbral para 'bajo stock'
    ).order_by(Inventario.cantidad).limit(5).all()

    return render_template('index.html', 
                           no_finca=False,
                           finca_actual=finca,
                           alertas=alertas,
                           total_animales=total_animales,
                           total_potreros=total_potreros,
                           total_empleados=total_empleados,
                           total_vacunas=total_vacunas,
                           # Nuevos datos de rendimiento
                           valor_total_inventario=valor_total_inventario,
                           produccion_reciente=produccion_reciente,
                           # KPIs
                           produccion_media_vaca=produccion_media_vaca,
                           gastos_mes=gastos_mes,
                           ingresos_mes=ingresos_mes,
                           margen_mes=margen_mes,
                           # Datos de la columna lateral
                           potreros_carga=potreros_carga,
                           bajo_inventario_items=bajo_inventario_items,
                           today=date.today(),
                           date=date
                           )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.estado == 'activo':
                login_user(user)  # Usar Flask-Login
                session['user_id'] = user.id  # Mantener para compatibilidad
                session['username'] = user.username
                flash(f'Bienvenido {user.nombre}', 'success')
                return redirect(url_for('index'))
            else:
                flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()  # Usar Flask-Login
    session.clear()
    return redirect(url_for('login'))

# Ruta para registro público de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        
        # Verificar que el username y email no existan
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe. Elige otro.', 'error')
            return render_template('registro.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado. Usa otro email.', 'error')
            return render_template('registro.html')
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            rol='usuario'  # Por defecto es usuario normal
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

# Ruta para gestión de usuarios (solo admin)
@app.route('/usuarios')
@login_required
def usuarios():
    # Verificar que el usuario sea admin
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('index'))
    
    # Mostrar todos los usuarios del sistema
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    # Verificar que el usuario sea admin
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('index'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        # Debug temporal - imprimir todos los campos del formulario
        print("🔍 DEBUG - Campos del formulario:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")
        
        usuario.nombre = request.form['nombre']
        usuario.apellido = request.form['apellido']
        usuario.telefono = request.form['telefono']
        usuario.email = request.form['email']
        usuario.direccion = request.form.get('direccion', '')
        usuario.estado = request.form['estado']
        
        # Manejar el campo rol de forma segura
        nuevo_rol = request.form.get('rol')
        print(f"🔍 DEBUG - Rol recibido: '{nuevo_rol}' (usuario: {usuario.username})")
        
        if nuevo_rol:
            usuario.rol = nuevo_rol
        elif usuario.username == 'admin':
            # Mantener rol admin si no se envía el campo
            usuario.rol = 'admin'
        else:
            # Valor por defecto para usuarios normales
            usuario.rol = 'usuario'
            
        print(f"🔍 DEBUG - Rol asignado: '{usuario.rol}'")
        
        # Si se proporciona una nueva contraseña, actualizarla
        nueva_password = request.form.get('nueva_password')
        if nueva_password:
            usuario.password_hash = generate_password_hash(nueva_password)
            flash('Usuario actualizado exitosamente. Nueva contraseña asignada.', 'success')
        else:
            flash('Usuario actualizado exitosamente', 'success')
        
        db.session.commit()
        return redirect(url_for('usuarios'))
    
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    # Verificar que el usuario sea admin
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('index'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # No permitir eliminar al admin principal
    if usuario.username == 'admin':
        flash('No se puede eliminar al administrador principal', 'error')
        return redirect(url_for('usuarios'))
    
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente', 'success')
    return redirect(url_for('usuarios'))

# Rutas para Animales
@app.route('/animales')
@login_required
def animales():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    potreros = Potrero.query.filter_by(finca_id=session['finca_id']).all()
    return render_template('animales.html', animales=animales, potreros=potreros, today=date.today())

@app.route('/animal/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_animal():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar', 'warning')
        return redirect(url_for('fincas'))

    potreros = Potrero.query.filter_by(finca_id=session['finca_id']).all()
    ubicaciones = Ubicacion.query.filter_by(finca_id=session['finca_id']).all()
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()

    if request.method == 'POST':
        identificacion = request.form['identificacion']
        # Validación de unicidad
        animal_existente = Animal.query.filter(
            Animal.finca_id == session['finca_id'],
            db.func.lower(Animal.identificacion) == db.func.lower(identificacion)
        ).first()
        if animal_existente:
            flash(f'El ID de animal "{identificacion}" ya existe en esta finca. Por favor, utiliza uno diferente.', 'danger')
            return render_template('nuevo_animal.html', potreros=potreros, animales=animales, form_data=request.form)
        
        filename = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file.save(os.path.join(upload_folder, filename))
        
        # Procesar ubicación seleccionada
        ubicacion_seleccionada = request.form.get('ubicacion_id')
        potrero_id = None
        ubicacion_id = None
        
        if ubicacion_seleccionada:
            if ubicacion_seleccionada.startswith('potrero_'):
                potrero_id = int(ubicacion_seleccionada.replace('potrero_', ''))
            elif ubicacion_seleccionada.startswith('ubicacion_'):
                ubicacion_id = int(ubicacion_seleccionada.replace('ubicacion_', ''))
        
        # Crear el animal con todos los campos adicionales
        animal = Animal(
            identificacion=identificacion,
            nombre=request.form.get('nombre'),
            tipo=request.form['tipo'],
            raza=request.form['raza'],
            fecha_nacimiento=datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date(),
            peso=float(request.form['peso_actual']),
            peso_nacimiento=float(request.form['peso_nacimiento']) if request.form.get('peso_nacimiento') else None,
            estado=request.form.get('estado', 'activo'),
            potrero_id=potrero_id,
            ubicacion_id=ubicacion_id,
            imagen=filename,
            finca_id=session['finca_id'],
            padre_id=parse_int(request.form.get('padre_id')),
            madre_id=parse_int(request.form.get('madre_id')),
            sexo=request.form.get('sexo'),
            color_señas=request.form.get('color_señas'),
            ubicacion_actual=request.form.get('ubicacion_actual'),
            numero_crias_camada=int(request.form['numero_crias_camada']) if request.form.get('numero_crias_camada') else None,
            peso_promedio_crias=float(request.form['peso_promedio_crias']) if request.form.get('peso_promedio_crias') else None,
            produccion_diaria=float(request.form['produccion_diaria']) if request.form.get('produccion_diaria') else None,
            unidad_produccion=request.form.get('unidad_produccion'),
            observaciones=request.form.get('observaciones')
        )
        
        db.session.add(animal)
        db.session.commit()
        
        
        # Registrar historial de potrero si se asignó
        if animal.potrero_id:
            historial_potrero = HistorialPotrero(
                animal_id=animal.id,
                potrero_id=animal.potrero_id,
                motivo='Asignación inicial'
            )
            db.session.add(historial_potrero)
        
        db.session.commit()
        flash('Animal registrado exitosamente', 'success')
        return redirect(url_for('animales'))
    
    # Siempre pasar form_data, aunque sea vacío
    return render_template('nuevo_animal.html', potreros=potreros, ubicaciones=ubicaciones, animales=animales, form_data={})

@app.route('/animal/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_animal(id):
    animal = Animal.query.get_or_404(id)
    # Asegurarse de que el animal pertenece a la finca activa en la sesión
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))

    potreros = Potrero.query.filter_by(finca_id=session['finca_id']).all()
    ubicaciones = Ubicacion.query.filter_by(finca_id=session['finca_id']).all()

    if request.method == 'POST':
        # Validación de unicidad para la identificación (excluyendo el propio animal)
        nueva_identificacion = request.form['identificacion']
        animal_existente = Animal.query.filter(
            Animal.finca_id == session['finca_id'],
            db.func.lower(Animal.identificacion) == db.func.lower(nueva_identificacion),
            Animal.id != id
        ).first()

        if animal_existente:
            flash(f'El ID de animal "{nueva_identificacion}" ya está en uso. Por favor, utiliza uno diferente.', 'danger')
            return render_template('editar_animal.html', animal=animal, potreros=potreros, form_data=request.form)

        animal.identificacion = nueva_identificacion
        animal.tipo = request.form['tipo']
        animal.raza = request.form['raza']
        animal.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date()
        animal.peso = float(request.form['peso'])
        animal.estado = request.form['estado']
        
        # Procesar ubicación seleccionada (igual que en nuevo_animal)
        ubicacion_seleccionada = request.form.get('ubicacion_id')
        potrero_anterior = animal.potrero_id
        ubicacion_anterior = animal.ubicacion_id
        
        animal.potrero_id = None
        animal.ubicacion_id = None
        
        if ubicacion_seleccionada:
            if ubicacion_seleccionada.startswith('potrero_'):
                animal.potrero_id = int(ubicacion_seleccionada.replace('potrero_', ''))
            elif ubicacion_seleccionada.startswith('ubicacion_'):
                animal.ubicacion_id = int(ubicacion_seleccionada.replace('ubicacion_', ''))
        
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Asegurarse que el directorio de subida existe
                upload_folder = app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                file.save(os.path.join(upload_folder, filename))
                animal.imagen = filename  # Guardar solo el nombre del archivo

        db.session.commit()
        # Registrar historial de potrero si cambió
        if animal.potrero_id and animal.potrero_id != potrero_anterior:
            historial_potrero = HistorialPotrero(
                animal_id=animal.id,
                potrero_id=animal.potrero_id,
                motivo='Cambio de potrero desde edición'
            )
            db.session.add(historial_potrero)
            db.session.commit()
        flash('Animal actualizado exitosamente', 'success')
        return redirect(url_for('animales'))
    
    return render_template('editar_animal.html', animal=animal, potreros=potreros, ubicaciones=ubicaciones)

# Rutas para Potreros (solo para bovinos)
@app.route('/potreros')
@login_required
def potreros():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    potreros = Potrero.query.filter_by(finca_id=session['finca_id']).all()
    animales_bovinos = Animal.query.filter_by(finca_id=session['finca_id']).filter(
        Animal.tipo.in_(['Bovino', 'bovino', 'vaca', 'toro'])
    ).all()
    
    # Calcular ocupación de cada potrero
    animales_por_potrero = {}
    for potrero in potreros:
        # Contar animales asignados a este potrero
        animales_en_potrero = Animal.query.filter_by(
            finca_id=session['finca_id'], 
            potrero_id=potrero.id
        ).all()
        animales_por_potrero[potrero.id] = len(animales_en_potrero)
    
    return render_template('potreros.html', 
                         potreros=potreros, 
                         animales=animales_bovinos, 
                         animales_por_potrero=animales_por_potrero)

# Rutas para Cochiqueras (solo para cerdos)
@app.route('/cochiqueras')
@login_required
def cochiqueras():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    cochiqueras = Ubicacion.query.filter_by(
        finca_id=session['finca_id'], 
        tipo_ubicacion='cochiquera'
    ).all()
    animales_porcinos = Animal.query.filter_by(finca_id=session['finca_id']).filter(
        Animal.tipo.in_(['Porcino', 'porcino', 'cerdo', 'cochino'])
    ).all()
    
    # Calcular ocupación de cada cochiquera
    animales_por_cochiquera = {}
    for cochiquera in cochiqueras:
        # Contar animales asignados a esta cochiquera
        animales_en_cochiquera = Animal.query.filter_by(
            finca_id=session['finca_id'], 
            ubicacion_id=cochiquera.id
        ).all()
        animales_por_cochiquera[cochiquera.id] = len(animales_en_cochiquera)
    
    return render_template('cochiqueras.html', 
                         cochiqueras=cochiqueras, 
                         animales=animales_porcinos, 
                         animales_por_cochiquera=animales_por_cochiquera)

# Rutas para Gallineros (solo para aves)
@app.route('/gallineros')
@login_required
def gallineros():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    gallineros = Ubicacion.query.filter_by(
        finca_id=session['finca_id'], 
        tipo_ubicacion='gallinero'
    ).all()
    animales_aviar = Animal.query.filter_by(finca_id=session['finca_id']).filter(
        Animal.tipo.in_(['Aviar', 'aviar', 'gallina', 'pollo', 'gallo'])
    ).all()
    
    # Calcular ocupación de cada gallinero
    animales_por_gallinero = {}
    for gallinero in gallineros:
        animales_por_gallinero[gallinero.id] = sum(1 for a in animales_aviar if a.ubicacion_id == gallinero.id)
    
    return render_template('gallineros.html', 
                         gallineros=gallineros, 
                         animales=animales_aviar, 
                         animales_por_gallinero=animales_por_gallinero)

# Rutas para Establos/Corrales (para caballos y otros equinos)
@app.route('/establos')
@login_required
def establos():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    establos = Ubicacion.query.filter_by(
        finca_id=session['finca_id']
    ).filter(
        Ubicacion.tipo_ubicacion.in_(['establo', 'corral'])
    ).all()
    animales_equinos = Animal.query.filter_by(finca_id=session['finca_id']).filter(
        Animal.tipo.in_(['Equino', 'equino', 'caballo', 'yegua'])
    ).all()
    
    # Calcular ocupación de cada establo
    animales_por_establo = {}
    for establo in establos:
        animales_por_establo[establo.id] = sum(1 for a in animales_equinos if a.ubicacion_id == establo.id)
    
    return render_template('establos.html', 
                         establos=establos, 
                         animales=animales_equinos, 
                         animales_por_establo=animales_por_establo)

@app.route('/potrero/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_potrero():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    if request.method == 'POST':
        funcion = request.form['funcion']
        if request.form.get('otra_funcion'):
            funcion = request.form['otra_funcion']
        potrero = Potrero(
            nombre=request.form['nombre'],
            area=float(request.form['area']),
            capacidad=int(request.form['capacidad']),
            funcion=funcion,
            finca_id=session['finca_id']
        )
        db.session.add(potrero)
        db.session.commit()
        flash('Potrero registrado exitosamente')
        return redirect(url_for('potreros'))
    return render_template('nuevo_potrero.html')

@app.route('/potrero/editar/<int:potrero_id>', methods=['GET', 'POST'])
@login_required
def editar_potrero(potrero_id):
    potrero = Potrero.query.get_or_404(potrero_id)
    if potrero.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('potreros'))
    if request.method == 'POST':
        potrero.nombre = request.form['nombre']
        potrero.area = float(request.form['area'])
        potrero.capacidad = int(request.form['capacidad'])
        potrero.estado = request.form['estado']
        potrero.funcion = request.form['funcion']
        db.session.commit()
        flash('Potrero actualizado exitosamente', 'success')
        return redirect(url_for('potreros'))
    return render_template('editar_potrero.html', potrero=potrero)

@app.route('/potrero/<int:potrero_id>/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_potrero(potrero_id):
    potrero = Potrero.query.get_or_404(potrero_id)
    if potrero.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('potreros'))
    
    if request.method == 'POST':
        # Verificar si hay animales asignados
        animales_asignados = Animal.query.filter_by(potrero_id=potrero_id).count()
        if animales_asignados > 0:
            flash(f'No se puede eliminar el potrero porque tiene {animales_asignados} animales asignados', 'danger')
            return redirect(url_for('potreros'))
        
        db.session.delete(potrero)
        db.session.commit()
        flash('Potrero eliminado exitosamente', 'success')
        return redirect(url_for('potreros'))
    
    return render_template('eliminar_potrero.html', potrero=potrero)

# Rutas para Ubicaciones
@app.route('/ubicacion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_ubicacion():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar', 'warning')
        return redirect(url_for('fincas'))
    
    if request.method == 'POST':
        ubicacion = Ubicacion(
            nombre=request.form['nombre'],
            tipo_ubicacion=request.form['tipo_ubicacion'],
            tipo_animal=request.form['tipo_animal'],
            capacidad=int(request.form['capacidad']),
            area=float(request.form['area']) if request.form.get('area') else None,
            descripcion=request.form.get('descripcion'),
            finca_id=session['finca_id']
        )
        
        db.session.add(ubicacion)
        db.session.commit()
        flash('Ubicación creada exitosamente', 'success')
        return redirect(url_for('potreros'))
    
    return render_template('nueva_ubicacion.html')

@app.route('/ubicacion/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_ubicacion(id):
    ubicacion = Ubicacion.query.get_or_404(id)
    if ubicacion.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('potreros'))
    
    if request.method == 'POST':
        ubicacion.nombre = request.form['nombre']
        ubicacion.tipo_ubicacion = request.form['tipo_ubicacion']
        ubicacion.tipo_animal = request.form['tipo_animal']
        ubicacion.capacidad = int(request.form['capacidad'])
        ubicacion.area = float(request.form['area']) if request.form.get('area') else None
        ubicacion.descripcion = request.form.get('descripcion')
        ubicacion.estado = request.form['estado']
        
        db.session.commit()
        flash('Ubicación actualizada exitosamente', 'success')
        return redirect(url_for('potreros'))
    
    return render_template('editar_ubicacion.html', ubicacion=ubicacion)

@app.route('/ubicacion/<int:id>/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_ubicacion(id):
    ubicacion = Ubicacion.query.get_or_404(id)
    if ubicacion.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('potreros'))
    
    if request.method == 'POST':
        # Verificar si hay animales asignados
        animales_asignados = Animal.query.filter_by(ubicacion_id=id).count()
        if animales_asignados > 0:
            flash(f'No se puede eliminar la ubicación porque tiene {animales_asignados} animales asignados', 'danger')
            return redirect(url_for('potreros'))
        
        db.session.delete(ubicacion)
        db.session.commit()
        flash('Ubicación eliminada exitosamente', 'success')
        return redirect(url_for('potreros'))
    
    return render_template('eliminar_ubicacion.html', ubicacion=ubicacion)

# Rutas para Vacunas
@app.route('/vacunas')
@login_required
def vacunas():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    vacunas = Vacuna.query.filter_by(finca_id=session['finca_id']).order_by(Vacuna.fecha_proxima.asc()).all()
    return render_template('vacunas.html', vacunas=vacunas, today=date.today())

@app.route('/vacuna/<int:vacuna_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_vacuna(vacuna_id):
    vacuna = Vacuna.query.get_or_404(vacuna_id)
    if vacuna.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('vacunas'))
    
    if request.method == 'POST':
        vacuna.tipo_vacuna = request.form['tipo_vacuna']
        if request.form.get('otra_vacuna'):
            vacuna.tipo_vacuna = request.form['otra_vacuna']
        vacuna.fecha_aplicacion = datetime.strptime(request.form['fecha_aplicacion'], '%Y-%m-%d').date()
        vacuna.fecha_proxima = datetime.strptime(request.form['fecha_proxima'], '%Y-%m-%d').date()
        vacuna.observaciones = request.form['observaciones']
        vacuna.aplicada_por = request.form['aplicada_por']
        vacuna.empleado_id = int(request.form['empleado_id']) if request.form.get('empleado_id') else None
        vacuna.numero_lote = request.form.get('numero_lote')
        if request.form.get('fecha_vencimiento'):
            vacuna.fecha_vencimiento = datetime.strptime(request.form['fecha_vencimiento'], '%Y-%m-%d').date()
        
        db.session.commit()
        flash('Vacuna actualizada exitosamente', 'success')
        return redirect(url_for('vacunas'))
    
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    veterinarios = Empleado.query.filter(Empleado.finca_id == session['finca_id'], Empleado.cargo.like('%veterinario%')).all()
    return render_template('editar_vacuna.html', vacuna=vacuna, animales=animales, veterinarios=veterinarios)

@app.route('/vacuna/<int:vacuna_id>/eliminar', methods=['POST'])
@login_required
def eliminar_vacuna(vacuna_id):
    vacuna = Vacuna.query.get_or_404(vacuna_id)
    if vacuna.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('vacunas'))
    db.session.delete(vacuna)
    db.session.commit()
    flash('Vacuna eliminada exitosamente', 'success')
    return redirect(url_for('vacunas'))

# En la ruta nueva_vacuna, permitir seleccionar el veterinario desde empleados
@app.route('/vacuna/nueva', methods=['GET', 'POST'])
@login_required
def nueva_vacuna():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    if request.method == 'POST':
        tipo_vacuna = request.form['tipo_vacuna']
        if request.form.get('otra_vacuna'):
            tipo_vacuna = request.form['otra_vacuna']
        vacuna = Vacuna(
            animal_id=int(request.form['animal_id']),
            tipo_vacuna=tipo_vacuna,
            fecha_aplicacion=datetime.strptime(request.form['fecha_aplicacion'], '%Y-%m-%d').date(),
            fecha_proxima=datetime.strptime(request.form['fecha_proxima'], '%Y-%m-%d').date(),
            observaciones=request.form['observaciones'],
            aplicada_por=request.form['aplicada_por'],
            finca_id=session['finca_id'],
            empleado_id=int(request.form['empleado_id']) if request.form.get('empleado_id') else None
        )
        db.session.add(vacuna)
        db.session.commit()
        flash('Vacuna registrada exitosamente')
        return redirect(url_for('vacunas'))
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    veterinarios = Empleado.query.filter(Empleado.finca_id == session['finca_id'], Empleado.cargo.like('%veterinario%')).all()
    return render_template('nueva_vacuna.html', animales=animales, veterinarios=veterinarios)

# Rutas para Empleados
@app.route('/empleados')
@login_required
def empleados():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    empleados = Empleado.query.filter_by(finca_id=session['finca_id']).all()
    return render_template('empleados.html', empleados=empleados, today=date.today())

@app.route('/empleado/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_empleado():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    if request.method == 'POST':
        cargo = request.form['cargo']
        if request.form.get('otro_cargo'):
            cargo = request.form['otro_cargo']
            
        empleado = Empleado(
            cedula=request.form['cedula'],
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            telefono=request.form['telefono'],
            direccion=request.form['direccion'],
            cargo=cargo,
            fecha_contratacion=datetime.strptime(request.form['fecha_contratacion'], '%Y-%m-%d').date(),
            salario=float(request.form['salario']),
            finca_id=session['finca_id']
        )
        db.session.add(empleado)
        db.session.commit()
        flash('Empleado registrado exitosamente')
        return redirect(url_for('empleados'))
    
    return render_template('nuevo_empleado.html')

@app.route('/empleado/editar/<int:empleado_id>', methods=['GET', 'POST'])
@login_required
def editar_empleado(empleado_id):
    empleado = Empleado.query.get_or_404(empleado_id)
    if empleado.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('empleados'))
    if request.method == 'POST':
        empleado.nombre = request.form['nombre']
        empleado.apellido = request.form['apellido']
        empleado.cedula = request.form['cedula']
        empleado.telefono = request.form['telefono']
        empleado.direccion = request.form['direccion']
        cargo = request.form['cargo']
        if request.form.get('otro_cargo'):
            cargo = request.form['otro_cargo']
        empleado.cargo = cargo
        empleado.fecha_contratacion = datetime.strptime(request.form['fecha_contratacion'], '%Y-%m-%d').date()
        empleado.salario = float(request.form['salario'])
        empleado.estado = request.form.get('estado', 'activo')
        empleado.descripcion = request.form.get('descripcion')
        db.session.commit()
        flash('Empleado actualizado exitosamente', 'success')
        return redirect(url_for('empleados'))
    return render_template('editar_empleado.html', empleado=empleado)

@app.route('/empleado/<int:empleado_id>/eliminar', methods=['POST'])
@login_required
def eliminar_empleado(empleado_id):
    empleado = Empleado.query.get_or_404(empleado_id)
    if empleado.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('empleados'))
    db.session.delete(empleado)
    db.session.commit()
    flash('Empleado eliminado exitosamente', 'success')
    return redirect(url_for('empleados'))

# Rutas para Producción
@app.route('/produccion')
@login_required
def produccion():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    producciones = Produccion.query.join(Animal).filter_by(finca_id=session['finca_id']).all()
    return render_template('produccion.html', producciones=producciones)

@app.route('/produccion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_produccion():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    if request.method == 'POST':
        tipo_produccion = request.form['tipo_produccion']
        unidad = request.form['unidad']
        
        if request.form.get('otra_produccion'):
            tipo_produccion = request.form['otra_produccion']
        if request.form.get('otra_unidad'):
            unidad = request.form['otra_unidad']
            
        produccion = Produccion(
            animal_id=int(request.form['animal_id']),
            tipo_produccion=tipo_produccion,
            cantidad=float(request.form['cantidad']),
            unidad=unidad,
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            calidad=request.form['calidad'],
            finca_id=session['finca_id']
        )
        db.session.add(produccion)
        db.session.commit()
        flash('Producción registrada exitosamente')
        return redirect(url_for('produccion'))
    
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    return render_template('nueva_produccion.html', animales=animales)

@app.route('/produccion/editar/<int:produccion_id>', methods=['GET', 'POST'])
@login_required
def editar_produccion(produccion_id):
    produccion = Produccion.query.get_or_404(produccion_id)
    if produccion.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('produccion'))
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    if request.method == 'POST':
        produccion.animal_id = int(request.form['animal_id'])
        produccion.tipo_produccion = request.form['tipo_produccion']
        produccion.cantidad = float(request.form['cantidad'])
        produccion.unidad = request.form['unidad']
        produccion.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        produccion.calidad = request.form['calidad']
        db.session.commit()
        flash('Producción actualizada exitosamente', 'success')
        return redirect(url_for('produccion'))
    return render_template('editar_produccion.html', produccion=produccion, animales=animales)

# Rutas para Inventario
@app.route('/inventario')
@login_required
def inventario():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    
    inventarios = Inventario.query.filter_by(finca_id=session['finca_id']).order_by(Inventario.fecha_vencimiento.asc()).all()
    
    total_valor_inventario = db.session.query(db.func.sum(Inventario.cantidad * Inventario.precio_unitario)).filter_by(finca_id=session['finca_id']).scalar() or 0
    
    productos_vencidos_count = 0
    productos_por_vencer_count = 0
    productos_por_vencer_list = []
    
    today = date.today()
    
    for item in inventarios:
        if item.fecha_vencimiento:
            dias_restantes = (item.fecha_vencimiento - today).days
            if dias_restantes < 0:
                productos_vencidos_count += 1
            elif dias_restantes <= 30:
                productos_por_vencer_count += 1
                productos_por_vencer_list.append(item)
    
    return render_template('inventario.html', 
                           inventarios=inventarios, 
                           total_valor_inventario=total_valor_inventario,
                           productos_vencidos_count=productos_vencidos_count,
                           productos_por_vencer_count=productos_por_vencer_count,
                           productos_por_vencer_list=productos_por_vencer_list,
                           today=today)

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_inventario():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    if request.method == 'POST':
        categoria = request.form['categoria']
        unidad = request.form['unidad']
        tipo_animal = request.form['tipo_animal']
        if request.form.get('otra_categoria'):
            categoria = request.form['otra_categoria']
        if request.form.get('otra_unidad'):
            unidad = request.form['otra_unidad']
        fecha_vencimiento = None
        if request.form.get('fecha_vencimiento'):
            fecha_vencimiento = datetime.strptime(request.form['fecha_vencimiento'], '%Y-%m-%d').date()
        inventario = Inventario(
            producto=request.form['producto'],
            cantidad=float(request.form['cantidad']),
            unidad=unidad,
            precio_unitario=float(request.form['precio_unitario']),
            fecha_vencimiento=fecha_vencimiento,
            categoria=categoria,
            tipo_animal=tipo_animal,
            finca_id=session['finca_id']
        )
        db.session.add(inventario)
        db.session.commit()
        # Registrar movimiento de entrada
        movimiento = MovimientoInventario(
            inventario_id=inventario.id,
            tipo_movimiento='entrada',
            cantidad=inventario.cantidad,
            motivo='Registro inicial'
        )
        db.session.add(movimiento)
        db.session.commit()
        # Registrar entrega a animal si se selecciona
        animal_id = request.form.get('animal_id')
        cantidad_entregada = request.form.get('cantidad_entregada')
        if animal_id and cantidad_entregada:
            movimiento_animal = MovimientoInventarioAnimal(
                inventario_id=inventario.id,
                animal_id=int(animal_id),
                cantidad=float(cantidad_entregada),
                motivo='Entrega inicial',
                observaciones=request.form.get('observaciones_entrega')
            )
            db.session.add(movimiento_animal)
            db.session.commit()
        flash('Producto agregado al inventario exitosamente')
        return redirect(url_for('inventario'))
    tipos_animales = db.session.query(Animal.tipo).filter_by(finca_id=session['finca_id']).distinct().all()
    tipos_animales = [t[0] for t in tipos_animales]
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    return render_template('nuevo_inventario.html', tipos_animales=tipos_animales, animales=animales, inventario=None, editar=False)

@app.route('/inventario/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    if inventario.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('inventario'))
    if request.method == 'POST':
        inventario.producto = request.form['producto']
        inventario.cantidad = float(request.form['cantidad'])
        inventario.unidad = request.form['unidad']
        inventario.precio_unitario = float(request.form['precio_unitario'])
        inventario.categoria = request.form['categoria']
        inventario.tipo_animal = request.form.get('tipo_animal')
        fecha_vencimiento = request.form.get('fecha_vencimiento')
        inventario.fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date() if fecha_vencimiento else None
        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('inventario'))
    return render_template('nuevo_inventario.html', inventario=inventario, editar=True)

@app.route('/inventario/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    if inventario.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('inventario'))
    db.session.delete(inventario)
    db.session.commit()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('inventario'))

@app.route('/animal/<int:animal_id>/notas', methods=['GET', 'POST'])
@login_required
def notas_animal(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    animal = Animal.query.get_or_404(animal_id)
    if request.method == 'POST':
        nota = NotaAnimal(
            animal_id=animal_id,
            nota=request.form['nota']
        )
        db.session.add(nota)
        db.session.commit()
        flash('Nota agregada exitosamente')
        return redirect(url_for('notas_animal', animal_id=animal_id))
    # Corregido: NotaAnimal no tiene campo finca_id, filtramos solo por animal_id
    notas = NotaAnimal.query.filter_by(animal_id=animal_id).order_by(NotaAnimal.fecha.desc()).all()
    return render_template('notas_animal.html', animal=animal, notas=notas)

# Rutas para el historial completo de animales
@app.route('/animal/<int:animal_id>/historial')
@login_required
def historial_animal(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    
    historial_alimentacion = HistorialAlimentacion.query.filter_by(animal_id=animal_id).order_by(HistorialAlimentacion.fecha_inicio.desc()).all()
    historial_salud = HistorialSalud.query.filter_by(animal_id=animal_id).order_by(HistorialSalud.fecha_inicio.desc()).all()
    vacunas = Vacuna.query.filter_by(animal_id=animal_id).order_by(Vacuna.fecha_aplicacion.desc()).all()
    servicios = ServicioReproductivo.query.filter_by(animal_id=animal_id).order_by(ServicioReproductivo.fecha.desc()).all()
    preneces = DiagnosticoPrenez.query.filter_by(animal_id=animal_id).order_by(DiagnosticoPrenez.fecha.desc()).all()
    partos = Parto.query.filter_by(animal_id=animal_id).order_by(Parto.fecha.desc()).all()
    producciones = Produccion.query.filter_by(animal_id=animal_id).order_by(Produccion.fecha.desc()).all()
    notas = NotaAnimal.query.filter_by(animal_id=animal_id).order_by(NotaAnimal.fecha.desc()).all()
    entregas_inventario = MovimientoInventarioAnimal.query.filter_by(animal_id=animal_id).order_by(MovimientoInventarioAnimal.fecha.desc()).all()
    
    return render_template('historial_animal.html', 
                         animal=animal,
                         historial_alimentacion=historial_alimentacion,
                         historial_salud=historial_salud,
                         vacunas=vacunas,
                         producciones=producciones,
                         notas=notas,
                         entregas_inventario=entregas_inventario,
                         servicios=servicios,
                         preneces=preneces,
                         partos=partos)

@app.route('/animal/<int:animal_id>/historial/pdf')
@login_required
def imprimir_historial_pdf(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    
    if not WEASYPRINT_AVAILABLE:
        flash('WeasyPrint no está instalado en el servidor. Exportación limitada.', 'warning')
        return redirect(url_for('historial_animal', animal_id=animal_id))

    historial_alimentacion = HistorialAlimentacion.query.filter_by(animal_id=animal_id).order_by(HistorialAlimentacion.fecha_inicio.desc()).all()
    historial_salud = HistorialSalud.query.filter_by(animal_id=animal_id).order_by(HistorialSalud.fecha_inicio.desc()).all()
    vacunas = Vacuna.query.filter_by(animal_id=animal_id).order_by(Vacuna.fecha_aplicacion.desc()).all()
    producciones = Produccion.query.filter_by(animal_id=animal_id).order_by(Produccion.fecha.desc()).all()
    notas = NotaAnimal.query.filter_by(animal_id=animal_id).order_by(NotaAnimal.fecha.desc()).all()

    html = render_template('historial_animal.html', animal=animal, historial_alimentacion=historial_alimentacion, historial_salud=historial_salud, vacunas=vacunas, producciones=producciones, notas=notas, pdf=True)
    pdf_file = HTML(string=html, base_url=request.base_url).write_pdf()
    response = make_response(pdf_file)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=historial_{animal.identificacion}.pdf'
    return response

@app.route('/animal/<int:animal_id>/certificado')
@login_required
def certificado_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    if not WEASYPRINT_AVAILABLE:
        flash('WeasyPrint no está instalado en el servidor.', 'warning')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    # Generar un certificado breve con QR
    verification_url = url_for('verificar_certificado', animal_id=animal.id, _external=True)
    html = render_template('certificado_animal.html', animal=animal, verification_url=verification_url, date=date)
    pdf_file = HTML(string=html, base_url=request.base_url).write_pdf()
    response = make_response(pdf_file)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=certificado_{animal.identificacion}.pdf'
    return response

def verificar_certificado(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    return render_template('verificar_certificado.html', animal=animal, date=date)

@app.route('/animal/<int:animal_id>/alimentacion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_alimentacion(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    
    if request.method == 'POST':
        alimentacion = HistorialAlimentacion(
            animal_id=animal_id,
            tipo_alimento=request.form['tipo_alimento'],
            marca=request.form.get('marca'),
            composicion=request.form.get('composicion'),
            cantidad_diaria=float(request.form['cantidad_diaria']) if request.form.get('cantidad_diaria') else None,
            unidad=request.form.get('unidad'),
            fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date(),
            fecha_fin=datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date() if request.form.get('fecha_fin') else None,
            observaciones=request.form.get('observaciones')
        )
        db.session.add(alimentacion)
        db.session.commit()
        flash('Registro de alimentación agregado exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    return render_template('nueva_alimentacion.html', animal=animal)

@app.route('/animal/<int:animal_id>/servicio/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_servicio_reproductivo(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    if request.method == 'POST':
        servicio = ServicioReproductivo(
            animal_id=animal_id,
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            tipo_servicio=request.form['tipo_servicio'],
            semental_id=parse_int(request.form.get('semental_id')),
            semental_nombre=request.form.get('semental_nombre'),
            responsable=request.form.get('responsable'),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(servicio)
        db.session.commit()
        flash('Servicio reproductivo registrado', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    sementales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    return render_template('nuevo_servicio.html', animal=animal, sementales=sementales)

@app.route('/animal/<int:animal_id>/prenez/nueva', methods=['GET', 'POST'])
@login_required
def nuevo_diagnostico_prenez(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    if request.method == 'POST':
        diag = DiagnosticoPrenez(
            animal_id=animal_id,
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            resultado=request.form['resultado'],
            metodo=request.form.get('metodo'),
            semanas_gestacion=parse_int(request.form.get('semanas_gestacion')),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(diag)
        db.session.commit()
        flash('Diagnóstico de preñez registrado', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    return render_template('nueva_prenez.html', animal=animal)

@app.route('/animal/<int:animal_id>/parto/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_parto(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    if request.method == 'POST':
        parto = Parto(
            animal_id=animal_id,
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            crias_vivas=parse_int(request.form.get('crias_vivas')),
            crias_muertas=parse_int(request.form.get('crias_muertas')),
            peso_promedio_crias=float(request.form['peso_promedio_crias']) if request.form.get('peso_promedio_crias') else None,
            dificultades=request.form.get('dificultades'),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(parto)
        # actualizar métricas básicas de la hembra
        animal.numero_partos = (animal.numero_partos or 0) + 1
        db.session.commit()
        flash('Parto registrado', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    return render_template('nuevo_parto.html', animal=animal)

@app.route('/animal/<int:animal_id>/salud/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_evento_salud(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    
    if request.method == 'POST':
        evento_salud = HistorialSalud(
            animal_id=animal_id,
            tipo_evento=request.form['tipo_evento'],
            descripcion=request.form['descripcion'],
            fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date(),
            fecha_fin=datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date() if request.form.get('fecha_fin') else None,
            tratamiento=request.form.get('tratamiento'),
            dias_tratamiento=int(request.form['dias_tratamiento']) if request.form.get('dias_tratamiento') else None,
            resultado=request.form.get('resultado'),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(evento_salud)
        db.session.commit()
        flash('Evento de salud registrado exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    return render_template('nuevo_evento_salud.html', animal=animal)

@app.route('/animal/<int:animal_id>/reproductivo/actualizar', methods=['GET', 'POST'])
@login_required
def actualizar_reproductivo(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    
    if request.method == 'POST':
        # Actualizar información reproductiva según el sexo
        if animal.sexo == 'Hembra':
            animal.fecha_servicio = datetime.strptime(request.form['fecha_servicio'], '%Y-%m-%d').date() if request.form.get('fecha_servicio') else None
            animal.semental_utilizado = request.form.get('semental_utilizado')
            animal.fecha_estimada_parto = datetime.strptime(request.form['fecha_estimada_parto'], '%Y-%m-%d').date() if request.form.get('fecha_estimada_parto') else None
            animal.fecha_real_parto = datetime.strptime(request.form['fecha_real_parto'], '%Y-%m-%d').date() if request.form.get('fecha_real_parto') else None
            animal.lechones_nacidos_vivos = int(request.form['lechones_nacidos_vivos']) if request.form.get('lechones_nacidos_vivos') else None
            animal.lechones_nacidos_muertos = int(request.form['lechones_nacidos_muertos']) if request.form.get('lechones_nacidos_muertos') else None
            animal.peso_promedio_lechones = float(request.form['peso_promedio_lechones']) if request.form.get('peso_promedio_lechones') else None
            if request.form.get('fecha_real_parto'):
                animal.numero_partos = (animal.numero_partos or 0) + 1
        else:  # Macho
            animal.fecha_inicio_semental = datetime.strptime(request.form['fecha_inicio_semental'], '%Y-%m-%d').date() if request.form.get('fecha_inicio_semental') else None
            animal.numero_servicios_exitosos = int(request.form['numero_servicios_exitosos']) if request.form.get('numero_servicios_exitosos') else None
            animal.promedio_lechones_por_camada = float(request.form['promedio_lechones_por_camada']) if request.form.get('promedio_lechones_por_camada') else None
        
        db.session.commit()
        flash('Información reproductiva actualizada exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    return render_template('actualizar_reproductivo.html', animal=animal)

@app.route('/animal/<int:animal_id>/evento/registrar', methods=['GET', 'POST'])
@login_required
def registrar_evento(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    
    if request.method == 'POST':
        tipo_evento = request.form['tipo_evento']
        
        if tipo_evento == 'venta':
            animal.fecha_venta = datetime.strptime(request.form['fecha_venta'], '%Y-%m-%d').date()
            animal.comprador = request.form['comprador']
            animal.peso_venta = float(request.form['peso_venta'])
            animal.precio_venta = float(request.form['precio_venta'])
            animal.estado = 'vendido'
        elif tipo_evento == 'fallecimiento':
            animal.fecha_fallecimiento = datetime.strptime(request.form['fecha_fallecimiento'], '%Y-%m-%d').date()
            animal.causa_fallecimiento = request.form['causa_fallecimiento']
            animal.disposicion_final = request.form['disposicion_final']
            animal.estado = 'muerto'
        elif tipo_evento == 'cambio_estado':
            animal.estado = request.form['nuevo_estado']
        
        db.session.commit()
        flash('Evento registrado exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    return render_template('registrar_evento.html', animal=animal)

@app.route('/exportar/animales')
@login_required
def exportar_animales():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    df = pd.DataFrame([{k: getattr(a, k) for k in ['id','identificacion','tipo','raza','fecha_nacimiento','peso','estado','potrero_id','fecha_ingreso','imagen']} for a in animales])
    return df.to_excel('animales.xlsx', index=False), 200, {'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Content-Disposition': 'attachment; filename=animales.xlsx'}

@app.route('/exportar/inventario')
@login_required
def exportar_inventario():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    inventarios = Inventario.query.filter_by(finca_id=session['finca_id']).all()
    df = pd.DataFrame([{k: getattr(i, k) for k in ['id','producto','cantidad','unidad','precio_unitario','fecha_ingreso','fecha_vencimiento','categoria','tipo_animal']} for i in inventarios])
    return df.to_excel('inventario.xlsx', index=False), 200, {'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Content-Disposition': 'attachment; filename=inventario.xlsx'}

# --- CRUD Centros de Costo, Gastos e Ingresos ---
@app.route('/centros', methods=['GET', 'POST'])
@login_required
def centros_costo():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    if request.method == 'POST':
        centro = CentroCosto(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion'),
            finca_id=session['finca_id']
        )
        db.session.add(centro)
        db.session.commit()
        flash('Centro de costo creado', 'success')
        return redirect(url_for('centros_costo'))
    centros = CentroCosto.query.filter_by(finca_id=session['finca_id']).order_by(CentroCosto.nombre).all()
    return render_template('centros.html', centros=centros)

@app.route('/centros/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_centro(id):
    centro = CentroCosto.query.get_or_404(id)
    if centro.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('centros_costo'))
    db.session.delete(centro)
    db.session.commit()
    flash('Centro de costo eliminado', 'success')
    return redirect(url_for('centros_costo'))

@app.route('/gastos', methods=['GET', 'POST'])
@login_required
def gastos():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    if request.method == 'POST':
        gasto = Gasto(
            finca_id=session['finca_id'],
            centro_costo_id=parse_int(request.form.get('centro_costo_id')),
            categoria=request.form['categoria'],
            monto=float(request.form['monto']),
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            descripcion=request.form.get('descripcion'),
            potrero_id=parse_int(request.form.get('potrero_id')),
            animal_id=parse_int(request.form.get('animal_id'))
        )
        db.session.add(gasto)
        db.session.commit()
        flash('Gasto registrado', 'success')
        return redirect(url_for('gastos'))
    centros = CentroCosto.query.filter_by(finca_id=session['finca_id']).all()
    potreros = Potrero.query.filter_by(finca_id=session['finca_id']).all()
    animales = Animal.query.filter_by(finca_id=session['finca_id']).all()
    lista = Gasto.query.filter_by(finca_id=session['finca_id']).order_by(Gasto.fecha.desc()).all()
    return render_template('gastos.html', centros=centros, potreros=potreros, animales=animales, gastos=lista)

@app.route('/gastos/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    if gasto.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('gastos'))
    db.session.delete(gasto)
    db.session.commit()
    flash('Gasto eliminado', 'success')
    return redirect(url_for('gastos'))

@app.route('/ingresos', methods=['GET', 'POST'])
@login_required
def ingresos():
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    if request.method == 'POST':
        ingreso = Ingreso(
            finca_id=session['finca_id'],
            concepto=request.form['concepto'],
            monto=float(request.form['monto']),
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            descripcion=request.form.get('descripcion')
        )
        db.session.add(ingreso)
        db.session.commit()
        flash('Ingreso registrado', 'success')
        return redirect(url_for('ingresos'))
    lista = Ingreso.query.filter_by(finca_id=session['finca_id']).order_by(Ingreso.fecha.desc()).all()
    return render_template('ingresos.html', ingresos=lista)

@app.route('/reportes_old')
@login_required
def reportes_old():
    if 'finca_id' not in session:
        flash('Selecciona una finca para ver reportes')
        return redirect(url_for('fincas'))
    finca_id = session['finca_id']
    # Totales simples
    total_gastos = db.session.query(db.func.sum(Gasto.monto)).filter_by(finca_id=finca_id).scalar() or 0.0
    total_ingresos = db.session.query(db.func.sum(Ingreso.monto)).filter_by(finca_id=finca_id).scalar() or 0.0
    margen_total = total_ingresos - total_gastos
    centros = CentroCosto.query.filter_by(finca_id=finca_id).order_by(CentroCosto.nombre).all()
    gastos_recientes = Gasto.query.filter_by(finca_id=finca_id).order_by(Gasto.fecha.desc()).limit(10).all()
    ingresos_recientes = Ingreso.query.filter_by(finca_id=finca_id).order_by(Ingreso.fecha.desc()).limit(10).all()
    return render_template('reportes.html', total_gastos=total_gastos, total_ingresos=total_ingresos, margen_total=margen_total, centros=centros, gastos_recientes=gastos_recientes, ingresos_recientes=ingresos_recientes)

@app.route('/api/reportes')
@login_required
def api_reportes():
    if 'finca_id' not in session:
        return jsonify({'error': 'No hay finca seleccionada'}), 400
    
    finca_id = session['finca_id']
    year = request.args.get('year', datetime.now().year, type=int)

    # 1. Producción mensual de leche
    produccion_leche_mensual = db.session.query(
        db.func.extract('month', Produccion.fecha).label('month'),
        db.func.sum(Produccion.cantidad).label('total')
    ).join(Animal).filter(
        Animal.finca_id == finca_id,
        Produccion.tipo_produccion == 'leche',
        db.func.extract('year', Produccion.fecha) == year
    ).group_by('month').all()

    meses = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    produccion_data = {item.month: item.total for item in produccion_leche_mensual}
    
    labels_produccion = [meses[i] for i in range(1, 13)]
    valores_produccion = [produccion_data.get(i, 0) for i in range(1, 13)]

    # 2. Valor de inventario por categoría
    inventario_categoria = db.session.query(
        Inventario.categoria,
        db.func.sum(Inventario.cantidad * Inventario.precio_unitario).label('valor')
    ).filter(Inventario.finca_id == finca_id).group_by(Inventario.categoria).order_by(db.desc('valor')).all()

    # 3. Conteo de animales por tipo
    animales_por_tipo = db.session.query(
        Animal.tipo,
        db.func.count(Animal.id).label('cantidad')
    ).filter(Animal.finca_id == finca_id).group_by(Animal.tipo).order_by(db.desc('cantidad')).all()

    # 4. Balance mensual
    hoy = date.today()
    primer_dia = hoy.replace(day=1)
    gastos_mes = db.session.query(db.func.sum(Gasto.monto)).filter(Gasto.finca_id == finca_id, Gasto.fecha >= primer_dia, Gasto.fecha <= hoy).scalar() or 0.0
    ingresos_mes = db.session.query(db.func.sum(Ingreso.monto)).filter(Ingreso.finca_id == finca_id, Ingreso.fecha >= primer_dia, Ingreso.fecha <= hoy).scalar() or 0.0

    return jsonify({
        'produccion_leche_mensual': {
            'labels': labels_produccion,
            'valores': valores_produccion
        },
        'inventario_categoria': {
            'labels': [item.categoria.title() for item in inventario_categoria],
            'valores': [float(item.valor) for item in inventario_categoria]
        },
        'animales_por_tipo': {
            'labels': [item.tipo.title() for item in animales_por_tipo],
            'cantidades': [item.cantidad for item in animales_por_tipo]
        },
        'balance_mes': {
            'gastos': float(gastos_mes),
            'ingresos': float(ingresos_mes),
            'margen': float(ingresos_mes - gastos_mes)
        }
    })

# Rutas para Fincas
@app.route('/fincas', methods=['GET', 'POST'])
@login_required
def fincas():
    user_id = session['user_id']
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        extension = request.form.get('extension')
        tipo_produccion = request.form.get('tipo_produccion')
        propietario = request.form.get('propietario')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        fecha_fundacion = request.form.get('fecha_fundacion')
        descripcion = request.form.get('descripcion')
        ubicacion = request.form.get('ubicacion')
        finca = Finca(
            nombre=nombre,
            direccion=direccion,
            extension=float(extension) if extension else None,
            tipo_produccion=tipo_produccion,
            propietario=propietario,
            telefono=telefono,
            email=email,
            fecha_fundacion=datetime.strptime(fecha_fundacion, '%Y-%m-%d').date() if fecha_fundacion else None,
            descripcion=descripcion,
            ubicacion=ubicacion,
            usuario_id=user_id
        )
        db.session.add(finca)
        db.session.commit()
        flash('Finca registrada exitosamente')
        return redirect(url_for('fincas'))
    fincas = Finca.query.filter_by(usuario_id=user_id).all()
    return render_template('fincas.html', fincas=fincas)

@app.route('/finca/seleccionar/<int:finca_id>')
@login_required
def seleccionar_finca(finca_id):
    finca = Finca.query.get_or_404(finca_id)
    session['finca_id'] = finca.id
    flash(f'Seleccionaste la finca: {finca.nombre}')
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

@app.context_processor
def inject_finca_model():
    return dict(Finca=Finca)

@app.route('/presentacion')
def presentacion():
    return render_template('presentacion.html')

@app.route('/agregar_dr_garcia')
@login_required
def agregar_dr_garcia():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Selecciona una finca para continuar', 'warning')
        return redirect(url_for('empleados'))
    from datetime import date
    # Importación absoluta para evitar ImportError
    from app_simple import db, Empleado, Finca
    # Verificar si ya existe
    existente = Empleado.query.filter_by(cedula='11223344', finca_id=finca_id).first()
    if existente:
        flash('El Dr. García ya está registrado en esta finca.', 'info')
        return redirect(url_for('empleados'))
    dr = Empleado(
        cedula='11223344',
        nombre='Dr.',
        apellido='García',
        telefono='0416-5556677',
        direccion='Calle Veterinaria #10',
        cargo='Veterinario',
        fecha_contratacion=date(2021, 5, 10),
        salario=1200.0,
        finca_id=finca_id
    )
    db.session.add(dr)
    db.session.commit()
    flash('Dr. García agregado exitosamente como veterinario.', 'success')
    return redirect(url_for('empleados'))

@app.route('/animal/<int:animal_id>/eliminar', methods=['POST'])
@login_required
def eliminar_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    db.session.delete(animal)
    db.session.commit()
    flash('Animal eliminado exitosamente', 'success')
    return redirect(url_for('animales'))

# === SISTEMA REPRODUCTIVO ===
@app.route('/reproductivo')
@login_required
def calendario_reproductivo():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debe seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    # Obtener animales hembras
    hembras = Animal.query.filter_by(finca_id=finca_id, sexo='hembra').all()
    
    # Servicios recientes (últimos 30 días)
    fecha_limite = date.today() - timedelta(days=30)
    servicios_recientes = db.session.query(ServicioReproductivo, Animal)\
        .join(Animal)\
        .filter(Animal.finca_id == finca_id)\
        .filter(ServicioReproductivo.fecha >= fecha_limite)\
        .order_by(ServicioReproductivo.fecha.desc())\
        .all()
    
    # Diagnósticos pendientes (servicios sin diagnóstico después de 30 días)
    servicios_sin_diagnostico = db.session.query(ServicioReproductivo, Animal)\
        .join(Animal)\
        .outerjoin(DiagnosticoPrenez, 
                  (DiagnosticoPrenez.animal_id == ServicioReproductivo.animal_id) &
                  (DiagnosticoPrenez.fecha >= ServicioReproductivo.fecha))\
        .filter(Animal.finca_id == finca_id)\
        .filter(ServicioReproductivo.fecha <= date.today() - timedelta(days=30))\
        .filter(DiagnosticoPrenez.id == None)\
        .all()
    
    # Partos esperados (diagnósticos positivos + 280 días)
    partos_esperados = db.session.query(DiagnosticoPrenez, Animal)\
        .join(Animal)\
        .filter(Animal.finca_id == finca_id)\
        .filter(DiagnosticoPrenez.resultado == 'preñada')\
        .all()
    
    partos_proximos = []
    for diagnostico, animal in partos_esperados:
        fecha_parto = diagnostico.fecha + timedelta(days=280)
        if fecha_parto >= date.today():
            partos_proximos.append({
                'animal': animal,
                'fecha_parto': fecha_parto,
                'dias_restantes': (fecha_parto - date.today()).days
            })
    
    partos_proximos.sort(key=lambda x: x['fecha_parto'])
    
    return render_template('calendario_reproductivo.html',
                         hembras=hembras,
                         servicios_recientes=servicios_recientes,
                         servicios_sin_diagnostico=servicios_sin_diagnostico,
                         partos_proximos=partos_proximos)

@app.route('/reproductivo/servicio', methods=['GET', 'POST'])
@login_required
def nuevo_servicio():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debe seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        servicio = ServicioReproductivo(
            animal_id=request.form['animal_id'],
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            tipo_servicio=request.form['tipo_servicio'],
            semental_nombre=request.form.get('semental_nombre'),
            responsable=request.form.get('responsable'),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(servicio)
        db.session.commit()
        flash('Servicio reproductivo registrado exitosamente.', 'success')
        return redirect(url_for('calendario_reproductivo'))
    
    hembras = Animal.query.filter_by(finca_id=finca_id, sexo='hembra').all()
    machos = Animal.query.filter_by(finca_id=finca_id, sexo='macho').all()
    return render_template('nuevo_servicio.html', hembras=hembras, machos=machos)

@app.route('/reproductivo/diagnostico', methods=['GET', 'POST'])
@login_required
def nuevo_diagnostico():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debe seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        diagnostico = DiagnosticoPrenez(
            animal_id=request.form['animal_id'],
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            resultado=request.form['resultado'],
            metodo=request.form.get('metodo'),
            semanas_gestacion=request.form.get('semanas_gestacion') or None,
            observaciones=request.form.get('observaciones')
        )
        db.session.add(diagnostico)
        db.session.commit()
        flash('Diagnóstico de preñez registrado exitosamente.', 'success')
        return redirect(url_for('calendario_reproductivo'))
    
    hembras = Animal.query.filter_by(finca_id=finca_id, sexo='hembra').all()
    return render_template('nuevo_diagnostico.html', hembras=hembras)

@app.route('/reproductivo/parto', methods=['GET', 'POST'])
@login_required
def registrar_parto():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debe seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        parto = Parto(
            animal_id=request.form['animal_id'],
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            crias_vivas=request.form.get('crias_vivas') or 0,
            crias_muertas=request.form.get('crias_muertas') or 0,
            peso_promedio_crias=request.form.get('peso_promedio_crias') or None,
            dificultades=request.form.get('dificultades'),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(parto)
        db.session.commit()
        flash('Parto registrado exitosamente.', 'success')
        return redirect(url_for('calendario_reproductivo'))
    
    hembras = Animal.query.filter_by(finca_id=finca_id, sexo='hembra').all()
    return render_template('nuevo_parto.html', hembras=hembras)

# === SISTEMA DE SALUD ===
@app.route('/salud')
@login_required
def gestion_salud():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debe seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    # Obtener todos los animales
    animales = Animal.query.filter_by(finca_id=finca_id).all()
    
    # Eventos de salud recientes (últimos 30 días)
    fecha_limite = date.today() - timedelta(days=30)
    eventos_recientes = db.session.query(HistorialSalud, Animal)\
        .join(Animal)\
        .filter(Animal.finca_id == finca_id)\
        .filter(HistorialSalud.fecha_inicio >= fecha_limite)\
        .order_by(HistorialSalud.fecha_inicio.desc())\
        .all()
    
    # Tratamientos activos
    tratamientos_activos = db.session.query(HistorialSalud, Animal)\
        .join(Animal)\
        .filter(Animal.finca_id == finca_id)\
        .filter(HistorialSalud.fecha_fin == None)\
        .filter(HistorialSalud.tipo_evento.in_(['tratamiento', 'medicamento']))\
        .all()
    
    # Próximas vacunaciones (simulado - en una implementación real sería un calendario)
    proximas_vacunaciones = []
    
    # Estadísticas de salud
    total_eventos = db.session.query(HistorialSalud)\
        .join(Animal)\
        .filter(Animal.finca_id == finca_id)\
        .count()
    
    eventos_mes = db.session.query(HistorialSalud)\
        .join(Animal)\
        .filter(Animal.finca_id == finca_id)\
        .filter(HistorialSalud.fecha_inicio >= fecha_limite)\
        .count()
    
    return render_template('gestion_salud.html',
                         animales=animales,
                         eventos_recientes=eventos_recientes,
                         tratamientos_activos=tratamientos_activos,
                         proximas_vacunaciones=proximas_vacunaciones,
                         total_eventos=total_eventos,
                         eventos_mes=eventos_mes)

@app.route('/salud/evento', methods=['GET', 'POST'])
@login_required
def registrar_evento_salud():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debe seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        evento = HistorialSalud(
            animal_id=request.form['animal_id'],
            tipo_evento=request.form['tipo_evento'],
            descripcion=request.form['descripcion'],
            fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date(),
            fecha_fin=datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date() if request.form.get('fecha_fin') else None,
            tratamiento=request.form.get('tratamiento'),
            dias_tratamiento=request.form.get('dias_tratamiento') or None,
            resultado=request.form.get('resultado'),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(evento)
        db.session.commit()
        flash('Evento de salud registrado exitosamente.', 'success')
        return redirect(url_for('gestion_salud'))
    
    animales = Animal.query.filter_by(finca_id=finca_id).all()
    return render_template('nuevo_evento_salud.html', animales=animales)

@app.route('/salud/vacunacion', methods=['GET', 'POST'])
@login_required
def nueva_vacunacion():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debe seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Crear evento de vacunación
        vacunacion = HistorialSalud(
            animal_id=request.form['animal_id'],
            tipo_evento='vacunacion',
            descripcion=f"Vacuna: {request.form['tipo_vacuna']}",
            fecha_inicio=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            tratamiento=f"Vacuna {request.form['tipo_vacuna']} - Dosis: {request.form.get('dosis', 'N/A')}",
            resultado='aplicada',
            observaciones=request.form.get('observaciones')
        )
        db.session.add(vacunacion)
        db.session.commit()
        flash('Vacunación registrada exitosamente.', 'success')
        return redirect(url_for('gestion_salud'))
    
    animales = Animal.query.filter_by(finca_id=finca_id).all()
    return render_template('nueva_vacunacion.html', animales=animales)

# ============================================================================
# SISTEMA DE SEGUIMIENTO DE PESO
# ============================================================================

@app.route('/camara', methods=['GET', 'POST'])
@login_required
def camara():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    # Guardar/leer URL del stream (IP Webcam)
    if request.method == 'POST':
        url = request.form.get('stream_url', '').strip()
        if url:
            session['stream_url'] = url
            flash('URL de cámara guardada.', 'success')
        return redirect(url_for('camara'))

    stream_url = session.get('stream_url', 'http://10.54.212.146:8080/video')
    return render_template('camara.html', stream_url=stream_url)

@app.route('/grabaciones')
@login_required
def grabaciones():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    # Obtener fecha de la consulta
    fecha_consulta = request.args.get('date')
    
    # Listar archivos de grabaciones
    import os
    recordings_dir = os.path.join('static', 'recordings')
    archivos = []
    if os.path.exists(recordings_dir):
        for archivo in os.listdir(recordings_dir):
            if archivo.endswith('.mp4'):
                fecha_archivo = os.path.splitext(archivo)[0]
                if fecha_consulta and fecha_archivo != fecha_consulta:
                    continue
                archivos.append({
                    'nombre': archivo,
                    'fecha': fecha_archivo
                })
        # Ordenar por fecha descendente
        archivos.sort(key=lambda x: x['fecha'], reverse=True)
    else:
        # Crear directorio si no existe (no destructivo)
        try:
            os.makedirs(recordings_dir, exist_ok=True)
        except Exception:
            pass
    
    return render_template('grabaciones.html', archivos=archivos, fecha_consulta=fecha_consulta)

class RegistroPeso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    peso = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    condicion_corporal = db.Column(db.Integer)  # Escala 1-9
    observaciones = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    animal = db.relationship('Animal', backref='registros_peso', lazy=True)
    usuario = db.relationship('Usuario', lazy=True)

# SISTEMA DE ALERTAS MEJORADO
# ============================================================================

class AlertaPersonalizada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_programada = db.Column(db.DateTime, nullable=False)
    tipo_alerta = db.Column(db.String(50), nullable=False)  # general, animal, vacuna, produccion, empleado
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'))  # Opcional para alertas específicas de animales
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, enviada, cancelada
    enviada = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    repetir = db.Column(db.Boolean, default=False)
    frecuencia = db.Column(db.String(20))  # diaria, semanal, mensual
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='alertas_personalizadas')
    finca = db.relationship('Finca', backref='alertas')
    animal = db.relationship('Animal', backref='alertas')

@app.route('/alertas')
@login_required
def alertas():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    alertas = AlertaPersonalizada.query.filter(
        AlertaPersonalizada.usuario_id == current_user.id,
        AlertaPersonalizada.finca_id == finca_id
    ).order_by(AlertaPersonalizada.fecha_programada.desc()).all()
    
    return render_template('alertas.html', alertas=alertas)

@app.route('/nueva_alerta', methods=['GET', 'POST'])
@login_required
def nueva_alerta():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Combinar fecha y hora
        fecha_str = request.form['fecha']
        hora_str = request.form['hora']
        fecha_programada = datetime.strptime(f"{fecha_str} {hora_str}", '%Y-%m-%d %H:%M')
        
        alerta = AlertaPersonalizada(
            usuario_id=current_user.id,
            finca_id=finca_id,
            titulo=request.form['titulo'],
            descripcion=request.form['descripcion'],
            fecha_programada=fecha_programada,
            tipo_alerta=request.form['tipo_alerta'],
            animal_id=request.form.get('animal_id') if request.form.get('animal_id') else None,
            repetir=bool(request.form.get('repetir')),
            frecuencia=request.form.get('frecuencia') if request.form.get('repetir') else None
        )
        
        db.session.add(alerta)
        db.session.commit()
        
        # Enviar notificación por email
        print(f"[DEBUG] Intentando enviar email a usuario: {current_user.email}")
        try:
            resultado = enviar_notificacion_email(current_user, alerta)
            if resultado:
                flash('Alerta creada y notificación enviada por email.', 'success')
            else:
                flash('Alerta creada pero no se pudo enviar el email.', 'warning')
        except Exception as e:
            print(f"[ERROR] Excepción enviando email: {e}")
            flash('Alerta creada pero error enviando email.', 'warning')
        
        return redirect(url_for('alertas'))
    
    animales = Animal.query.filter_by(finca_id=finca_id).all()
    return render_template('nueva_alerta.html', animales=animales)

@app.route('/editar_alerta/<int:alerta_id>', methods=['GET', 'POST'])
@login_required
def editar_alerta(alerta_id):
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    alerta = AlertaPersonalizada.query.filter_by(
        id=alerta_id, 
        usuario_id=current_user.id, 
        finca_id=finca_id
    ).first_or_404()
    
    if request.method == 'POST':
        # Combinar fecha y hora
        fecha_str = request.form['fecha']
        hora_str = request.form['hora']
        fecha_programada = datetime.strptime(f"{fecha_str} {hora_str}", '%Y-%m-%d %H:%M')
        
        # Actualizar alerta
        alerta.titulo = request.form['titulo']
        alerta.descripcion = request.form['descripcion']
        alerta.fecha_programada = fecha_programada
        alerta.tipo_alerta = request.form['tipo_alerta']
        alerta.animal_id = request.form.get('animal_id') if request.form.get('animal_id') else None
        alerta.repetir = bool(request.form.get('repetir'))
        alerta.frecuencia = request.form.get('frecuencia') if request.form.get('repetir') else None
        
        db.session.commit()
        flash('Alerta actualizada exitosamente.', 'success')
        return redirect(url_for('alertas'))
    
    animales = Animal.query.filter_by(finca_id=finca_id).all()
    return render_template('editar_alerta.html', alerta=alerta, animales=animales)

@app.route('/test_email_alert')
@login_required
def test_email_alert():
    """Ruta de prueba para enviar una alerta de email al usuario admin"""
    try:
        # Crear alerta de prueba
        from datetime import datetime, timedelta
        
        # Buscar usuario admin
        admin_user = Usuario.query.filter_by(username='admin').first()
        if not admin_user:
            return f"Usuario admin no encontrado"
        
        # Obtener finca del admin
        finca = Finca.query.filter_by(usuario_id=admin_user.id).first()
        if not finca:
            return f"No se encontró finca para el usuario admin"
        
        # Crear alerta de prueba
        alerta_prueba = AlertaPersonalizada(
            usuario_id=admin_user.id,
            finca_id=finca.id,
            titulo="Alerta de Prueba - Sistema AgroGest",
            descripcion="Esta es una alerta de prueba para verificar que el sistema de notificaciones por email funciona correctamente.",
            fecha_programada=datetime.now() + timedelta(hours=1),
            tipo_alerta="general",
            animal_id=None,
            repetir=False,
            frecuencia=None
        )
        
        db.session.add(alerta_prueba)
        db.session.commit()
        
        # Enviar email
        print(f"[TEST] Enviando email de prueba a: {admin_user.email}")
        resultado = enviar_notificacion_email(admin_user, alerta_prueba)
        
        if resultado:
            return f"✅ Email de prueba enviado exitosamente a {admin_user.email}. Revisa tu bandeja de entrada."
        else:
            return f"❌ Error enviando email a {admin_user.email}. Revisa los logs del servidor."
            
    except Exception as e:
        import traceback
        return f"❌ Error en prueba de email: {str(e)}<br><pre>{traceback.format_exc()}</pre>"

def verificar_alertas_pendientes():
    """Función que verifica y envía alertas pendientes"""
    if not EMAIL_AVAILABLE:
        return
    
    try:
        with app.app_context():
            ahora = datetime.now()
            fecha_actual = ahora.date()
            hora_actual = ahora.time()
            
            # Buscar alertas que deben enviarse ahora (con margen de 2 minutos)
            margen_minutos = timedelta(minutes=2)
            hora_limite = (ahora + margen_minutos).time()
            
            alertas_pendientes = AlertaPersonalizada.query.filter(
                AlertaPersonalizada.fecha_programada <= ahora,
                AlertaPersonalizada.estado == 'pendiente'
            ).all()
            
            for alerta in alertas_pendientes:
                try:
                    # Obtener usuario y su email
                    usuario = Usuario.query.get(alerta.usuario_id)
                    if usuario and usuario.email:
                        resultado = enviar_notificacion_email(usuario, alerta)
                        if resultado:
                            alerta.estado = 'enviada'
                            db.session.commit()
                            print(f"[INFO] Alerta enviada: {alerta.titulo} a {usuario.email}")
                        else:
                            print(f"[ERROR] No se pudo enviar alerta: {alerta.titulo}")
                except Exception as e:
                    print(f"[ERROR] Error procesando alerta {alerta.id}: {str(e)}")
                    continue
                    
    except Exception as e:
        print(f"[ERROR] Error en verificar_alertas_pendientes: {str(e)}")

def iniciar_scheduler():
    """Inicia el scheduler de alertas"""
    if not SCHEDULER_AVAILABLE:
        print("[WARNING] Scheduler no disponible - alertas automáticas deshabilitadas")
        return None
        
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=verificar_alertas_pendientes,
        trigger=IntervalTrigger(seconds=60),  # Verificar cada minuto
        id='verificar_alertas',
        name='Verificar alertas pendientes',
        replace_existing=True
    )
    scheduler.start()
    
    # Asegurar que el scheduler se cierre al terminar la aplicación
    atexit.register(lambda: scheduler.shutdown())
    
    print("[INFO] Scheduler de alertas iniciado - verificando cada 60 segundos")
    return scheduler

@app.route('/cancelar_alerta/<int:alerta_id>', methods=['POST'])
@login_required
def cancelar_alerta(alerta_id):
    """Cancela una alerta específica"""
    try:
        finca_id = session.get('finca_id')
        if not finca_id:
            return jsonify({'success': False, 'error': 'No hay finca seleccionada'}), 400
        
        alerta = AlertaPersonalizada.query.filter_by(
            id=alerta_id, 
            usuario_id=current_user.id, 
            finca_id=finca_id
        ).first()
        
        if not alerta:
            return jsonify({'success': False, 'error': 'Alerta no encontrada'}), 404
        
        # Cambiar estado a cancelada
        alerta.estado = 'cancelada'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Alerta cancelada correctamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/eliminar_alerta/<int:alerta_id>', methods=['POST'])
@login_required
def eliminar_alerta(alerta_id):
    """Elimina permanentemente una alerta específica"""
    try:
        finca_id = session.get('finca_id')
        if not finca_id:
            return jsonify({'success': False, 'error': 'No hay finca seleccionada'}), 400
        
        alerta = AlertaPersonalizada.query.filter_by(
            id=alerta_id, 
            usuario_id=current_user.id, 
            finca_id=finca_id
        ).first()
        
        if not alerta:
            return jsonify({'success': False, 'error': 'Alerta no encontrada'}), 404
        
        # Eliminar permanentemente de la base de datos
        db.session.delete(alerta)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Alerta eliminada permanentemente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerta_detalle/<int:alerta_id>')
@login_required
def api_alerta_detalle(alerta_id):
    """API para obtener detalles completos de una alerta"""
    finca_id = session.get('finca_id')
    if not finca_id:
        return jsonify({'error': 'No hay finca seleccionada'}), 400
    
    alerta = AlertaPersonalizada.query.filter_by(
        id=alerta_id, 
        usuario_id=current_user.id, 
        finca_id=finca_id
    ).first()
    
    if not alerta:
        return jsonify({'error': 'Alerta no encontrada'}), 404
    
    # Obtener información del animal si existe
    animal_info = None
    if alerta.animal_id:
        animal = Animal.query.get(alerta.animal_id)
        if animal:
            animal_info = {
                'identificacion': animal.identificacion,
                'nombre': animal.nombre or 'Sin nombre',
                'tipo': animal.tipo,
                'raza': animal.raza
            }
    
    return jsonify({
        'id': alerta.id,
        'titulo': alerta.titulo,
        'descripcion': alerta.descripcion,
        'tipo_alerta': alerta.tipo_alerta,
        'fecha_programada': alerta.fecha_programada.strftime('%d/%m/%Y %H:%M'),
        'estado': alerta.estado,
        'fecha_creacion': alerta.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
        'repetir': alerta.repetir,
        'frecuencia': alerta.frecuencia,
        'animal': animal_info
    })

# ============================================================================
# API PARA OBTENER ANIMALES EN UBICACIONES
# ============================================================================

@app.route('/api/animales_en_ubicacion')
@login_required
def api_animales_en_ubicacion():
    """API para obtener animales en una ubicación específica"""
    tipo = request.args.get('tipo')  # 'potrero' o 'ubicacion'
    ubicacion_id = request.args.get('id')
    
    if not tipo or not ubicacion_id:
        return jsonify({'error': 'Parámetros requeridos: tipo e id'}), 400
    
    finca_id = session.get('finca_id')
    if not finca_id:
        return jsonify({'error': 'No hay finca seleccionada'}), 400
    
    try:
        if tipo == 'potrero':
            animales = Animal.query.filter_by(
                finca_id=finca_id,
                potrero_id=int(ubicacion_id)
            ).all()
        elif tipo == 'ubicacion':
            animales = Animal.query.filter_by(
                finca_id=finca_id,
                ubicacion_id=int(ubicacion_id)
            ).all()
        else:
            return jsonify({'error': 'Tipo no válido'}), 400
        
        animales_data = []
        for animal in animales:
            animales_data.append({
                'id': animal.id,
                'identificacion': animal.identificacion,
                'nombre': animal.nombre,
                'tipo': animal.tipo,
                'raza': animal.raza,
                'peso': animal.peso,
                'estado': animal.estado,
                'sexo': animal.sexo
            })
        
        return jsonify({'animales': animales_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SISTEMA DE SEGUIMIENTO DE PESO
# ============================================================================

@app.route('/peso')
@login_required
def seguimiento_peso():
    """Dashboard de seguimiento de peso"""
    if 'finca_id' not in session:
        flash('Selecciona una finca para ver el seguimiento de peso')
        return redirect(url_for('fincas'))
    
    finca_id = session['finca_id']
    
    # Estadísticas básicas
    total_registros = db.session.query(func.count(RegistroPeso.id))\
        .join(Animal, RegistroPeso.animal_id == Animal.id)\
        .filter(Animal.finca_id == finca_id)\
        .scalar() or 0
    total_animales = db.session.query(func.count(func.distinct(Animal.id)))\
        .join(RegistroPeso, RegistroPeso.animal_id == Animal.id)\
        .filter(Animal.finca_id == finca_id)\
        .scalar() or 0
    
    # Peso promedio actual
    peso_promedio = db.session.query(func.avg(RegistroPeso.peso))\
        .join(Animal, RegistroPeso.animal_id == Animal.id)\
        .filter(Animal.finca_id == finca_id)\
        .scalar() or 0
    
    # Registros recientes (evitar cargar la entidad completa para no requerir columnas inexistentes)
    filas_recientes = db.session.query(
            RegistroPeso.id,
            RegistroPeso.animal_id,
            RegistroPeso.peso,
            RegistroPeso.fecha,
            RegistroPeso.condicion_corporal,
            RegistroPeso.observaciones,
            Animal.identificacion,
            Animal.nombre
        )\
        .join(Animal, RegistroPeso.animal_id == Animal.id)\
        .filter(Animal.finca_id == finca_id)\
        .order_by(RegistroPeso.fecha.desc())\
        .limit(10).all()

    # Adaptar a estructura esperada por la plantilla: (registro_like, identificacion, nombre)
    registros_recientes = []
    for fila in filas_recientes:
        (_id, _animal_id, peso, fecha, condicion_corporal, observaciones, identificacion, nombre) = fila
        registro_like = SimpleNamespace(
            peso=peso,
            condicion_corporal=condicion_corporal,
            fecha=fecha,
            observaciones=observaciones
        )
        registros_recientes.append((registro_like, identificacion, nombre))
    
    stats = {
        'total_registros': total_registros,
        'total_animales': total_animales,
        'peso_promedio': round(peso_promedio, 2) if peso_promedio else 0,
        'registros_recientes': registros_recientes
    }
    
    return render_template('seguimiento_peso.html', stats=stats)

@app.route('/peso/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_registro_peso():
    """Crear nuevo registro de peso"""
    if 'finca_id' not in session:
        flash('Selecciona una finca para registrar peso')
        return redirect(url_for('fincas'))
    
    finca_id = session['finca_id']
    
    if request.method == 'POST':
        try:
            animal_id = request.form['animal_id']
            peso = float(request.form['peso'])
            fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            condicion_corporal = request.form.get('condicion_corporal', type=int)
            observaciones = request.form.get('observaciones', '')
            
            # Verificar que el animal pertenece a la finca
            animal = Animal.query.filter_by(id=animal_id, finca_id=finca_id).first()
            if not animal:
                flash('Animal no encontrado', 'error')
                return redirect(url_for('nuevo_registro_peso'))
            
            # Crear registro
            registro = RegistroPeso(
                animal_id=animal_id,
                finca_id=finca_id,
                peso=peso,
                fecha=fecha,
                condicion_corporal=condicion_corporal,
                observaciones=observaciones,
                usuario_id=current_user.id
            )
            
            db.session.add(registro)
            db.session.commit()
            
            flash('Registro de peso guardado exitosamente', 'success')
            return redirect(url_for('seguimiento_peso'))
            
        except ValueError as e:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash('Error al guardar el registro', 'error')
            db.session.rollback()
    
    # Obtener animales de la finca
    # Corregido: ordenar por un campo existente (identificacion) en lugar de un campo inexistente (numero)
    animales = Animal.query.filter_by(finca_id=finca_id).order_by(Animal.identificacion).all()
    
    return render_template('nuevo_registro_peso.html', animales=animales)

# SISTEMA DE REPORTES AVANZADO CON PDF
# ============================================================================

@app.route('/reportes')
@login_required
def reportes():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    # Estadísticas generales para mostrar en la página de reportes
    total_animales = Animal.query.filter_by(finca_id=finca_id).count()
    total_vacunas = HistorialSalud.query.join(Animal).filter(
        Animal.finca_id == finca_id,
        HistorialSalud.tipo_evento == 'vacunacion'
    ).count()
    total_empleados = Empleado.query.filter_by(finca_id=finca_id).count()
    total_alertas = AlertaPersonalizada.query.filter_by(finca_id=finca_id).count()
    
    stats = {
        'total_animales': total_animales,
        'total_vacunas': total_vacunas,
        'total_empleados': total_empleados,
        'total_alertas': total_alertas
    }
    
    return render_template('reportes.html', stats=stats)

def generar_pdf_reporte(tipo_reporte, datos, finca_nombre):
    """Genera un PDF para cualquier tipo de reporte"""
    if not REPORTLAB_AVAILABLE:
        # Crear un PDF simple sin ReportLab
        buffer = BytesIO()
        buffer.write(b"PDF generation not available. Please install reportlab: pip install reportlab")
        buffer.seek(0)
        return buffer
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e293b'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#334155'),
        alignment=TA_LEFT,
        spaceAfter=20
    )
    
    # Título del reporte
    story.append(Paragraph(f"AgroGest - {finca_nombre}", title_style))
    story.append(Paragraph(f"Reporte de {tipo_reporte.title()}", subtitle_style))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    table_data = None
    if datos:
        # Crear tabla con los datos
        if tipo_reporte == 'animales':
            headers = ['ID', 'Identificación', 'Tipo', 'Raza', 'Sexo', 'Peso', 'Estado']
            table_data = [headers]
            for animal in datos:
                table_data.append([
                    str(animal.id),
                    animal.identificacion,
                    animal.tipo,
                    animal.raza,
                    animal.sexo or 'N/A',
                    f"{animal.peso} kg" if animal.peso else 'N/A',
                    animal.estado
                ])
        
        elif tipo_reporte == 'vacunas':
            headers = ['Animal', 'Tipo Vacuna', 'Fecha', 'Descripción', 'Estado']
            table_data = [headers]
            for evento in datos:
                table_data.append([
                    evento.animal.identificacion,
                    evento.descripcion.split(':')[1].strip() if ':' in evento.descripcion else evento.descripcion,
                    evento.fecha_inicio.strftime('%d/%m/%Y'),
                    evento.tratamiento or 'N/A',
                    evento.resultado or 'N/A'
                ])
        
        elif tipo_reporte == 'empleados':
            headers = ['Nombre', 'Cargo', 'Teléfono', 'Email', 'Estado']
            table_data = [headers]
            for empleado in datos:
                table_data.append([
                    f"{empleado.nombre} {empleado.apellido}",
                    empleado.cargo,
                    getattr(empleado, 'telefono', None) or 'N/A',
                    getattr(empleado, 'email', None) or 'N/A',
                    empleado.estado
                ])
        
        elif tipo_reporte == 'alertas':
            headers = ['Título', 'Tipo', 'Fecha Programada', 'Estado', 'Animal']
            table_data = [headers]
            for alerta in datos:
                table_data.append([
                    alerta.titulo,
                    alerta.tipo_alerta,
                    alerta.fecha_programada.strftime('%d/%m/%Y %H:%M'),
                    alerta.estado,
                    alerta.animal.identificacion if alerta.animal else 'N/A'
                ])
        
        elif tipo_reporte == 'salud':
            headers = ['Animal', 'Tipo Evento', 'Descripción', 'Inicio', 'Fin', 'Resultado']
            table_data = [headers]
            for ev in datos:
                table_data.append([
                    getattr(getattr(ev, 'animal', None), 'identificacion', 'N/A'),
                    getattr(ev, 'tipo_evento', 'N/A'),
                    getattr(ev, 'descripcion', 'N/A'),
                    ev.fecha_inicio.strftime('%d/%m/%Y') if getattr(ev, 'fecha_inicio', None) else 'N/A',
                    ev.fecha_fin.strftime('%d/%m/%Y') if getattr(ev, 'fecha_fin', None) else 'N/A',
                    getattr(ev, 'resultado', 'N/A') or 'N/A'
                ])
        
        elif tipo_reporte == 'produccion':
            headers = ['Animal', 'Tipo', 'Cantidad', 'Unidad', 'Fecha', 'Calidad']
            table_data = [headers]
            for pr in datos:
                table_data.append([
                    getattr(getattr(pr, 'animal', None), 'identificacion', 'N/A'),
                    getattr(pr, 'tipo_produccion', 'N/A'),
                    getattr(pr, 'cantidad', 'N/A'),
                    getattr(pr, 'unidad', 'N/A'),
                    pr.fecha.strftime('%d/%m/%Y') if getattr(pr, 'fecha', None) else 'N/A',
                    getattr(pr, 'calidad', 'N/A') or 'N/A'
                ])
        
        elif tipo_reporte == 'inventario':
            headers = ['Producto', 'Cantidad', 'Unidad', 'Precio Unitario', 'Fecha Ingreso', 'Vencimiento']
            table_data = [headers]
            for it in datos:
                table_data.append([
                    getattr(it, 'producto', 'N/A'),
                    getattr(it, 'cantidad', 'N/A'),
                    getattr(it, 'unidad', 'N/A'),
                    getattr(it, 'precio_unitario', 'N/A'),
                    it.fecha_ingreso.strftime('%d/%m/%Y') if getattr(it, 'fecha_ingreso', None) else 'N/A',
                    it.fecha_vencimiento.strftime('%d/%m/%Y') if getattr(it, 'fecha_vencimiento', None) else 'N/A'
                ])
        
        # Fallback genérico si no se preparó table_data
        if table_data is None and len(datos) > 0:
            # Tomar algunos campos comunes si existen
            headers = []
            sample = datos[0]
            candidate_fields = ['id','identificacion','nombre','tipo','descripcion','fecha','estado']
            for f in candidate_fields:
                if hasattr(sample, f):
                    headers.append(f.title())
            if not headers:
                headers = ['Objeto']
                table_data = [headers] + [[str(item)] for item in datos]
            else:
                table_data = [headers]
                for item in datos:
                    row = []
                    for f in candidate_fields:
                        if hasattr(item, f):
                            val = getattr(item, f)
                            if hasattr(val, 'strftime'):
                                try:
                                    val = val.strftime('%d/%m/%Y')
                                except Exception:
                                    val = str(val)
                            row.append(val if val is not None else 'N/A')
                    table_data.append(row)

        # Crear y estilizar la tabla sólo si hay datos
        if table_data:
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(table)
    else:
        story.append(Paragraph("No hay datos disponibles para este reporte.", styles['Normal']))
    
    # Pie de página
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generado por AgroGest - Sistema de Gestión Ganadera", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/reporte_pdf/<tipo>')
@login_required
def reporte_pdf(tipo):
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    finca = Finca.query.get(finca_id)
    finca_nombre = finca.nombre if finca else 'Finca Desconocida'
    
    # Obtener datos según el tipo de reporte
    if tipo == 'animales':
        datos = Animal.query.filter_by(finca_id=finca_id).all()
    elif tipo == 'vacunas':
        datos = HistorialSalud.query.join(Animal).filter(
            Animal.finca_id == finca_id,
            HistorialSalud.tipo_evento == 'vacunacion'
        ).all()
    elif tipo == 'salud':
        datos = HistorialSalud.query.join(Animal).filter(
            Animal.finca_id == finca_id
        ).all()
    elif tipo == 'empleados':
        datos = Empleado.query.filter_by(finca_id=finca_id).all()
    elif tipo == 'alertas':
        datos = AlertaPersonalizada.query.filter_by(finca_id=finca_id).all()
    elif tipo == 'produccion':
        datos = RegistroProduccion.query.join(Animal).filter(
            Animal.finca_id == finca_id
        ).all()
    elif tipo == 'inventario':
        datos = InventarioItem.query.filter_by(finca_id=finca_id).all() if 'InventarioItem' in globals() else []
    else:
        flash('Tipo de reporte no válido.', 'error')
        return redirect(url_for('reportes'))
    
    # Generar PDF
    pdf_buffer = generar_pdf_reporte(tipo, datos, finca_nombre)
    
    # Crear respuesta
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_{tipo}_{finca_nombre}_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return response

# ============================================================================
# CONFIGURACIÓN DE FINCA MEJORADA
# ============================================================================

@app.route('/configuracion_finca')
@login_required
def configuracion_finca():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    finca = Finca.query.get_or_404(finca_id)
    return render_template('configuracion_finca.html', finca=finca)

@app.route('/api/perfil_usuario')
@login_required
def api_perfil_usuario():
    """API para obtener datos del perfil del usuario actual"""
    try:
        usuario = Usuario.query.get(current_user.id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'username': usuario.username,
            'email': usuario.email,
            'telefono': usuario.telefono,
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'rol': usuario.rol
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/actualizar_perfil', methods=['POST'])
@login_required
def api_actualizar_perfil():
    """API para actualizar datos del perfil del usuario"""
    try:
        data = request.get_json()
        usuario = Usuario.query.get(current_user.id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Actualizar campos si están presentes en la petición
        if 'email' in data:
            usuario.email = data['email']
        if 'telefono' in data:
            usuario.telefono = data['telefono']
        if 'nombre' in data:
            usuario.nombre = data['nombre']
        if 'apellido' in data:
            usuario.apellido = data['apellido']
        
        db.session.commit()
        
        return jsonify({'message': 'Perfil actualizado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat_agro', methods=['POST'])
@login_required
def api_chat_agro():
    """Asistente de chat enfocado en ganadería y agricultura.
    Acepta una pregunta en JSON: {"message": "..."} y retorna {"answer": "..."}.
    Solo responde sobre temas agropecuarios (ganado, potreros, pastos, salud animal, producción, bioseguridad, etc.).
    """
    try:
        user_msg = ''
        image_bytes = None
        image_mime = None
        page_context = ''

        if request.content_type and 'multipart/form-data' in request.content_type:
            user_msg = (request.form.get('message') or '').strip()
            page_context = (request.form.get('context') or '').strip()
            image = request.files.get('image')
            if image and image.filename:
                image_bytes = image.read()
                image_mime = image.mimetype or 'image/jpeg'
        else:
            data = request.get_json(silent=True) or {}
            user_msg = (data.get('message') or '').strip()
            page_context = (data.get('context') or '').strip()

        if not user_msg and not image_bytes:
            return jsonify({'error': 'Mensaje vacío. Escribe una pregunta relacionada con el campo agropecuario.'}), 400

        msg_for_domain = (user_msg or '').lower()

        # Palabras clave del dominio agropecuario (para fallback cuando no hay Gemini)
        agro_keywords = [
            'vaca','bovino','ganado','ternero','novillo','toro','veterinario','potrero','pasto','forraje',
            'rotación','rotacion','heno','ensilaje','leche','ordeño','ordeño','rumen','desparasitación','desparasitacion',
            'vacuna','brucelosis','aftosa','clostridiosis','mastitis','fiebre','cojera','parásitos','parasitos','garrapata',
            'pastura','suplemento','mineral','sal','reproducción','reproduccion','celo','inseminación','inseminacion',
            'parto','destete','engorde','pesaje','peso','condición corporal','condicion corporal','bioseguridad',
            'corrales','bebedero','comederos','calostro','cría','cria','nutrición','nutricion','fertilizante','suelo',
            'agricola','agricultura','finca','granja','forrajes','rabia','leptospirosis','pastos','rotacional'
        ]

        # Política: si hay Gemini disponible, permitimos temas generales (incluida la página). Si NO hay Gemini, restringimos a agro.
        # Verificar/Configurar Gemini en tiempo de petición
        _genai_ref = _check_gemini()
        if not GEMINI_AVAILABLE:
            # Si hay imagen pero no texto, permitimos pasar el filtro (análisis visual solo si fuese posible)
            if not image_bytes and not any(k in msg_for_domain for k in agro_keywords):
                return jsonify({'error': 'Solo puedo responder preguntas sobre ganadería y agricultura. Por favor, pregunta sobre animales, potreros, pasturas, salud, reproducción o producción.'}), 400

        # Si hay Gemini y (hay imagen o queremos mejor respuesta), usar Gemini
        if GEMINI_AVAILABLE and (image_bytes or user_msg):
            # Si hay contexto de página, el usuario puede estar preguntando sobre la página actual.
            # Instruimos a Gemini a responder en español y, si hay contexto, tenerlo en cuenta.
            prompt_parts = []
            system_preamble = (
                'Responde SIEMPRE en español. '
                'Eres un asistente útil para el sistema AgroGest (gestión ganadera). '
                'Puedes responder preguntas generales o sobre la página actual si se proporciona contexto. '
                'Cuando la pregunta sea agropecuaria, incluye buenas prácticas y advertencias sanitarias si aplica.'
            )
            prompt_parts.append(system_preamble)
            if page_context:
                prompt_parts.append(f"Contexto de página (URL/Título/Notas):\n{page_context}\n")
            prompt_parts.append(f"Pregunta del usuario: {user_msg or '(Análisis basado en imagen)'}")
            prompt = '\n\n'.join(prompt_parts)
            try:
                answer = _gemini_responder(prompt, image_bytes, image_mime)
                if answer:
                    return jsonify({'answer': answer})
            except Exception as ge:
                # Si falla Gemini, caer a reglas
                pass

        # Respuesta basada en reglas (fallback)
        answer = _responder_agro((user_msg or '').lower())
        if image_bytes and not GEMINI_AVAILABLE:
            answer += '\n\nNota: Recibí una imagen, pero no puedo analizarla sin configurar Gemini. Agrega la variable GOOGLE_API_KEY para habilitar análisis de imágenes.'
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': f'Error procesando la solicitud: {str(e)}'}), 500

def _gemini_responder(prompt: str, image_bytes: bytes | None, image_mime: str | None) -> str | None:
    # Reconfirmar que Gemini está disponible
    _genai_ref = _check_gemini()
    if not GEMINI_AVAILABLE:
        return None
    # Seleccionar modelo multimodal si hay imagen
    model_name = 'gemini-1.5-flash' if image_bytes else 'gemini-1.5-flash'
    model = genai.GenerativeModel(model_name)
    if image_bytes:
        # Construir contenido con imagen
        img_part = { 'mime_type': image_mime or 'image/jpeg', 'data': image_bytes }
        resp = model.generate_content([
            {'text': prompt},
            img_part
        ])
    else:
        resp = model.generate_content(prompt)
    text = getattr(resp, 'text', None)
    if text:
        return text.strip()
    # Algunas respuestas vienen en candidates
    try:
        return resp.candidates[0].content.parts[0].text.strip()
    except Exception:
        return None

@app.route('/api/chat_status')
@login_required
def api_chat_status():
    """Diagnóstico: indica si Gemini está disponible en este proceso."""
    _ = _check_gemini()
    return jsonify({ 'gemini': GEMINI_AVAILABLE })

def _responder_agro(msg: str) -> str:
    """Respuesta sencilla basada en reglas/keywords para preguntas frecuentes del ámbito agropecuario."""
    # Base de conocimientos simple
    rules = [
        # Desparasitación
        (['desparas', 'parasito', 'garrapata', 'lombr'],
         'La desparasitación en bovinos suele realizarse cada 3 a 6 meses según el nivel de parasitismo y manejo. Alterna principios activos (ivermectina, levamisol, albendazol) y refuerza con control de garrapatas y manejo rotacional de potreros. Siempre consulta al veterinario para dosificación por peso.'),

        # Vacunación
        (['vacun', 'brucelosis', 'aftosa', 'clostridio', 'leptosp'],
         'Un plan básico de vacunación bovina incluye: fiebre aftosa y brucelosis según normativa local, y clostridiosis (2 dosis iniciales + refuerzos anuales). Ajusta el esquema a la región y normativa sanitaria. Mantén la cadena de frío y registra lote y fecha.'),

        # Pastoreo rotacional
        (['pastore', 'rotacion', 'rotación', 'potrero', 'carga animal'],
         'Para pastoreo rotacional, divide potreros y ajusta la carga animal. Descansa el potrero 25–35 días (según especie forrajera y clima) y entra cuando el pasto tenga entre 25–35 cm. Evita el sobrepastoreo para proteger el rebrote y la persistencia de la pastura.'),

        # Condición corporal y peso
        (['condicion corporal', 'condición corporal', 'peso', 'engorde', 'bc'],
         'La condición corporal (1–5 o 1–9) ayuda a decidir suplementación y manejo reproductivo. Apunta a 3–3.5 al servicio/parto. Pesa regularmente y ofrece minerales y energía en época seca para evitar pérdidas.'),

        # Reproducción y celo
        (['celo', 'insemin', 'monta', 'servicio', 'preñez', 'prenez', 'prenez'],
         'Detecta celo observando inquietud, monta entre vacas, vulva húmeda y mucosa. Inseminar 12 horas después de visto el celo (regla AM-PM). Realiza diagnóstico de preñez a los 45–60 días y registra servicios y partos.'),

        # Mastitis y ordeño
        (['mastit', 'ordeñ', 'orden', 'leche grumos', 'inflamacion ubre'],
         'Para prevenir mastitis: rutina de pre y pos sellado, higiene en pezones, primeros chorros a descarte y mantenimiento del equipo de ordeño. Trata casos clínicos con antibiótico indicado por veterinario y respeta los períodos de retiro de leche.'),

        # Terneros y calostro
        (['ternero', 'becerro', 'calostro', 'destete'],
         'Ofrece calostro de calidad en las primeras 2 horas de vida (10% del peso vivo en 24 h). Desinfecta ombligo, provee sombra y cama seca. Destete común a 6–8 meses según peso y oferta forrajera; introduce concentrado starter gradualmente.'),

        # Suplementación mineral
        (['mineral', 'sal proteinada', 'bloque'],
         'Mantén sales minerales a libre acceso, con macro y microminerales (Ca, P, Na, Cu, Zn, Se). En época seca considera sal proteinada para sostener consumo de forraje y ganancia de peso.'),

        # Bioseguridad
        (['biosegur', 'cuarentena', 'ingreso animales', 'sanitario'],
         'Aplica bioseguridad: cuarentena de animales nuevos 21–30 días, control de visitantes y vehículos, limpieza de equipos, registro sanitario y control de vectores. Esto reduce brotes de enfermedades en la finca.'),
    ]

    for keys, resp in rules:
        if any(k in msg for k in keys):
            return resp

    # Respuesta por defecto
    return (
        'Puedo ayudarte con planes de vacunación, desparasitación, manejo de potreros, pasturas, reproducción, ordeño, bioseguridad y más. '
        'Dime qué necesitas (por ejemplo: "Plan de vacunación para terneras", "¿Cómo organizar pastoreo rotacional?", "Recomendaciones para prevenir mastitis").'
    )

@app.route('/actualizar_finca', methods=['POST'])
@login_required
def actualizar_finca():
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero.', 'warning')
        return redirect(url_for('index'))
    
    finca = Finca.query.get_or_404(finca_id)
    
    finca.nombre = request.form['nombre']
    finca.direccion = request.form['direccion']
    finca.telefono = request.form['telefono']
    finca.email = request.form['email']
    finca.descripcion = request.form.get('descripcion')
    
    db.session.commit()
    flash('Configuración de finca actualizada exitosamente.', 'success')
    return redirect(url_for('configuracion_finca'))

@app.route('/simulador_movil')
def simulador_movil():
    """Simulador móvil deshabilitado. Solo se mantiene la versión web."""
    return ("Simulador móvil deshabilitado", 404)

if __name__ == '__main__':
    try:
        print('>>> Iniciando Sistema de Gestion Ganadera...')
        print('>>> Accede a: http://localhost:5000')
        
        print('[DEBUG] Entrando al bloque principal')
        with app.app_context():
            print('[DEBUG] Creando tablas de la base de datos...')
            db.create_all()
            
            # Crear usuario admin por defecto si no existe
            if not Usuario.query.filter_by(username='admin').first():
                print('[DEBUG] Creando usuario admin por defecto...')
                admin = Usuario(
                    username='admin',
                    email='admin@finca.com',
                    password_hash=generate_password_hash('admin123'),
                    nombre='Administrador',
                    apellido='del Sistema',
                    telefono='3001234567',
                    direccion='Finca',
                    rol='admin')
                db.session.add(admin)
                db.session.commit()
                print('OK Usuario administrador creado:')
                print('   Usuario: admin')
                print('   Contraseña: admin123')
            
            # Iniciar el scheduler de alertas si está disponible
            if SCHEDULER_AVAILABLE:
                print('[DEBUG] Iniciando scheduler de alertas...')
                scheduler = iniciar_scheduler()
            
            # Iniciar el servidor en todas las interfaces de red (0.0.0.0) en el puerto 5000
            print('[DEBUG] Iniciando servidor...')
            print('>>> La aplicación está disponible en tu red local. Para acceder desde tu teléfono:')
            print('>>> 1. Asegúrate de que tu teléfono esté conectado a la misma red WiFi que esta computadora')
            print('>>> 2. Abre un navegador en tu teléfono y ve a la dirección que se muestra a continuación:')
            
            # Obtener la dirección IP de la red local
            import socket
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            print(f'>>> http://{ip_address}:5000')
            print('>>> Usuario: admin')
            print('>>> Contraseña: admin123')
            
            # Iniciar el servidor
            app.run(host='0.0.0.0', port=5000, debug=True)
            
    except Exception as e:
        print('[ERROR] Excepción al iniciar la aplicación:')
        import traceback
        traceback.print_exc()