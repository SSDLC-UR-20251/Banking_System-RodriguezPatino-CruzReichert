import datetime
from time import time
from app.validation import *
from app.reading import *
from app.encryption import *
from flask import request, jsonify, redirect, url_for, render_template, session, make_response
from app import app

app.secret_key = 'your_secret_key'


@app.route('/api/users', methods=['POST'])
def create_record():
    data = request.form
    email = data.get('email')
    username = data.get('username')
    nombre = data.get('nombre')
    apellido = data.get('Apellidos')
    password = data.get('password')
    dni = data.get('dni')
    dob = data.get('dob')
    role = data.get('role')
    password_hash, salt = hash_with_salt(password)
    errores = []
    print(data)
    # Validaciones
    if not validate_email(email):
        errores.append("Email inválido")
    if not validate_pswd(password):
        errores.append("Contraseña inválida")
    if not validate_dob(dob):
        errores.append("Fecha de nacimiento inválida")
    if not validate_dni(dni):
        errores.append("DNI inválido")
    if not validate_user(username):
        errores.append("Usuario inválido")
    if not validate_name(nombre):
        errores.append("Nombre inválido")
    if not validate_name(apellido):
        errores.append("Apellido inválido")

    if errores:
        return render_template('form.html', error=errores)

    email = normalize_input(email)

    db = read_db("db.txt")
    db[email] = {
        'nombre': normalize_input(nombre),
        'apellido': normalize_input(apellido),
        'username': normalize_input(username),
        'password': password_hash.hex(),
        'salt': salt.hex(),
        "dni": dni,
        'dob': normalize_input(dob),
        "role": normalize_input(role)
    }

    write_db("db.txt", db)
    return redirect("/login")


intentos_fallidos = {}

@app.route('/delete_user/<email>', methods=['GET'])
def delete_user(email):
    db = read_db("db.txt")
    del db[email]
    write_db("db.txt", db)
    return redirect(url_for('read_record', message="Usuario eliminado correctamente"))



# Endpoint para el login
@app.route('/api/login', methods=['POST'])
def api_login():
    global intentos_fallidos
    email = normalize_input(request.form['email'])
    password = normalize_input(request.form['password'])
    db = read_db("db.txt")

    if email not in intentos_fallidos:
        intentos_fallidos[email] = {"intentos": 0,"bloqueado": False, "tiempo_bloqueo": 0, "time": datetime.datetime.now()}
    else:
        if intentos_fallidos[email]["bloqueado"] == False:
            if intentos_fallidos[email]["intentos"] >= 3:
                intentos_fallidos[email]["tiempo_bloqueo"] = 300
                intentos_fallidos[email]["bloqueado"] = True
        else:
            if (datetime.datetime.now() - intentos_fallidos[email]["time"]).total_seconds() > intentos_fallidos[email]["tiempo_bloqueo"]:
                    intentos_fallidos[email]["intentos"] = 0
                    intentos_fallidos[email]["tiempo_bloqueo"] = 0
                    intentos_fallidos[email]["bloqueado"] = False
                    intentos_fallidos[email]["time"] = datetime.datetime.now()
            else:
                error = "Estas bloqueado mi rey :("
                return render_template('login.html', error=error)

    stored_hash = db[email]["password"]
    stored_salt = db[email]["salt"]

    if verify_password(password, stored_hash, stored_salt):
        session['email'] = email
        session['role'] = db[email]['role']
        return redirect(url_for('customer_menu'))
    else:
        intentos_fallidos[email]["intentos"] += 1
        print(intentos_fallidos)
        return render_template('login.html', error="Credenciales inválidas")





# Página principal del menú del cliente
@app.route('/customer_menu')
def customer_menu():

    db = read_db("db.txt")

    transactions = read_db("transaction.txt")
    current_balance = 100
    last_transactions = []
    message = request.args.get('message', '')
    error = request.args.get('error', 'false').lower() == 'true'
    return render_template('customer_menu.html',
                           message=message,
                           nombre="",
                           balance=current_balance,
                           last_transactions=last_transactions,
                           error=error,)


# Endpoint para leer un registro
@app.route('/records', methods=['GET'])
def read_record():
    db = read_db("db.txt")
    message = request.args.get('message', '')
    return render_template('records.html', users=db,role=session.get('role'),message=message)


@app.route('/update_user/<email>', methods=['POST'])
def update_user(email):
    # Leer la base de datos de usuarios
    db = read_db("db.txt")

    username = request.form['username']
    dni = request.form['dni']
    dob = request.form['dob']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    errores = []

    if not validate_dob(dob):
        errores.append("Fecha de nacimiento inválida")
    if not validate_dni(dni):
        errores.append("DNI inválido")
    if not validate_user(username):
        errores.append("Usuario inválido")
    if not validate_name(nombre):
        errores.append("Nombre inválido")
    if not validate_name(apellido):
        errores.append("Apellido inválido")

    if errores:
        return render_template('edit_user.html',
                               user_data=db[email],
                               email=email,
                               error=errores)


    db[email]['username'] = normalize_input(username)
    db[email]['nombre'] = normalize_input(nombre)
    db[email]['apellido'] = normalize_input(apellido)
    db[email]['dni'] = dni
    db[email]['dob'] = normalize_input(dob)


    write_db("db.txt", db)
    

    # Redirigir al usuario a la página de records con un mensaje de éxito
    return redirect(url_for('read_record', message="Información actualizada correctamente"))

