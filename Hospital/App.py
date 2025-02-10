from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename
import os
from flask_mysqldb import MySQL
from datetime import datetime
from flask import jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file, make_response
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import openai
import mysql.connector

UPLOAD_FOLDER_IMAGES = 'static/imagenes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'hospital2'
mysql = MySQL(app)

app.config['UPLOAD_FOLDER_PDF'] = 'static/PDF'

app.secret_key = 'mysecretkey'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función para registrar la sesión del usuario
def registrar_sesion(user_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO sesion (ID_Logeado) VALUES (%s)", (user_id,))
    mysql.connection.commit()
    cur.close()

# Rutas permitidas sin comprobación de tipo
allowed_routes = ['index', 'login', 'dashboard', 'logout', 'static', 'register']

def verificar_permisos():
    if not session.get('user_id'):
        # No está autenticado
        abort(401)
    elif session['user_type'] == 1:
        # Si es un usuario de tipo 1, bloquear ciertas rutas
        blocked_routes = ['mis_citas', 'agregar_cita', 'eliminar_cita', 'doctores_por_fecha', 'horarios_por_doctor_y_fecha',
                          'mostrar_recetas_usuario',
                          'mis_horarios','agregar_horario','actualizar_estado','eliminar_horario',
                          'mis_citas_doctor','actualizar_cita','insertar_detalle_tratamiento','insertar_receta','procesar_pago',
                          'mostrar_pacientes','mostrar_tratamientos_paciente','mostrar_recetas_paciente']
        if request.endpoint in blocked_routes:
            abort(403)
    elif session['user_type'] == 2:
        # Si es un usuario de tipo 2, bloquear ciertas rutas
        blocked_routes = ['mis_citas', 'agregar_cita', 'eliminar_cita', 'doctores_por_fecha', 'horarios_por_doctor_y_fecha',
                          'mostrar_recetas_usuario',
                          'pagos',
                          'pacientes_registros','mostrar_tratamientos_paciente_registro','mostrar_recetas_paciente_registro',
                          'doctores','agregar_doctor','editar_doctor','actualizar_doctor','inactivar_doctor','activar_doctor',
                          'tratamientos','agregar_tratamiento','editar_tratamiento','actualizar_tratamiento','inactivar_tratamiento','activar_tratamiento',
                          'inteligencia_artificial']
        if request.endpoint in blocked_routes:
            abort(403)
    elif session['user_type'] == 3:
        # Si es un usuario de tipo 3, bloquear ciertas rutas
        blocked_routes = ['ver_medicamentos', 'agregar_medicamento', 'editar_medicamento', 'actualizar_medicamento', 'inactivar_medicamento','activar_medicamento',
                          'pagos',
                          'pacientes_registros','mostrar_tratamientos_paciente_registro','mostrar_recetas_paciente_registro',
                          'doctores','agregar_doctor','editar_doctor','actualizar_doctor','inactivar_doctor','activar_doctor',
                          'tratamientos','agregar_tratamiento','editar_tratamiento','actualizar_tratamiento','inactivar_tratamiento','activar_tratamiento',
                          'mis_horarios','agregar_horario','actualizar_estado','eliminar_horario',
                          'mis_citas_doctor','actualizar_cita','insertar_detalle_tratamiento','insertar_receta','procesar_pago',
                          'mostrar_pacientes','mostrar_tratamientos_paciente','mostrar_recetas_paciente',
                          'inteligencia_artificial']
        if request.endpoint in blocked_routes:
            abort(403)

@app.before_request
def before_request():
    if request.endpoint and request.endpoint not in allowed_routes:
        verificar_permisos()

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('error.html', error_code=401, error_message='No estás autenticado. Inicia sesión para acceder.'), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_code=403, error_message='Acceso prohibido. No tienes permisos para esta página.'), 403

# Rutas para Login

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('log.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT usuario.ID_Usuario, persona.Nom_persona, usuario.ID_Tipo
            FROM usuario
            INNER JOIN Persona ON usuario.ID_Persona = persona.IDPersona
            WHERE Email = %s AND Contraseña = %s
        """, (email, password))
        user = cur.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_type'] = user[2]
            
            # Insertar registro en la tabla sesion
            user_id = session['user_id']
            cur.execute("""INSERT INTO sesion (ID_Logeado) VALUES (%s)""", (user_id,))
            mysql.connection.commit()
            
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas. Intenta de nuevo.', 'danger')

    return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        Nom_Persona = request.form['Nom_Persona']
        ApellidoP = request.form['ApellidoP']
        ApellidoM = request.form['ApellidoM']
        Email = request.form['Email']
        Contraseña = request.form['Contraseña']
        Fecha_Nacimiento = request.form['Fecha_Nacimiento']
        
        # Insertar en la tabla persona para el registro
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO persona (Nom_Persona, ApellidoP, ApellidoM, Email, Fecha_Nacimiento, Estado) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (Nom_Persona, ApellidoP, ApellidoM, Email, Fecha_Nacimiento, 1))
        mysql.connection.commit()

        # Obtener el ID de la último registro de persona
        cur.execute("SELECT LAST_INSERT_ID()")
        id_persona = cur.fetchone()[0]

        # Insertar en la tabla usuario la ultima persona
        cur.execute("""
            INSERT INTO usuario (ID_Persona, Contraseña, ID_Tipo) 
            VALUES (%s, %s, %s)
        """, (id_persona, Contraseña, 3))
        mysql.connection.commit()

        flash('Registro exitoso', 'success')
    return redirect(url_for('index'))
 
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return redirect(url_for('principal'))
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM sesion")
    mysql.connection.commit()
    cur.close()
    flash('Sesion cerrada', 'success')
    return redirect(url_for('index'))

# Ruta con relación a la pagina principal

@app.route('/Principal')
def principal():
    return render_template('dashboard.html')

# Rutas con relación a citas (Del paciente)

@app.route('/mis_citas')
def mis_citas():
    if 'user_id' in session:
        user_id = session['user_id']

        # Consulta SQL para obtener las citas del usuario logueado
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                c.ID_Cita, 
                CONCAT(p.Nom_persona, ' ', p.ApellidoP, ' ', p.ApellidoM) AS Nombre_Completo_Doctor, 
                c.Fecha,
                CONCAT(hd.hora_inicio, ' - ', hd.hora_fin) AS Horario
            FROM 
                citas c
            INNER JOIN 
                doctores d ON c.ID_Doctor = d.ID_Doctor
            INNER JOIN 
                persona p ON d.ID_Persona = p.IDPersona
            INNER JOIN 
                pacientes pa ON c.ID_Paciente = pa.ID_Paciente
            INNER JOIN 
                usuario u ON pa.ID_Persona = u.ID_Persona
            INNER JOIN 
                horariosdisponibles hd ON c.Hora = hd.horario_id AND c.Fecha = hd.fecha
            WHERE 
                u.ID_Usuario = %s 
                AND c.Estado = 3
        """, (user_id,))


        citas = cur.fetchall()
        cur.close()

        return render_template('mis_citas.html', citas=citas)
    else:
        return redirect(url_for('index'))

@app.route('/agregar_cita', methods=['GET', 'POST'])
def agregar_cita():
    if 'user_id' in session:
        cur = mysql.connection.cursor()

        if request.method == 'POST':
            fecha = request.form.get('fecha')
            id_doctor = request.form.get('doctor')
            horario_id = request.form.get('horario')

            if not fecha or not id_doctor or not horario_id:
                flash('Por favor completa todos los campos.', 'error')
                return redirect(url_for('agregar_cita'))

            # Obtener el usuario en sesión para vincularlo con el paciente
            user_id = session['user_id']

            # Obtener la fecha y hora del horario seleccionado de `horariosdisponibles`
            cur.execute("SELECT fecha, hora_inicio FROM horariosdisponibles WHERE horario_id = %s", (horario_id,))
            horario_seleccionado = cur.fetchone()

            if not horario_seleccionado:
                flash('Horario no válido, por favor intenta nuevamente.', 'error')
                return redirect(url_for('agregar_cita'))

            fecha_cita = horario_seleccionado[0]
            hora_cita = horario_seleccionado[1]

            # Verificar si ya existe una cita a la misma hora y fecha para el usuario
            cur.execute("""
                SELECT COUNT(*) FROM citas
                WHERE ID_Paciente IN (
                    SELECT ID_Paciente FROM pacientes WHERE usuario_id = %s
                ) AND Fecha = %s AND Hora IN (
                    SELECT horario_id FROM horariosdisponibles WHERE fecha = %s AND hora_inicio = %s
                )
            """, (user_id, fecha_cita, fecha_cita, hora_cita))
            cita_existente = cur.fetchone()[0]

            if cita_existente > 0:
                flash('Ya tienes una cita agendada en esa fecha y hora.', 'error')
                return redirect(url_for('agregar_cita'))

            # Continuar con la lógica de agregar una nueva cita
            cur.execute("""
                SELECT p.ID_Paciente
                FROM pacientes p
                INNER JOIN usuario u ON p.usuario_id = u.ID_Usuario
                WHERE u.ID_Usuario = %s AND p.ID_Doctor_Asignado = %s
            """, (user_id, id_doctor))
            paciente = cur.fetchone()

            # Si el paciente no existe, crear un nuevo registro en la tabla pacientes
            if paciente is None:
                fecha_registro = datetime.now().strftime('%Y-%m-%d')
                cur.execute("SELECT ID_Persona FROM usuario WHERE ID_Usuario = %s", (user_id,))
                id_persona = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO pacientes (ID_Persona, Fecha_Registro, ID_Doctor_Asignado, usuario_id)
                    VALUES (%s, %s, %s, %s)
                """, (id_persona, fecha_registro, id_doctor, user_id))
                mysql.connection.commit()

                cur.execute("SELECT LAST_INSERT_ID()")
                id_paciente = cur.fetchone()[0]
            else:
                id_paciente = paciente[0]

            # Inserción en la tabla citas
            cur.execute("""
                INSERT INTO citas (ID_Paciente, ID_Doctor, Fecha, Hora, Estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_paciente, id_doctor, fecha_cita, horario_id, 3))

            cur.execute("""
                UPDATE horariosdisponibles
                SET estado_id = 5
                WHERE horario_id = %s
            """, (horario_id,))

            mysql.connection.commit()
            cur.close()
            return redirect('/mis_citas')

        else:
            # Lógica GET: proporcionar datos iniciales si es necesario
            cur.execute("""
                SELECT DISTINCT doctores.ID_Doctor, 
                       CONCAT(persona.Nom_persona, ' ', persona.ApellidoP, ' ', persona.ApellidoM) AS nombre_completo
                FROM horariosdisponibles
                JOIN doctores ON doctores.ID_Doctor = horariosdisponibles.doctor_id
                JOIN persona ON persona.IDPersona = doctores.ID_Persona
                WHERE horariosdisponibles.estado_id = 1
            """)
            doctores = cur.fetchall()
            cur.close()
            return render_template('agregar_cita.html', doctores=doctores)
    else:
        return redirect(url_for('index'))
    
@app.route('/eliminar_cita/<string:cita_id>', methods=['POST', 'GET'])
def eliminar_cita(cita_id):
    cur = mysql.connection.cursor()

    cur.execute("SELECT Hora FROM citas WHERE ID_Cita = %s", (cita_id,))
    horario_id = cur.fetchone()[0]

    cur.execute("DELETE FROM citas WHERE ID_Cita = %s", (cita_id,))

    cur.execute("""
        UPDATE horariosdisponibles
        SET estado_id = 1
        WHERE horario_id = %s
    """, (horario_id,))

    mysql.connection.commit()
    cur.close()

    return redirect('/mis_citas')

@app.route('/doctores_por_fecha')
def doctores_por_fecha():
    fecha = request.args.get('fecha')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT doctores.ID_Doctor, 
               CONCAT(persona.Nom_persona, ' ', persona.ApellidoP, ' ', persona.ApellidoM) AS nombre_completo
        FROM horariosdisponibles
        JOIN doctores ON doctores.ID_Doctor = horariosdisponibles.doctor_id
        JOIN persona ON persona.IDPersona = doctores.ID_Persona
        WHERE horariosdisponibles.fecha = %s AND horariosdisponibles.estado_id = 1
    """, (fecha,))
    doctores = [{'doctor_id': row[0], 'nombre_completo': row[1]} for row in cur.fetchall()]
    cur.close()
    return jsonify(doctores=doctores)

@app.route('/horarios_por_doctor_y_fecha')
def horarios_por_doctor_y_fecha():
    fecha = request.args.get('fecha')
    doctor_id = request.args.get('doctor_id')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT horario_id, hora_inicio, hora_fin FROM horariosdisponibles
        WHERE fecha = %s AND doctor_id = %s AND estado_id = 1
    """, (fecha, doctor_id))
    horarios = [{'horario_id': row[0], 'hora_inicio': str(row[1]), 'hora_fin': str(row[2])} for row in cur.fetchall()]
    cur.close()
    return jsonify(horarios=horarios)

# Rutas con relacion a recetas (Del paciente)

@app.route('/mis_recetas')
def mostrar_recetas_usuario():
    if 'user_id' in session:
        user_id = session['user_id']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.ID_Paciente
            FROM pacientes p
            INNER JOIN persona pr ON p.ID_Persona = pr.IDPersona
            INNER JOIN usuario u ON pr.IDPersona = u.ID_Persona
            WHERE u.ID_Usuario = %s
        """, (user_id,))
        paciente = cur.fetchone()
        cur.close()

        if paciente:
            id_paciente = paciente[0]

            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    CONCAT(m.Nombre_Medicamento, ' - $', m.Precio) AS Nombre_Precio_Medicamento,
                    m.Descripcion,
                    r.Fecha_Receta,
                    r.Dosis,
                    r.Duracion
                FROM 
                    recetas r
                INNER JOIN 
                    medicamentos m ON r.ID_Medicamento = m.ID_Medicamento
                WHERE 
                    r.ID_Paciente = %s
                    AND r.Estado = 4
            """, (id_paciente,))
            
            recetas = cur.fetchall()
            cur.close()

            return render_template('mis_recetas.html', recetas=recetas)

        else:
            return "No hay un paciente asociado al usuario logueado."
    else:
        return redirect('/login')

# Rutas con relacion a horarios (Del doctor)

@app.route('/mis_horarios')
def mis_horarios():
    if 'user_id' in session:
        user_id = session['user_id']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                hd.horario_id,
                hd.Fecha, 
                hd.hora_inicio, 
                hd.hora_fin, 
                e.Estado
            FROM 
                horariosdisponibles hd
            INNER JOIN 
                doctores d ON hd.doctor_id = d.ID_Doctor
            INNER JOIN 
                persona p ON d.ID_Persona = p.IDPersona
            INNER JOIN 
                usuario u ON p.IDPersona = u.ID_Persona
            INNER JOIN 
                estado e ON hd.estado_id = e.ID_Estado
            WHERE 
                u.ID_Usuario = %s
                AND hd.estado_id !=4
        """, (user_id,))
        
        horarios = cur.fetchall()
        cur.close()

        return render_template('mis_horarios.html', horarios=horarios)
    else:
        flash('Debes iniciar sesión para ver tus horarios', 'danger')
        return redirect(url_for('index'))

@app.route('/agregar_horario', methods=['GET', 'POST'])
def agregar_horario():
    if 'user_id' in session:
        if request.method == 'POST':
            fecha = request.form['fecha']
            horario = request.form['horario']
            hora_inicio, hora_fin = horario.split('-')

            user_id = session['user_id']

            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT doctores.ID_Doctor 
                FROM doctores
                JOIN persona ON doctores.ID_Persona = persona.IDPersona
                JOIN usuario ON persona.IDPersona = usuario.ID_Persona
                WHERE usuario.ID_Usuario = %s;
            """, (user_id,))
            
            doctor_id = cur.fetchone()
            
            if doctor_id:
                doctor_id = doctor_id[0]
            else:
                return "Error: Doctor no encontrado", 400
            
            # Insertar nuevo horario en la tabla con estado_id = 1
            estado_id = 1
            cur.execute("""
                INSERT INTO horariosdisponibles (doctor_id, fecha, hora_inicio, hora_fin, estado_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (doctor_id, fecha, hora_inicio, hora_fin, estado_id))
            
            mysql.connection.commit()
            cur.close()
            
            return redirect(url_for('mis_horarios'))
        
        return render_template('agregar_horario.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/actualizar_estado/<string:cita_id>', methods=['POST', 'GET'])
def actualizar_estado(cita_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE horariosdisponibles SET estado_id = 1 WHERE horario_id = %s", (cita_id,))
    cur.execute("DELETE FROM citas WHERE Hora = %s", (cita_id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/mis_horarios')

@app.route('/eliminar_horario/<string:cita_id>', methods=['POST', 'GET'])
def eliminar_horario(cita_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM horariosdisponibles WHERE horario_id = %s", (cita_id,))
    cur.execute("DELETE FROM citas WHERE ID_Cita = %s", (cita_id,))
    mysql.connection.commit()
    cur.close()
    flash('Registro eliminado exitosamente', 'success')
    return redirect('/mis_horarios')

# Rutas con relacion a citas (Del doctor)

@app.route('/mis_citas_doctor', methods=['GET', 'POST'])
def mis_citas_doctor():
    if 'user_id' in session:
        user_id = session['user_id']

        # Conectar al cursor para realizar consultas
        cur = mysql.connection.cursor()
        
        # Consulta para obtener citas con estado 3 o 5
        cur.execute("""
            SELECT 
                c.ID_Cita, 
                CONCAT(pers.Nom_persona, ' ', pers.ApellidoP, ' ', pers.ApellidoM) AS Nombre_Paciente,
                c.Fecha, 
                hd.hora_inicio AS Hora,
                c.Estado
            FROM 
                citas c
            INNER JOIN 
                pacientes pac ON c.ID_Paciente = pac.ID_Paciente
            INNER JOIN 
                persona pers ON pac.ID_Persona = pers.IDPersona
            INNER JOIN 
                doctores d ON c.ID_Doctor = d.ID_Doctor
            INNER JOIN 
                usuario u ON d.ID_Persona = u.ID_Persona
            INNER JOIN 
                horariosdisponibles hd ON c.Fecha = hd.fecha AND c.Hora = hd.horario_id
            WHERE
                u.ID_Usuario = %s
                AND (c.Estado = 3 OR c.Estado = 5)
            ORDER BY 
                c.Fecha ASC, 
                hd.hora_inicio ASC
        """, (user_id,))

        citas = cur.fetchall()
        cur.close()

        # Verificar si alguna cita tiene el estado 5
        cita_estado_5 = any(cita[4] == 5 for cita in citas)

        if cita_estado_5:
            # Consultar los tratamientos disponibles
            cur = mysql.connection.cursor()
            cur.execute("SELECT ID_Tratamiento, Nombre_Tratamiento FROM tratamientos WHERE Estado = 1")
            tratamientos = cur.fetchall()
            cur.close()

            # Si se detecta el estado 5, redirigimos a detalle_tratamiento.html con la lista de tratamientos
            return render_template('detalle_tratamiento.html', tratamientos=tratamientos, citas=citas)

        # Mostrar las citas usuales si no hay estado 5
        return render_template('mis_citas_doctor.html', citas=citas)
    else:
        return redirect(url_for('index'))

@app.route('/actualizar_cita/<string:Id_cita>', methods=['POST', 'GET'])
def actualizar_cita(Id_cita):
    cur = mysql.connection.cursor()

    # Actualizar el estado de la cita
    cur.execute("UPDATE citas SET Estado = 5 WHERE ID_Cita = %s", (Id_cita,))

    # Actualizar el estado del horario disponible relacionado con la cita
    cur.execute("""
        UPDATE horariosdisponibles
        SET estado_id = 5
        WHERE Horario_ID = (
            SELECT Hora
            FROM citas
            WHERE ID_Cita = %s
        )
    """, (Id_cita,))

    mysql.connection.commit()
    cur.close()

    return redirect('/mis_citas_doctor')

@app.route('/insertar_detalle_tratamiento', methods=['POST'])
def insertar_detalle_tratamiento():
    if 'user_id' in session:
        user_id = session['user_id']

        # Consulta SQL para verificar si hay una cita con Estado 5 del doctor logueado
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                c.ID_Paciente
            FROM 
                citas c
            INNER JOIN 
                doctores d ON c.ID_Doctor = d.ID_Doctor
            INNER JOIN 
                usuario u ON d.ID_Persona = u.ID_Persona
            WHERE 
                u.ID_Usuario = %s AND c.Estado = 5
            LIMIT 1
        """, (user_id,))

        result = cur.fetchone()

        if result:
            # Extraer el ID del paciente
            id_paciente = result[0]

            # Obtener los datos del formulario
            id_tratamiento = request.form['ID_Tratamiento']
            notas = request.form['Notas']
            fecha_tratamiento = datetime.now().strftime('%Y-%m-%d')

            # Insertar en la tabla detalle_tratamiento
            cur.execute("""
                INSERT INTO detalle_tratamiento (ID_Tratamiento, ID_Paciente, Fecha_Tratamiento, Notas, Estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_tratamiento, id_paciente, fecha_tratamiento, notas, 5))
            mysql.connection.commit()
            cur.close()

            return redirect('/insertar_receta')
        else:
            cur.close()
            # Si no hay citas con Estado 5 para el doctor logeado
            flash('No se encontraron citas con Estado 5.')
            return redirect('/mis_citas_doctor')
    else:
        return redirect(url_for('index'))

@app.route('/insertar_receta', methods=['GET', 'POST'])
def insertar_receta():
    if 'user_id' in session:
        user_id = session['user_id']

        # Consulta SQL para verificar si hay una cita con Estado 5 del doctor logueado
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                c.ID_Paciente
            FROM 
                citas c
            INNER JOIN 
                doctores d ON c.ID_Doctor = d.ID_Doctor
            INNER JOIN 
                usuario u ON d.ID_Persona = u.ID_Persona
            WHERE 
                u.ID_Usuario = %s AND c.Estado = 5
            LIMIT 1
        """, (user_id,))

        result = cur.fetchone()
        cur.close()

        if result:
            # Extraer el ID del paciente
            id_paciente = result[0]

            if request.method == 'POST':
                id_medicamento = request.form['ID_Medicamento']
                dosis = request.form['Dosis']
                duracion = request.form['Duracion']
                fecha_receta = datetime.now().strftime('%Y-%m-%d')
                estado = 5

                cur = mysql.connection.cursor()
                cur.execute("""
                    INSERT INTO recetas (ID_Paciente, ID_Medicamento, Fecha_Receta, Dosis, Duracion, Estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_paciente, id_medicamento, fecha_receta, dosis, duracion, estado))
                mysql.connection.commit()
                cur.close()

                return redirect('/insertar_receta')

            # Si es GET, obtener la lista de medicamentos para mostrar en el menú desplegable
            cur = mysql.connection.cursor()
            cur.execute("SELECT ID_Medicamento, Nombre_Medicamento, Descripcion FROM medicamentos WHERE Estado = 1")
            medicamentos = cur.fetchall()
            cur.close()

            return render_template('agregar_receta.html', medicamentos=medicamentos)
        else:
            flash('No se encontraron citas con Estado 5.')
            return redirect('/mis_citas_doctor')
    else:
        return redirect(url_for('index'))

@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    if 'user_id' in session:
        user_id = session['user_id']

        # Conectar al cursor para realizar consultas
        cur = mysql.connection.cursor()

        # Consulta para obtener el ID del paciente con cita en Estado 5
        cur.execute("""
            SELECT 
                c.ID_Paciente
            FROM 
                citas c
            INNER JOIN 
                doctores d ON c.ID_Doctor = d.ID_Doctor
            INNER JOIN 
                usuario u ON d.ID_Persona = u.ID_Persona
            WHERE 
                u.ID_Usuario = %s AND c.Estado = 5
            LIMIT 1
        """, (user_id,))

        result = cur.fetchone()

        if result:
            id_paciente = result[0]
            cur = mysql.connection.cursor()

            # Obtener el precio del tratamiento relacionado con detalle_tratamiento con Estado 5
            cur.execute("""
                SELECT 
                    t.Precio
                FROM 
                    detalle_tratamiento dt
                INNER JOIN 
                    tratamientos t ON dt.ID_Tratamiento = t.ID_Tratamiento
                WHERE 
                    dt.ID_Paciente = %s AND dt.Estado = 5
            """, (id_paciente,))
            tratamiento_precio = cur.fetchone()
            tratamiento_precio = tratamiento_precio[0] if tratamiento_precio else 0

            # Variable para almacenar el total de medicamentos, asumida a 0 si no se procesa más adelante
            total_medicamentos = 0

            # Verificar si hay registros en la tabla recetas
            cur.execute("SELECT COUNT(*) FROM recetas WHERE ID_Paciente = %s AND Estado = 5", (id_paciente,))
            recetas_count = cur.fetchone()[0]

            if recetas_count > 0:
                # Si hay recetas, entonces suma los precios de los medicamentos con Estado 5
                cur.execute("""
                    SELECT 
                        SUM(m.Precio) AS total_medicamentos
                    FROM 
                        recetas r
                    INNER JOIN 
                        medicamentos m ON r.ID_Medicamento = m.ID_Medicamento
                    WHERE 
                        r.ID_Paciente = %s AND r.Estado = 5
                """, (id_paciente,))
                total_medicamentos = cur.fetchone()[0] or 0

            cur.close()

            # Calcular el total a pagar
            total_pago = tratamiento_precio + total_medicamentos

            # Insertar el pago en la tabla pagos
            fecha_pago = datetime.now().strftime('%Y-%m-%d')
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO pagos (ID_Paciente, Monto, Fecha_Pago)
                VALUES (%s, %s, %s)
            """, (id_paciente, total_pago, fecha_pago))
            mysql.connection.commit()

            # Actualizar el Estado a 4 en las tablas: citas y detalle_tratamiento siempre
            cur.execute("""
                UPDATE citas
                SET Estado = 4
                WHERE ID_Paciente = %s AND Estado = 5
            """, (id_paciente,))

            cur.execute("""
                UPDATE detalle_tratamiento
                SET Estado = 4
                WHERE ID_Paciente = %s AND Estado = 5
            """, (id_paciente,))

            cur.execute("""
                UPDATE horariosdisponibles
                SET estado_id = 4
                WHERE estado_id = 5
            """)

            if recetas_count > 0:
                # Solo si hay recetas, actualizamos el estado en recetas también
                cur.execute("""
                    UPDATE recetas
                    SET Estado = 4
                    WHERE ID_Paciente = %s AND Estado = 5
                """, (id_paciente,))

            mysql.connection.commit()
            cur.close()

            return redirect('/mis_citas_doctor')

        else:
            flash('No se encontraron citas con Estado 5.')
            return redirect('/mis_citas_doctor')
      
    else:
        return redirect(url_for('index'))

# Rutas con relacion a pacientes (Del doctor)

@app.route('/pacientes')
def mostrar_pacientes():
    if 'user_id' in session:
        user_id = session['user_id']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT d.ID_Doctor
            FROM doctores d
            INNER JOIN persona p ON d.ID_Persona = p.IDPersona
            INNER JOIN usuario u ON p.IDPersona = u.ID_Persona
            WHERE u.ID_Usuario = %s
        """, (user_id,))
        
        doctor = cur.fetchone()
        cur.close()

        if doctor:
            id_doctor = doctor[0]

            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    p.ID_Paciente, 
                    CONCAT(pr.Nom_persona, ' ', pr.ApellidoP, ' ', pr.ApellidoM) AS Nombre_Completo,
                    p.Fecha_Registro
                FROM 
                    pacientes p
                INNER JOIN 
                    persona pr ON p.ID_Persona = pr.IDPersona
                WHERE 
                    p.ID_Doctor_Asignado = %s
            """, (id_doctor,))
            
            pacientes = cur.fetchall()
            cur.close()

            return render_template('pacientes.html', pacientes=pacientes)

        else:
            return "El usuario logueado no tiene un doctor asociado."
    else:
        return redirect('/login')

@app.route('/pacientes/<int:paciente_id>/tratamientos')
def mostrar_tratamientos_paciente(paciente_id):
    if 'user_id' in session:
        user_id = session['user_id']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT d.ID_Doctor
            FROM doctores d
            INNER JOIN persona p ON d.ID_Persona = p.IDPersona
            INNER JOIN usuario u ON p.IDPersona = u.ID_Persona
            WHERE u.ID_Usuario = %s
        """, (user_id,))
        doctor = cur.fetchone()
        cur.close()

        if doctor:
            id_doctor = doctor[0]

            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    CONCAT(t.Nombre_Tratamiento, ' - $', t.Precio) AS Nombre_Precio_Tratamiento,
                    t.Descripcion,
                    dt.Fecha_Tratamiento,
                    dt.Notas
                FROM 
                    detalle_tratamiento dt
                INNER JOIN 
                    tratamientos t ON dt.ID_Tratamiento = t.ID_Tratamiento
                WHERE 
                    dt.ID_Paciente = %s
                    AND dt.Estado = 4
            """, (paciente_id,))
            
            tratamientos = cur.fetchall()
            cur.close()

            return render_template('tratamientos_paciente.html', tratamientos=tratamientos)

        else:
            return "El usuario logueado no tiene un doctor asociado."
    else:
        return redirect('/login')

@app.route('/pacientes/<int:paciente_id>/recetas')
def mostrar_recetas_paciente(paciente_id):
    if 'user_id' in session:
        user_id = session['user_id']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT d.ID_Doctor
            FROM doctores d
            INNER JOIN persona p ON d.ID_Persona = p.IDPersona
            INNER JOIN usuario u ON p.IDPersona = u.ID_Persona
            WHERE u.ID_Usuario = %s
        """, (user_id,))
        doctor = cur.fetchone()
        cur.close()

        if doctor:
            id_doctor = doctor[0]

            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    CONCAT(m.Nombre_Medicamento, ' - $', m.Precio) AS Nombre_Precio_Medicamento,
                    m.Descripcion,
                    r.Fecha_Receta,
                    r.Dosis,
                    r.Duracion
                FROM 
                    recetas r
                INNER JOIN 
                    medicamentos m ON r.ID_Medicamento = m.ID_Medicamento
                WHERE 
                    r.ID_Paciente = %s
                    AND r.Estado = 4
            """, (paciente_id,))
            
            recetas = cur.fetchall()
            cur.close()

            return render_template('recetas.html', recetas=recetas)

        else:
            return "El usuario logueado no tiene un doctor asociado."
    else:
        return redirect('/login')

# Rutas con relacion a medicamentos (Del administrador)

@app.route('/medicamentos')
def ver_medicamentos():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT m.ID_Medicamento, m.Nombre_Medicamento, m.Descripcion, m.Precio, e.Estado 
            FROM medicamentos AS m
            JOIN estado AS e ON m.Estado = e.ID_Estado
        """)
        medicamentos = cur.fetchall()
        cur.close()
        return render_template('medicamentos.html', medicamentos=medicamentos)
    else:
        return redirect(url_for('index'))
    
@app.route('/agregar_medicamento', methods=['GET', 'POST'])
def agregar_medicamento():
    if 'user_id' in session:
        if request.method == 'POST':
            nombre_medicamento = request.form['nombre_medicamento']
            descripcion = request.form['descripcion']
            precio = request.form['precio']
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO medicamentos (Nombre_Medicamento, Descripcion, Precio, Estado) VALUES (%s, %s, %s, 1)", 
            (nombre_medicamento, descripcion, precio))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('ver_medicamentos'))
        
        return render_template('agregar_medicamento.html')
    else:
        return redirect(url_for('index'))

@app.route('/editar_medicamento/<id>', methods=['GET'])
def editar_medicamento(id):
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM medicamentos WHERE ID_Medicamento = %s", (id,))
        medicamento = cur.fetchone()
        cur.close()
        return render_template('editar_medicamento.html', medicamento=medicamento)
    else:
        return redirect(url_for('index'))  

@app.route('/actualizar_medicamento/<int:id>', methods=['POST'])
def actualizar_medicamento(id):
    nombre_medicamento = request.form['nombre_medicamento']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE medicamentos 
        SET Nombre_Medicamento = %s, Descripcion = %s, Precio = %s 
        WHERE ID_Medicamento = %s
    """, (nombre_medicamento, descripcion, precio, id))
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('ver_medicamentos'))

@app.route('/inactivar_medicamento/<id>')
def inactivar_medicamento(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE medicamentos SET Estado = 2 WHERE ID_Medicamento = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('ver_medicamentos'))

@app.route('/activar_medicamento/<id>')
def activar_medicamento(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE medicamentos SET Estado = 1 WHERE ID_Medicamento = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('ver_medicamentos'))

# Ruta con relacion a pagos (Del Adminstrador)

@app.route('/pagos')
def pagos():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
                SELECT 
                    pagos.ID_Pago,
                    CONCAT(persona.Nom_persona, ' ', persona.ApellidoP, ' ', persona.ApellidoM) AS Nombre_Completo,
                    pagos.Monto,
                    pagos.Fecha_Pago
                FROM 
                    pagos
                JOIN 
                    pacientes ON pagos.ID_Paciente = pacientes.ID_Paciente
                JOIN 
                    persona ON pacientes.ID_Persona = persona.IDPersona;
            """)
        pagos = cur.fetchall()
        cur.close()
        return render_template('pagos.html', pagos=pagos)
    else:
        return redirect(url_for('index'))

# Rutas con relacion a registros de pacientes (Del Administrador)

@app.route('/pacientes_registros')
def pacientes_registros():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                p.ID_Paciente, 
                CONCAT(pr.Nom_persona, ' ', pr.ApellidoP, ' ', pr.ApellidoM) AS Nombre_Completo,
                p.Fecha_Registro,
                CONCAT(dpersona.Nom_persona, ' ', dpersona.ApellidoP, ' ', dpersona.ApellidoM) AS Doctor_Asignado
            FROM 
                pacientes p
            INNER JOIN 
                persona pr ON p.ID_Persona = pr.IDPersona
            LEFT JOIN 
                doctores d ON p.ID_Doctor_Asignado = d.ID_Doctor
            LEFT JOIN 
                persona dpersona ON d.ID_Persona = dpersona.IDPersona
        """)
        
        pacientes = cur.fetchall() 
        cur.close()

        return render_template('pacientes_admin.html', pacientes=pacientes)
    else:
        return redirect(url_for('index'))

@app.route('/pacientes_registros/<int:paciente_id>/tratamientos')
def mostrar_tratamientos_paciente_registro(paciente_id):
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                CONCAT(t.Nombre_Tratamiento, ' - $', t.Precio) AS Nombre_Precio_Tratamiento,
                t.Descripcion,
                dt.Fecha_Tratamiento,
                dt.Notas
            FROM 
                detalle_tratamiento dt
            INNER JOIN 
                tratamientos t ON dt.ID_Tratamiento = t.ID_Tratamiento
            WHERE 
                dt.ID_Paciente = %s
                AND dt.Estado = 4
        """, (paciente_id,))
        
        tratamientos = cur.fetchall()
        cur.close()

        return render_template('tratamientos_paciente.html', tratamientos=tratamientos)
    else:
        return redirect(url_for('index'))
    
@app.route('/pacientes_registros/<int:paciente_id>/recetas')
def mostrar_recetas_paciente_registro(paciente_id):
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                CONCAT(m.Nombre_Medicamento, ' - $', m.Precio) AS Nombre_Precio_Medicamento,
                m.Descripcion,
                r.Fecha_Receta,
                r.Dosis,
                r.Duracion
            FROM 
                recetas r
            INNER JOIN 
                medicamentos m ON r.ID_Medicamento = m.ID_Medicamento
            WHERE 
                r.ID_Paciente = %s
                AND r.Estado = 4
        """, (paciente_id,))
        
        recetas = cur.fetchall()
        cur.close()

        return render_template('recetas.html', recetas=recetas)
    else:
        return redirect(url_for('index'))
    
# Rutas con relacion a doctores (Del administrador)

@app.route('/doctores')
def doctores():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT d.ID_Doctor, 
                CONCAT(p.Nom_persona, ' ', p.ApellidoP, ' ', p.ApellidoM) AS NombreCompleto, 
                d.Especialidad,
                e.Estado AS NombreEstado
            FROM doctores d
            JOIN persona p ON d.ID_Persona = p.IDPersona
            JOIN estado e ON p.Estado = e.ID_Estado
        """)
        doctores = cur.fetchall()
        return render_template('doctores.html', doctores=doctores)
    else:
        return redirect(url_for('index'))
    
@app.route('/agregar_doctor', methods=['POST', 'GET'])
def agregar_doctor():
    if 'user_id' in session:
        if request.method == 'POST':
            # Obtener datos del formulario
            Nom_Persona = request.form['Nom_Persona']
            ApellidoP = request.form['ApellidoP']
            ApellidoM = request.form['ApellidoM']
            Email = request.form['Email']
            Contraseña = request.form['Contraseña']
            Fecha_Nacimiento = request.form['Fecha_Nacimiento']
            Especialidad = request.form['Especialidad']
            
            # Insertar en la tabla persona
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO persona (Nom_persona, ApellidoP, ApellidoM, Email, Fecha_Nacimiento, Estado) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (Nom_Persona, ApellidoP, ApellidoM, Email, Fecha_Nacimiento, 1))
            mysql.connection.commit()

            # Obtener el ID de la última persona registrada
            cur.execute("SELECT LAST_INSERT_ID()")
            id_persona = cur.fetchone()[0]

            # Insertar en la tabla usuario
            cur.execute("""
                INSERT INTO usuario (ID_Persona, Contraseña, ID_Tipo) 
                VALUES (%s, %s, %s)
            """, (id_persona, Contraseña, 2))
            mysql.connection.commit()

            # Obtener el ID de usuario recién creado
            cur.execute("SELECT LAST_INSERT_ID()")
            usuario_id = cur.fetchone()[0]

            # Insertar en la tabla doctores
            cur.execute("""
                INSERT INTO doctores (Especialidad, ID_Persona, usuario_id) 
                VALUES (%s, %s, %s)
            """, (Especialidad, id_persona, usuario_id))
            mysql.connection.commit()

            flash('Doctor registrado exitosamente', 'success')
            return redirect(url_for('doctores'))
        
        return render_template('agregar_doctor.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/editar_doctor/<id>', methods=['GET'])
def editar_doctor(id):
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT d.ID_Doctor, 
                p.Nom_persona, 
                p.ApellidoP, 
                p.ApellidoM, 
                p.Email, 
                p.Fecha_Nacimiento, 
                d.Especialidad, 
                u.Contraseña, 
                p.Estado
            FROM doctores d
            JOIN persona p ON d.ID_Persona = p.IDPersona
            JOIN usuario u ON d.usuario_id = u.ID_Usuario
            WHERE d.ID_Doctor = %s
        """, (id,))
        doctor = cur.fetchone()
        cur.close()
        return render_template('editar_doctor.html', doctor=doctor)
    else:
        return redirect(url_for('index'))

@app.route('/actualizar_doctor/<int:id>', methods=['POST'])
def actualizar_doctor(id):
    Nom_Persona = request.form['Nom_Persona']
    ApellidoP = request.form['ApellidoP']
    ApellidoM = request.form['ApellidoM']
    Email = request.form['Email']
    Contraseña = request.form['Contraseña']
    Fecha_Nacimiento = request.form['Fecha_Nacimiento']
    Especialidad = request.form['Especialidad']
    
    cur = mysql.connection.cursor()
    # Actualizar la tabla persona
    cur.execute("""
        UPDATE persona 
        SET Nom_persona = %s, ApellidoP = %s, ApellidoM = %s, Email = %s, Fecha_Nacimiento = %s
        WHERE IDPersona = (SELECT ID_Persona FROM doctores WHERE ID_Doctor = %s)
    """, (Nom_Persona, ApellidoP, ApellidoM, Email, Fecha_Nacimiento, id))
    
    # Actualizar la tabla usuario
    cur.execute("""
        UPDATE usuario 
        SET Contraseña = %s
        WHERE ID_Usuario = (SELECT usuario_id FROM doctores WHERE ID_Doctor = %s)
    """, (Contraseña, id))
    
    # Actualizar la tabla doctores
    cur.execute("""
        UPDATE doctores 
        SET Especialidad = %s
        WHERE ID_Doctor = %s
    """, (Especialidad, id))
    
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('doctores'))

@app.route('/inactivar_doctor/<id>')
def inactivar_doctor(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE persona 
        SET Estado = 2 
        WHERE IDPersona = (SELECT ID_Persona FROM doctores WHERE ID_Doctor = %s)
    """, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('doctores'))

@app.route('/activar_doctor/<id>')
def activar_doctor(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE persona 
        SET Estado = 1 
        WHERE IDPersona = (SELECT ID_Persona FROM doctores WHERE ID_Doctor = %s)
    """, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('doctores'))

# Rutas con relacion a tratamientos (Del administrador)

@app.route('/tratamientos')
def tratamientos():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT t.ID_Tratamiento, 
                t.Nombre_Tratamiento, 
                t.Descripcion, 
                t.Precio, 
                e.Estado
            FROM tratamientos t
            JOIN estado e ON t.Estado = e.ID_Estado
        """)
        tratamientos = cur.fetchall()
        cur.close()
        return render_template('tratamientos.html', tratamientos=tratamientos)
    else:
        return redirect(url_for('index'))
    
@app.route('/agregar_tratamiento', methods=['POST', 'GET'])
def agregar_tratamiento():
    if 'user_id' in session:
        if request.method == 'POST':
            Nombre_Tratamiento = request.form['Nombre_Tratamiento']
            Descripcion = request.form['Descripcion']
            Precio = request.form['Precio']
            Estado = 1

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO tratamientos (Nombre_Tratamiento, Descripcion, Precio, Estado)
                VALUES (%s, %s, %s, %s)
            """, (Nombre_Tratamiento, Descripcion, Precio, Estado))
            mysql.connection.commit()
            cur.close()

            flash('Tratamiento registrado exitosamente', 'success')
            return redirect(url_for('tratamientos'))

        return render_template('agregar_tratamiento.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/editar_tratamiento/<int:id>', methods=['GET'])
def editar_tratamiento(id):
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT ID_Tratamiento, 
                Nombre_Tratamiento, 
                Descripcion, 
                Precio, 
                Estado
            FROM tratamientos
            WHERE ID_Tratamiento = %s
        """, (id,))
        tratamiento = cur.fetchone()
        cur.close()
        return render_template('editar_tratamiento.html', tratamiento=tratamiento)
    else:
        return redirect(url_for('index'))
    
@app.route('/actualizar_tratamiento/<int:id>', methods=['POST'])
def actualizar_tratamiento(id):
    Nombre_Tratamiento = request.form['Nombre_Tratamiento']
    Descripcion = request.form['Descripcion']
    Precio = request.form['Precio']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE tratamientos 
        SET Nombre_Tratamiento = %s, Descripcion = %s, Precio = %s
        WHERE ID_Tratamiento = %s
    """, (Nombre_Tratamiento, Descripcion, Precio, id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('tratamientos'))

@app.route('/inactivar_tratamiento/<int:id>')
def inactivar_tratamiento(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE tratamientos 
        SET Estado = 2 
        WHERE ID_Tratamiento = %s
    """, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('tratamientos'))

@app.route('/activar_tratamiento/<int:id>')
def activar_tratamiento(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE tratamientos 
        SET Estado = 1 
        WHERE ID_Tratamiento = %s
    """, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('tratamientos'))

# Rutas con relacion a la IA

openai.api_key = ""

relaciones = {
    'usuario': {
        'ID_Persona': {
            'tabla': 'persona',
            'clave': 'IDPersona',
            'columna': "CONCAT(Nom_persona, ' ', ApellidoP, ' ', ApellidoM)"
        },
        'ID_Tipo': {
            'tabla': 'tipos_usu',
            'clave': 'ID_Tipo',
            'columna': 'Tipo'
        },
    },

    'doctores': {
        'ID_Persona': {
            'tabla': 'persona',
            'clave': 'IDPersona',
            'columna': "CONCAT(Nom_persona, ' ', ApellidoP, ' ', ApellidoM)"
        }
    },

    'pacientes': {
        'ID_Persona': {
            'tabla': 'persona',
            'clave': 'IDPersona',
            'columna': "CONCAT(Nom_persona, ' ', ApellidoP, ' ', ApellidoM)"
        },
        'ID_Doctor_Asignado': {
            'tabla': 'doctores',
            'clave': 'ID_Doctor',
            'columna': (
                "CONCAT(persona.Nom_persona, ' ', persona.ApellidoP, ' ', persona.ApellidoM)",
                {
                    'tabla': 'persona',
                    'clave': 'IDPersona',
                    'columna': "CONCAT(Nom_persona, ' ', ApellidoP, ' ', ApellidoM)"
                }
            )
        }
    },

    'detalle_tratamiento': {
        'ID_Tratamiento': {
            'tabla': 'tratamientos',
            'clave': 'ID_Tratamiento',
            'columna': 'Nombre_Tratamiento'
        },
        'ID_Paciente': {
            'tabla': 'pacientes',
            'clave': 'ID_Paciente',
            'columna': (
                "CONCAT(persona.Nom_persona, ' ', persona.ApellidoP, ' ', persona.ApellidoM)",
                {
                    'tabla': 'persona',
                    'clave': 'IDPersona',
                    'columna': "CONCAT(Nom_persona, ' ', ApellidoP, ' ', ApellidoM)"
                }
            )
        }
    },

    'horariosdisponibles': {
        'doctor_id': {
            'tabla': 'doctores',
            'clave': 'ID_Doctor',
            'columna': (
                "CONCAT(persona.Nom_persona, ' ', persona.ApellidoP, ' ', persona.ApellidoM)",
                {
                    'tabla': 'persona',
                    'clave': 'IDPersona',
                    'columna': "CONCAT(Nom_persona, ' ', ApellidoP, ' ', ApellidoM)"
                }
            )
        }
    },

    'pagos': {
        'ID_Paciente': {
            'tabla': 'pacientes',
            'clave': 'ID_Paciente',
            'columna': (
                "CONCAT(persona.Nom_persona, ' ', persona.ApellidoP, ' ', persona.ApellidoM)",
                {
                    'tabla': 'persona',
                    'clave': 'IDPersona',
                    'columna': "CONCAT(Nom_persona, ' ', ApellidoP, ' ', ApellidoM)"
                }
            )
        }
    },

    'recetas': {
        'ID_Paciente': {
            'tabla': 'pacientes',
            'clave': 'ID_Paciente',
            'columna': (
                "CONCAT(persona.Nom_persona, ' ', persona.ApellidoP, ' ', persona.ApellidoM)",
                {
                    'tabla': 'persona',
                    'clave': 'IDPersona',
                    'columna': "CONCAT(Nom_persona, ' ', ApellidoP, ' ', ApellidoM)"
                }
            )
        },
        'ID_Medicamento': {
            'tabla': 'medicamentos',
            'clave': 'ID_Medicamento',
            'columna': "CONCAT(Nombre_Medicamento, ' ', Descripcion, ' ', Precio)"
        }
    }
}

def get_sql_query(user_input):
    """
    Convierte la entrada del usuario en una consulta SQL optimizada usando relaciones predefinidas
    y listas negras de campos por tabla.
    """
    def get_table_structure(table_name):
        """
        Obtiene la estructura de una tabla: nombres de columnas.
        """
        cursor = mysql.connection.cursor()
        try:
            query = f"DESCRIBE {table_name};"
            cursor.execute(query)
            columns = cursor.fetchall()
            return [column[0] for column in columns]
        except Exception as e:
            print(f"Error al obtener la estructura de la tabla '{table_name}': {e}")
            return []
        finally:
            cursor.close()

    # Listas negras de campos por tabla
    listas_negras = {
        "usuario": ["ID_Persona", "ID_Tipo"],
        "doctores": ["ID_Persona"],
        "pacientes": ["ID_Persona","ID_Doctor_Asignado"],
        "detalle_tratamiento": ["ID_Tratamiento","ID_Paciente"],
        "horariosdisponibles": ["doctor_id"],
        "pagos": ["ID_Paciente"],
        "recetas": ["ID_Paciente","ID_Medicamento"]
    }

    # Obtener las relaciones y estructuras dinámicamente
    relaciones_dinamicas = {}
    for table in relaciones:
        estructura = get_table_structure(table)
        relaciones_dinamicas[table] = {
            "estructura": estructura,
            "relaciones": relaciones.get(table, {}),
            "excluir": listas_negras.get(table, []) 
        }

    # Generar descripción de relaciones para el prompt
    table_relations = "\n".join(
        f"- '{table}':\n" +
        "\n".join(
            f"  * Relaciona '{col}' con '{rel['tabla']}' usando {table}.{col} = {rel['tabla']}.{rel['clave']}, y selecciona '{rel['columna']}' como alias."
            for col, rel in relaciones_dinamicas[table]["relaciones"].items()
        )
        for table in relaciones_dinamicas
    )

    # Generar descripción de exclusiones
    exclusion_descriptions = "\n".join(
        f"- '{table}': No selecciones estos campos: {relaciones_dinamicas[table]['excluir']}"
        for table in relaciones_dinamicas
        if relaciones_dinamicas[table]["excluir"]
    )

    # Prompt para OpenAI
    prompt = f"""
Eres un asistente SQL avanzado. Tienes acceso a las siguientes relaciones y estructuras de tablas:

Estructuras de tablas:
{chr(10).join(f"- '{table}': {relaciones_dinamicas[table]['estructura']}" for table in relaciones_dinamicas)}

Relaciones entre tablas:
{table_relations}

Exclusiones de campos:
{exclusion_descriptions}

Tu tarea:
1. Si el usuario solicita "todos los datos" de una tabla, selecciona:
    - Todos los campos de la tabla principal excepto los que se indiquen en la sección de exclusiones.
    - Campos de las tablas relacionadas según los `JOIN` necesarios, utilizando las relaciones proporcionadas.
2. Si el usuario solicita datos específicos, selecciona solo los campos indicados por el usuario y sus relaciones correspondientes.
3. Incluye explícitamente los nombres de las columnas (no uses 'tabla.*').
4. Respeta las exclusiones especificadas para cada tabla.
5. Solo responde con la consulta SQL sin explicaciones adicionales.

Solicitud del usuario: {user_input}
"""

    # Llamar a la API de OpenAI para generar la consulta
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    sql_query = response.choices[0].message['content'].strip()
    return sql_query

def execute_sql_query(query):
    """
    Ejecuta la consulta SQL y devuelve resultados o mensajes de error en formato presentable.
    """
    cursor = mysql.connection.cursor()
    try:
        # Ejecutar la consulta SQL proporcionada
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # Si no hay resultados, informar al usuario
        if not results:
            return {"message": "No se encontraron registros que coincidan con su consulta."}
        
        return {"data": results, "columns": column_names}
    
    except Exception as err:
        error_message = (
            "Error en la ejecución: Verifique los datos ingresados. "
            "Es posible que alguno de los nombres o IDs ingresados no sea válido o que el registro no exista. "
            "Intente corregir la consulta y vuelva a intentarlo."
        )
        return {"message": error_message}
    
    finally:
        cursor.close()
        
@app.route('/inteligencia_artificial', methods=['GET', 'POST'])
def inteligencia_artificial():
    result = None
    sql_query = None

    if request.method == 'POST':
        user_input = request.form['user_input']
        sql_query = get_sql_query(user_input)

        # Validación de la consulta SQL antes de ejecutarla
        if not sql_query:
            result = "Error: No se pudo generar una consulta SQL válida. Intente expresar su solicitud de otra forma."
        else:
            result = execute_sql_query(sql_query)

    # Renderizar el resultado y la consulta generada
    return render_template('inteligencia_artificial.html', result=result, sql_query=sql_query)

# Rutas con relacion a la busqueda

routes = {
    "inicio": "/",
    "mis citas": "/mis_citas",
    "mis recetas": "/mis_recetas",
    "horarios": "/mis_horarios",
    "citas": "/mis_citas_doctor",
    "pacientes": "/pacientes",
    "medicamentos": "/medicamentos",
    "pagos": "/pagos",
    "registros de pacientes": "/pacientes_registros",
    "doctores": "/doctores",
    "tratamientos": "/tratamientos",
    "asistente virtual": "/inteligencia_artificial",
    "cerrar sesión": "/logout"
}

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip().lower() 
    if query:
        # Buscar la ruta correspondiente
        for name, path in routes.items():
            if query in name.lower():
                return redirect(path) 

    # Si no se encuentra, mostrar la página de error
    return render_template('error.html', error_code=404, error_message="No se encontró la página que buscabas.")

@app.route('/not_found')
def not_found():
    return render_template('error.html', error_code=404, error_message="Página no encontrada.")

if __name__ == '__main__':
 app.run(port=4000, debug = True)