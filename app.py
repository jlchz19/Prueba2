from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os
from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finca_ganadera.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si la extensión del archivo es permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

db = SQLAlchemy(app)
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
    rol = db.Column(db.String(20), default='admin')

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identificacion = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100))  # Nombre opcional del animal
    tipo = db.Column(db.String(20), nullable=False)  # vaca, cerdo, etc.
    raza = db.Column(db.String(50), nullable=False)
    sexo = db.Column(db.String(10))  # macho, hembra
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    peso_nacimiento = db.Column(db.Float)  # Peso al nacer
    peso = db.Column(db.Float, nullable=False)  # Peso actual
    color_señas = db.Column(db.String(200))  # Color o señas particulares
    estado = db.Column(db.String(20), default='activo')  # activo, en_produccion, gestante, etc.
    ubicacion_actual = db.Column(db.String(100))  # Ubicación actual
    potrero_id = db.Column(db.Integer, db.ForeignKey('potrero.id'))
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    imagen = db.Column(db.String(200))  # Ruta a la imagen del animal
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'))
    # Relación con la finca
    finca = db.relationship('Finca', backref=db.backref('animales', lazy=True))
    # Relación con el potrero
    potrero = db.relationship('Potrero', backref=db.backref('animales', lazy=True))
    # Relación con el historial de peso
    historial_peso = db.relationship('HistorialPeso', backref='animal', lazy=True)

class Potrero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    area = db.Column(db.Float, nullable=False)  # en hectáreas
    capacidad = db.Column(db.Integer, nullable=False)  # número máximo de animales
    estado = db.Column(db.String(20), default='disponible')  # disponible, ocupado, mantenimiento
    funcion = db.Column(db.String(200), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'))
    # Relación con la finca
    finca = db.relationship('Finca', backref=db.backref('potreros', lazy=True))

class Vacuna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_vacuna = db.Column(db.String(100), nullable=False)
    fecha_aplicacion = db.Column(db.Date, nullable=False)
    fecha_proxima = db.Column(db.Date, nullable=False)
    observaciones = db.Column(db.Text)
    aplicada_por = db.Column(db.String(100), nullable=False)

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

class Produccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_produccion = db.Column(db.String(50), nullable=False)  # leche, carne, etc.
    cantidad = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)  # litros, kg, etc.
    fecha = db.Column(db.Date, nullable=False)
    calidad = db.Column(db.String(20), default='buena')  # buena, regular, mala

class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.Date)
    categoria = db.Column(db.String(50), nullable=False)  # alimento, medicina, equipos, etc.

class HistorialPeso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    peso = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo_medicion = db.Column(db.String(50))  # destete, mensual, sacrificio, etc.
    observaciones = db.Column(db.Text)

class EventoSalud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=False)  # enfermedad, lesión, tratamiento, etc.
    descripcion = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    tratamiento = db.Column(db.Text)
    resultado = db.Column(db.String(50))  # recuperación total, parcial, en proceso, etc.
    observaciones = db.Column(db.Text)
    # Relación con el animal
    animal = db.relationship('Animal', backref=db.backref('eventos_salud', lazy=True))

class Alimentacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_alimento = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100))
    cantidad = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)  # kg, g, lb, etc.
    fecha = db.Column(db.Date, nullable=False)
    observaciones = db.Column(db.Text)
    # Relación con el animal
    animal = db.relationship('Animal', backref=db.backref('alimentaciones', lazy=True))

class Reproductivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=False)  # celo, inseminación, parto, etc.
    fecha = db.Column(db.Date, nullable=False)
    detalles = db.Column(db.Text)
    resultado = db.Column(db.String(50))  # exitoso, fallido, en proceso
    observaciones = db.Column(db.Text)
    # Relación con el animal
    animal = db.relationship('Animal', backref=db.backref('eventos_reproductivos', lazy=True))

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=False)  # venta, muerte, traslado, etc.
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Float)  # valor de venta, costo, etc.
    destino = db.Column(db.String(200))  # comprador, destino de traslado, etc.
    observaciones = db.Column(db.Text)
    # Relación con el animal
    animal = db.relationship('Animal', backref=db.backref('eventos', lazy=True))

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='activo')  # activo, inactivo
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'))
    # Relación con la finca
    finca = db.relationship('Finca', backref=db.backref('clientes', lazy=True))

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
    # Relaciones mínimas para evitar errores
    # animales = db.relationship('Animal', backref='finca', lazy=True)
    # potreros = db.relationship('Potrero', backref='finca', lazy=True)
    # empleados = db.relationship('Empleado', backref='finca', lazy=True)
    # vacunas = db.relationship('Vacuna', backref='finca', lazy=True)
    # producciones = db.relationship('Produccion', backref='finca', lazy=True)
    # inventarios = db.relationship('Inventario', backref='finca', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas principales
@app.route('/')
@login_required
def index():
    # Verificar si hay una finca seleccionada
    finca_id = session.get('finca_id')
    no_finca = True
    finca = None
    
    if finca_id:
        finca = Finca.query.get(finca_id)
        if finca:
            no_finca = False
    
    # Si no hay finca seleccionada, mostrar vista global
    if no_finca:
        total_fincas = Finca.query.filter_by(usuario_id=current_user.id).count()
        total_animales = Animal.query.join(Finca).filter(Finca.usuario_id == current_user.id).count()
        total_potreros = Potrero.query.join(Finca).filter(Finca.usuario_id == current_user.id).count()
        total_empleados = 0  # Implementar cuando se agregue la relación con empleados
        
        # Datos para gráfico de distribución de animales por finca
        fincas_usuario = Finca.query.filter_by(usuario_id=current_user.id).all()
        finca_labels = [f.nombre for f in fincas_usuario]
        finca_data = [Animal.query.filter_by(finca_id=f.id).count() for f in fincas_usuario]
        
        # Animales recientes
        animales_recientes = Animal.query.join(Finca).filter(Finca.usuario_id == current_user.id).order_by(Animal.fecha_ingreso.desc()).limit(5).all()
    else:
        # Datos específicos de la finca seleccionada
        total_animales = Animal.query.filter_by(finca_id=finca_id).count()
        total_potreros = Potrero.query.filter_by(finca_id=finca_id).count()
        total_empleados = 0  # Implementar cuando se agregue la relación con empleados
        total_fincas = 1
        
        # Datos para gráficos específicos de la finca
        finca_labels = []
        finca_data = []
        
        # Animales recientes de la finca
        animales_recientes = Animal.query.filter_by(finca_id=finca_id).order_by(Animal.fecha_ingreso.desc()).limit(5).all()
    
    return render_template('index.html',
        valor_total_inventario=0.0,
        ingreso_mes_actual=0.0,
        crecimiento_ingresos=0.0,
        produccion_media_vaca=0.0,
        total_empleados=total_empleados,
        total_animales=total_animales,
        total_potreros=total_potreros,
        total_fincas=total_fincas,
        no_finca=no_finca,
        finca=finca,
        finca_labels=finca_labels,
        finca_data=finca_data,
        animales_recientes=animales_recientes,
        date=date
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas para Animales
@app.route('/animales')
@login_required
def animales():
    # Verificar si hay una finca seleccionada
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Primero debes seleccionar una finca', 'warning')
        return redirect(url_for('fincas'))
    
    # Obtener solo los animales de la finca seleccionada
    # Usar db.session.query para asegurar que se obtienen los datos actualizados
    db.session.commit()  # Asegurar que todas las transacciones pendientes se completen
    # Usar join para cargar explícitamente la relación con potrero
    animales = db.session.query(Animal).filter_by(finca_id=finca_id).options(db.joinedload(Animal.potrero)).all()
    potreros = Potrero.query.filter_by(finca_id=finca_id).all()
    from datetime import date
    today = date.today()
    return render_template('animales.html', animales=animales, potreros=potreros, today=today)

@app.route('/animal/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_animal():
    # Verificar si hay una finca seleccionada
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Primero debes seleccionar una finca', 'warning')
        return redirect(url_for('fincas'))
        
    if request.method == 'POST':
        # Crear el animal con los campos básicos
        animal = Animal(
            identificacion=request.form['identificacion'],
            tipo=request.form['tipo'],
            raza=request.form['raza'],
            fecha_nacimiento=datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date(),
            peso=float(request.form['peso_actual']),
            potrero_id=int(request.form['potrero_id']) if request.form['potrero_id'] else None,
            finca_id=finca_id  # Asociar con la finca seleccionada
        )
        
        # Procesar campos adicionales del formulario
        if 'nombre' in request.form:
            animal.nombre = request.form['nombre']
        if 'sexo' in request.form:
            animal.sexo = request.form['sexo']
        if 'peso_nacimiento' in request.form and request.form['peso_nacimiento']:
            animal.peso_nacimiento = float(request.form['peso_nacimiento'])
        if 'color_senas' in request.form:
            animal.color_señas = request.form['color_senas']
        if 'estado' in request.form:
            animal.estado = request.form['estado']
        if 'ubicacion_actual' in request.form:
            animal.ubicacion_actual = request.form['ubicacion_actual']
        
        # Información genética y parentesco
        if 'padre_id' in request.form:
            animal.padre_id = request.form['padre_id']
        if 'madre_id' in request.form:
            animal.madre_id = request.form['madre_id']
        
        # Observaciones adicionales
        if 'observaciones_adicionales' in request.form:
            animal.observaciones = request.form['observaciones_adicionales']
            
        # Procesar imagen si se proporciona
        if 'imagen' in request.files and request.files['imagen'].filename:
            imagen = request.files['imagen']
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                # Crear directorio si no existe
                ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], 'animales')
                if not os.path.exists(ruta_imagen):
                    os.makedirs(ruta_imagen)
                # Guardar imagen
                filepath = os.path.join(ruta_imagen, filename)
                imagen.save(filepath)
                animal.imagen = os.path.join('animales', filename)
        
        db.session.add(animal)
        db.session.commit()
        
        # Registrar el peso inicial en el historial
        peso_inicial = HistorialPeso(
            animal_id=animal.id,
            peso=float(request.form['peso_actual']),
            fecha=date.today(),
            tipo_medicion='inicial',
            observaciones='Peso registrado al crear el animal'
        )
        db.session.add(peso_inicial)
        db.session.commit()
        flash('Animal registrado exitosamente')
        return redirect(url_for('animales'))
    
    # Obtener solo los potreros de la finca seleccionada
    potreros = Potrero.query.filter_by(finca_id=finca_id).all()
    return render_template('nuevo_animal.html', potreros=potreros)

@app.route('/animal/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_animal(id):
    animal = Animal.query.get_or_404(id)
    # Verificar si hay una finca seleccionada
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Primero debes seleccionar una finca', 'warning')
        return redirect(url_for('fincas'))
    
    # Verificar que el animal pertenezca a la finca seleccionada
    if animal.finca_id != finca_id:
        flash('No tienes permiso para editar este animal', 'danger')
        return redirect(url_for('animales'))
        
    if request.method == 'POST':
        # Guardar los valores anteriores para depuración
        old_values = {
            'identificacion': animal.identificacion,
            'tipo': animal.tipo,
            'raza': animal.raza,
            'nombre': animal.nombre,
            'sexo': animal.sexo,
            'estado': animal.estado
        }
        
        # Actualizar campos básicos
        animal.identificacion = request.form['identificacion']
        animal.tipo = request.form['tipo']
        animal.raza = request.form['raza']
        animal.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date()
        animal.peso = float(request.form['peso'])
        animal.potrero_id = int(request.form['potrero_id']) if request.form['potrero_id'] else None
        
        # Actualizar campos adicionales directamente
        animal.nombre = request.form.get('nombre', '')
        # Asegurarse de que el campo sexo se procese correctamente
        if 'sexo' in request.form and request.form['sexo']:
            animal.sexo = request.form['sexo']
            print(f"Valor de sexo recibido: {request.form['sexo']}")
        animal.peso_nacimiento = float(request.form.get('peso_nacimiento', 0)) if request.form.get('peso_nacimiento') else None
        animal.color_señas = request.form.get('color_señas', '')
        animal.estado = request.form.get('estado', 'activo')
        animal.ubicacion_actual = request.form.get('ubicacion_actual', '')
            
        # Procesar imagen si se proporciona
        if 'imagen' in request.files and request.files['imagen'].filename:
            imagen = request.files['imagen']
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                # Crear directorio si no existe
                ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], 'animales')
                if not os.path.exists(ruta_imagen):
                    os.makedirs(ruta_imagen)
                # Guardar imagen
                filepath = os.path.join(ruta_imagen, filename)
                imagen.save(filepath)
                animal.imagen = os.path.join('animales', filename)
        
        # Mantener la finca_id
        animal.finca_id = finca_id
        
        # Guardar los cambios en la base de datos
        try:
            db.session.commit()
            flash('Animal actualizado exitosamente')
            
            # Depuración: Verificar si los cambios se aplicaron
            updated_animal = Animal.query.get(id)
            if updated_animal:
                new_values = {
                    'identificacion': updated_animal.identificacion,
                    'tipo': updated_animal.tipo,
                    'raza': updated_animal.raza,
                    'nombre': updated_animal.nombre,
                    'sexo': updated_animal.sexo,
                    'estado': updated_animal.estado
                }
                print(f"Valores anteriores: {old_values}")
                print(f"Nuevos valores: {new_values}")
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el animal: {str(e)}', 'danger')
            print(f"Error en la actualización: {str(e)}")
        
        return redirect(url_for('animales'))
    
    # Obtener solo los potreros de la finca seleccionada
    potreros = Potrero.query.filter_by(finca_id=finca_id).all()
    return render_template('editar_animal.html', animal=animal, potreros=potreros)

@app.route('/animal/<int:animal_id>/eliminar', methods=['POST'])
@login_required
def eliminar_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    db.session.delete(animal)
    db.session.commit()
    flash('Animal eliminado exitosamente')
    return redirect(url_for('animales'))

@app.route('/animal/<int:animal_id>/historial')
@login_required
def historial_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    
    # Obtener todos los datos relacionados con el animal para mostrar en las pestañas
    historial_peso = HistorialPeso.query.filter_by(animal_id=animal_id).order_by(HistorialPeso.fecha.desc()).all()
    vacunas = Vacuna.query.filter_by(animal_id=animal_id).order_by(Vacuna.fecha_aplicacion.desc()).all()
    producciones = Produccion.query.filter_by(animal_id=animal_id).order_by(Produccion.fecha.desc()).all()
    entregas_inventario = Inventario.query.filter_by(animal_id=animal_id).all()
    
    # Obtener datos de los nuevos modelos
    eventos_salud = EventoSalud.query.filter_by(animal_id=animal_id).order_by(EventoSalud.fecha_inicio.desc()).all()
    alimentaciones = Alimentacion.query.filter_by(animal_id=animal_id).order_by(Alimentacion.fecha.desc()).all()
    eventos_reproductivos = Reproductivo.query.filter_by(animal_id=animal_id).order_by(Reproductivo.fecha.desc()).all()
    eventos = Evento.query.filter_by(animal_id=animal_id).order_by(Evento.fecha.desc()).all()
    
    return render_template('historial_animal.html', 
                           animal=animal, 
                           historial_peso=historial_peso,
                           vacunas=vacunas,
                           producciones=producciones,
                           entregas_inventario=entregas_inventario,
                           eventos_salud=eventos_salud,
                           alimentaciones=alimentaciones,
                           eventos_reproductivos=eventos_reproductivos,
                           eventos=eventos)

@app.route('/animal/<int:animal_id>/peso/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_peso(animal_id):
    if 'finca_id' not in session:
        flash('Selecciona una finca para continuar')
        return redirect(url_for('fincas'))
    
    animal = Animal.query.get_or_404(animal_id)
    if animal.finca_id != session.get('finca_id'):
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('animales'))
    
    if request.method == 'POST':
        peso = HistorialPeso(
            animal_id=animal_id,
            peso=float(request.form['peso']),
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            tipo_medicion=request.form['tipo_medicion'],
            observaciones=request.form.get('observaciones')
        )
        db.session.add(peso)
        
        # Actualizar el peso actual del animal
        animal.peso = float(request.form['peso'])
        
        db.session.commit()
        flash('Peso registrado exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    # Pasar la fecha actual al template
    today = date.today().strftime('%Y-%m-%d')
    return render_template('nuevo_peso.html', animal=animal, today=today)

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
        # Procesar el formulario para crear un nuevo evento de salud
        evento_salud = EventoSalud(
            animal_id=animal_id,
            tipo_evento=request.form['tipo_evento'],
            descripcion=request.form['descripcion'],
            fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date(),
            tratamiento=request.form.get('tratamiento'),
            resultado=request.form.get('resultado'),
            observaciones=request.form.get('observaciones')
        )
        
        # Si hay fecha de finalización, agregarla
        if request.form.get('fecha_fin') and request.form.get('fecha_fin') != '':
            evento_salud.fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date()
        
        db.session.add(evento_salud)
        db.session.commit()
        
        flash('Evento de salud registrado exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    # Pasar la fecha actual al template
    today = date.today().strftime('%Y-%m-%d')
    return render_template('nuevo_evento_salud.html', animal=animal, today=today)

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
        # Procesar el formulario para crear un nuevo registro de alimentación
        alimentacion = Alimentacion(
            animal_id=animal_id,
            tipo_alimento=request.form['tipo_alimento'],
            marca=request.form.get('marca'),
            cantidad=float(request.form['cantidad']),
            unidad=request.form['unidad'],
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            observaciones=request.form.get('observaciones')
        )
        
        db.session.add(alimentacion)
        db.session.commit()
        
        flash('Registro de alimentación creado exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    # Pasar la fecha actual al template
    today = date.today().strftime('%Y-%m-%d')
    return render_template('nueva_alimentacion.html', animal=animal, today=today)

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
        # Procesar el formulario para actualizar información reproductiva
        evento_reproductivo = Reproductivo(
            animal_id=animal_id,
            tipo_evento=request.form['tipo_evento'],
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            detalles=request.form.get('detalles'),
            resultado=request.form.get('resultado'),
            observaciones=request.form.get('observaciones')
        )
        
        db.session.add(evento_reproductivo)
        db.session.commit()
        
        flash('Información reproductiva actualizada exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    # Pasar la fecha actual al template
    today = date.today().strftime('%Y-%m-%d')
    return render_template('actualizar_reproductivo.html', animal=animal, today=today)

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
        # Procesar el formulario para registrar un nuevo evento
        evento = Evento(
            animal_id=animal_id,
            tipo_evento=request.form['tipo_evento'],
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            descripcion=request.form['descripcion'],
            observaciones=request.form.get('observaciones')
        )
        
        # Agregar valor si está presente
        if request.form.get('valor') and request.form.get('valor') != '':
            evento.valor = float(request.form['valor'])
            
        # Agregar destino si está presente
        if request.form.get('destino'):
            evento.destino = request.form['destino']
        
        db.session.add(evento)
        db.session.commit()
        
        flash('Evento registrado exitosamente', 'success')
        return redirect(url_for('historial_animal', animal_id=animal_id))
    
    # Pasar la fecha actual al template
    today = date.today().strftime('%Y-%m-%d')
    return render_template('registrar_evento.html', animal=animal, today=today)

# Rutas para Potreros
@app.route('/potreros')
@login_required
def potreros():
    # Verificar si hay una finca seleccionada
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Primero debes seleccionar una finca', 'warning')
        return redirect(url_for('fincas'))
    
    # Obtener solo los potreros de la finca seleccionada
    potreros = Potrero.query.filter_by(finca_id=finca_id).all()
    
    # Obtener todos los animales de la finca
    animales = Animal.query.filter_by(finca_id=finca_id).all()
    
    # Crear un diccionario con el conteo de animales por potrero
    animales_por_potrero = {}
    for animal in animales:
        if animal.potrero_id:
            if animal.potrero_id in animales_por_potrero:
                animales_por_potrero[animal.potrero_id] += 1
            else:
                animales_por_potrero[animal.potrero_id] = 1
    
    return render_template('potreros.html', potreros=potreros, animales=animales, animales_por_potrero=animales_por_potrero)

@app.route('/potrero/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_potrero():
    # Verificar si hay una finca seleccionada
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Primero debes seleccionar una finca', 'warning')
        return redirect(url_for('fincas'))
        
    if request.method == 'POST':
        potrero = Potrero(
            nombre=request.form['nombre'],
            area=float(request.form['area']),
            capacidad=int(request.form['capacidad']),
            funcion=request.form['funcion'],
            finca_id=finca_id  # Asociar con la finca seleccionada
        )
        db.session.add(potrero)
        db.session.commit()
        flash('Potrero registrado exitosamente')
        return redirect(url_for('potreros'))
    
    return render_template('nuevo_potrero.html')

@app.route('/potrero/editar/<int:potrero_id>', methods=['GET', 'POST'])
@login_required
def editar_potrero(potrero_id):
    # Verificar si hay una finca seleccionada
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Primero debes seleccionar una finca', 'warning')
        return redirect(url_for('fincas'))
        
    potrero = Potrero.query.get_or_404(potrero_id)
    
    # Verificar que el potrero pertenezca a la finca seleccionada
    if potrero.finca_id != finca_id:
        flash('No tienes permiso para editar este potrero', 'danger')
        return redirect(url_for('potreros'))
    
    if request.method == 'POST':
        # Verificar el tipo de formulario
        form_type = request.form.get('form_type', 'info_potrero')
        
        if form_type == 'info_potrero':
            potrero.nombre = request.form['nombre']
            potrero.area = float(request.form['area'])
            potrero.capacidad = int(request.form['capacidad'])
            potrero.estado = request.form['estado']
            potrero.funcion = request.form['funcion']
            # Mantener la finca_id
            potrero.finca_id = finca_id
            db.session.commit()
            flash('Potrero actualizado exitosamente')
            return redirect(url_for('potreros'))
        
        elif form_type == 'agregar_animal':
            animal_id = request.form.get('animal_id')
            if animal_id:
                animal = Animal.query.get(animal_id)
                # Verificar que el animal pertenezca a la finca seleccionada
                if animal and animal.finca_id == finca_id:
                    # Obtener animales actuales en el potrero para verificar capacidad
                    animales_actuales = Animal.query.filter_by(potrero_id=potrero_id).all()
                    # Verificar capacidad del potrero
                    if len(animales_actuales) < potrero.capacidad:
                        animal.potrero_id = potrero_id
                        db.session.commit()
                        flash('Animal agregado al potrero exitosamente')
                    else:
                        flash('El potrero ha alcanzado su capacidad máxima', 'warning')
                else:
                    flash('No tienes permiso para agregar este animal', 'danger')
            return redirect(url_for('editar_potrero', potrero_id=potrero_id))
        
        elif form_type == 'quitar_animal':
            animal_id = request.form.get('animal_id')
            if animal_id:
                animal = Animal.query.get(animal_id)
                # Verificar que el animal pertenezca a la finca seleccionada
                if animal and animal.finca_id == finca_id and animal.potrero_id == potrero_id:
                    animal.potrero_id = None
                    db.session.commit()
                    flash('Animal removido del potrero exitosamente')
                else:
                    flash('No tienes permiso para quitar este animal', 'danger')
            return redirect(url_for('editar_potrero', potrero_id=potrero_id))
    
    return render_template('editar_potrero.html', potrero=potrero)

# Rutas para Vacunas
@app.route('/vacunas')
@login_required
def vacunas():
    vacunas = Vacuna.query.join(Animal).all()
    return render_template('vacunas.html', vacunas=vacunas)

@app.route('/vacuna/nueva', methods=['GET', 'POST'])
@login_required
def nueva_vacuna():
    if request.method == 'POST':
        vacuna = Vacuna(
            animal_id=int(request.form['animal_id']),
            tipo_vacuna=request.form['tipo_vacuna'],
            fecha_aplicacion=datetime.strptime(request.form['fecha_aplicacion'], '%Y-%m-%d').date(),
            fecha_proxima=datetime.strptime(request.form['fecha_proxima'], '%Y-%m-%d').date(),
            observaciones=request.form['observaciones'],
            aplicada_por=request.form['aplicada_por']
        )
        db.session.add(vacuna)
        db.session.commit()
        flash('Vacuna registrada exitosamente')
        return redirect(url_for('vacunas'))
    
    animales = Animal.query.all()
    return render_template('nueva_vacuna.html', animales=animales)

# Rutas para Empleados
@app.route('/empleados')
@login_required
def empleados():
    empleados = Empleado.query.all()
    return render_template('empleados.html', empleados=empleados)

@app.route('/empleado/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_empleado():
    if request.method == 'POST':
        empleado = Empleado(
            cedula=request.form['cedula'],
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            telefono=request.form['telefono'],
            direccion=request.form['direccion'],
            cargo=request.form['cargo'],
            fecha_contratacion=datetime.strptime(request.form['fecha_contratacion'], '%Y-%m-%d').date(),
            salario=float(request.form['salario'])
        )
        db.session.add(empleado)
        db.session.commit()
        flash('Empleado registrado exitosamente')
        return redirect(url_for('empleados'))
    
    return render_template('nuevo_empleado.html')

# Rutas para Producción
@app.route('/produccion')
@login_required
def produccion():
    producciones = Produccion.query.join(Animal).all()
    return render_template('produccion.html', producciones=producciones)

@app.route('/produccion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_produccion():
    if request.method == 'POST':
        produccion = Produccion(
            animal_id=int(request.form['animal_id']),
            tipo_produccion=request.form['tipo_produccion'],
            cantidad=float(request.form['cantidad']),
            unidad=request.form['unidad'],
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            calidad=request.form['calidad']
        )
        db.session.add(produccion)
        db.session.commit()
        flash('Producción registrada exitosamente')
        return redirect(url_for('produccion'))
    
    animales = Animal.query.all()
    return render_template('nueva_produccion.html', animales=animales)

# Rutas para Inventario
@app.route('/inventario')
@login_required
def inventario():
    inventarios = Inventario.query.all()
    return render_template('inventario.html', inventarios=inventarios)

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_inventario():
    if request.method == 'POST':
        inventario = Inventario(
            producto=request.form['producto'],
            cantidad=float(request.form['cantidad']),
            unidad=request.form['unidad'],
            precio_unitario=float(request.form['precio_unitario']),
            fecha_vencimiento=datetime.strptime(request.form['fecha_vencimiento'], '%Y-%m-%d').date() if request.form['fecha_vencimiento'] else None,
            categoria=request.form['categoria']
        )
        db.session.add(inventario)
        db.session.commit()
        flash('Producto agregado al inventario exitosamente')
        return redirect(url_for('inventario'))
    
    return render_template('nuevo_inventario.html')

# Rutas para Fincas
@app.route('/fincas', methods=['GET', 'POST'])
@login_required
def fincas():
    user_id = current_user.id if hasattr(current_user, 'id') else None
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
    fincas = Finca.query.filter_by(usuario_id=user_id).all() if user_id else []
    return render_template('fincas.html', fincas=fincas)

@app.route('/finca/seleccionar/<int:finca_id>')
@login_required
def seleccionar_finca(finca_id):
    # Aquí puedes guardar la finca seleccionada en la sesión o hacer lógica adicional
    session['finca_id'] = finca_id
    flash('Finca seleccionada correctamente')
    return redirect(url_for('index'))

# Rutas para Reportes
@app.route('/reportes')
@login_required
def reportes():
    # Puedes personalizar la lógica de reportes aquí
    return render_template('reportes.html')

# API para estadísticas
@app.route('/api/estadisticas')
@login_required
def estadisticas():
    total_animales = Animal.query.count()
    total_vacas = Animal.query.filter_by(tipo='vaca').count()
    total_cochinos = Animal.query.filter_by(tipo='cochino').count()
    total_potreros = Potrero.query.count()
    total_empleados = Empleado.query.filter_by(estado='activo').count()
    
    return jsonify({
        'total_animales': total_animales,
        'total_vacas': total_vacas,
        'total_cochinos': total_cochinos,
        'total_potreros': total_potreros,
        'total_empleados': total_empleados
    })

@app.context_processor
def inject_finca_model():
    return dict(Finca=Finca)

# Rutas para Clientes (solo accesibles por admin)
@app.route('/clientes')
@login_required
def clientes():
    # Verificar que el usuario sea admin
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('index'))
    
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero', 'error')
        return redirect(url_for('fincas'))
    
    clientes = Cliente.query.filter_by(finca_id=finca_id).all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    # Verificar que el usuario sea admin
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('index'))
    
    finca_id = session.get('finca_id')
    if not finca_id:
        flash('Debes seleccionar una finca primero', 'error')
        return redirect(url_for('fincas'))
    
    if request.method == 'POST':
        # Generar username y password automáticamente
        nombre = request.form['nombre'].lower().replace(' ', '')
        apellido = request.form['apellido'].lower().replace(' ', '')
        username = f"{nombre}{apellido}{datetime.now().strftime('%y%m')}"
        password = f"{nombre.capitalize()}{datetime.now().strftime('%m%y')}!"
        
        # Verificar que el username sea único
        while Cliente.query.filter_by(username=username).first():
            username = f"{nombre}{apellido}{datetime.now().strftime('%y%m%d%H%M')}"
        
        cliente = Cliente(
            username=username,
            password_hash=generate_password_hash(password),
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            telefono=request.form['telefono'],
            email=request.form['email'],
            direccion=request.form.get('direccion', ''),
            finca_id=finca_id
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        flash(f'Cliente registrado exitosamente. Usuario: {username}, Contraseña: {password}', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('nuevo_cliente.html')

@app.route('/clientes/editar/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(cliente_id):
    # Verificar que el usuario sea admin
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('index'))
    
    cliente = Cliente.query.get_or_404(cliente_id)
    finca_id = session.get('finca_id')
    
    # Verificar que el cliente pertenezca a la finca seleccionada
    if cliente.finca_id != finca_id:
        flash('No tienes permisos para editar este cliente', 'error')
        return redirect(url_for('clientes'))
    
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.apellido = request.form['apellido']
        cliente.telefono = request.form['telefono']
        cliente.email = request.form['email']
        cliente.direccion = request.form.get('direccion', '')
        cliente.estado = request.form['estado']
        
        # Si se proporciona una nueva contraseña, actualizarla
        nueva_password = request.form.get('nueva_password')
        if nueva_password:
            cliente.password_hash = generate_password_hash(nueva_password)
            flash('Cliente actualizado exitosamente. Nueva contraseña asignada.', 'success')
        else:
            flash('Cliente actualizado exitosamente', 'success')
        
        db.session.commit()
        return redirect(url_for('clientes'))
    
    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:cliente_id>', methods=['POST'])
@login_required
def eliminar_cliente(cliente_id):
    # Verificar que el usuario sea admin
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('index'))
    
    cliente = Cliente.query.get_or_404(cliente_id)
    finca_id = session.get('finca_id')
    
    # Verificar que el cliente pertenezca a la finca seleccionada
    if cliente.finca_id != finca_id:
        flash('No tienes permisos para eliminar este cliente', 'error')
        return redirect(url_for('clientes'))
    
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado exitosamente', 'success')
    return redirect(url_for('clientes'))

# Ruta para login de clientes
@app.route('/cliente/login', methods=['GET', 'POST'])
def cliente_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cliente = Cliente.query.filter_by(username=username).first()
        if cliente and check_password_hash(cliente.password_hash, password):
            if cliente.estado == 'activo':
                # Crear sesión para cliente
                session['cliente_id'] = cliente.id
                session['cliente_nombre'] = f"{cliente.nombre} {cliente.apellido}"
                session['tipo_usuario'] = 'cliente'
                flash(f'Bienvenido {cliente.nombre}', 'success')
                return redirect(url_for('cliente_dashboard'))
            else:
                flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('cliente_login.html')

@app.route('/cliente/dashboard')
def cliente_dashboard():
    if 'cliente_id' not in session:
        flash('Debes iniciar sesión como cliente', 'error')
        return redirect(url_for('cliente_login'))
    
    cliente = Cliente.query.get(session['cliente_id'])
    if not cliente or cliente.estado != 'activo':
        flash('Sesión inválida', 'error')
        return redirect(url_for('cliente_login'))
    
    # Aquí puedes agregar la información que quieres mostrar al cliente
    return render_template('cliente_dashboard.html', cliente=cliente)

@app.route('/cliente/logout')
def cliente_logout():
    session.pop('cliente_id', None)
    session.pop('cliente_nombre', None)
    session.pop('tipo_usuario', None)
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('cliente_login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crear usuario admin por defecto si no existe
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                email='admin@finca.com',
                password_hash=generate_password_hash('admin123'),
                nombre='Administrador',
                rol='admin'
            )
            db.session.add(admin)
            db.session.commit()
    
    # Importante: enlazar en 0.0.0.0 para que sea accesible desde la red local (teléfono)
    app.run(host="0.0.0.0", port=5000, debug=True)