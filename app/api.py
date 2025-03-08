import datetime

from time import time
from app.validation import *
from app.reading import *
from app.encryption import *
from flask import request, jsonify, redirect, url_for, render_template, session, make_response
from app import app

app.secret_key = 'your_secret_key'
key = get_master_key()


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=5)

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

    dni_crypt, nonce = encrypt_aes(dni,key)
    print(dni_crypt)
    print(nonce)
    print(key)


    db = read_db("db.txt")
    db[email] = {
        'nombre': normalize_input(nombre),
        'apellido': normalize_input(apellido),
        'username': normalize_input(username),
        'password': password_hash.hex(),
        'salt': salt.hex(),
        "dni": dni_crypt,
        "nonce": nonce,
        'dob': normalize_input(dob),
        "role": normalize_input(str(role))
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
    if email not in db:
        error = "Credenciales inválidas"
        return render_template('login.html', error=error)
    else:
        if email not in intentos_fallidos:
            intentos_fallidos[email] = {"intentos": 0,"bloqueado": False, "tiempo_bloqueo": 0, "time": datetime.datetime.now()}
        else:
            if intentos_fallidos[email]["bloqueado"] == False:
                if intentos_fallidos[email]["intentos"] >= 2:
                    intentos_fallidos[email]["tiempo_bloqueo"] = 300
                    intentos_fallidos[email]["bloqueado"] = True
            else:
                if (datetime.datetime.now() - intentos_fallidos[email]["time"]).total_seconds() > intentos_fallidos[email]["tiempo_bloqueo"]:
                        intentos_fallidos[email]["intentos"] = 0
                        intentos_fallidos[email]["tiempo_bloqueo"] = 0
                        intentos_fallidos[email]["bloqueado"] = False
                        intentos_fallidos[email]["time"] = datetime.datetime.now()
                else:
                    error = f"Estas bloqueado por {300//60} min mi rey :("
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

#Enpoint para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login',message='Has cerrado sesión'))

# Página principal del menú del cliente
@app.route('/customer_menu')
def customer_menu():
    if 'email' not in session:
        error_msg = "Por favor, inicia sesión para acceder a esta página."
        return render_template('login.html', error=error_msg)

    email = session.get('email')
    db = read_db("db.txt")
    transactions = read_db("transaction.txt")
    current_balance = sum(float(t['balance']) for t in transactions.get(email, []))
    last_transactions = transactions.get(email, [])[-5:]
    message = request.args.get('message', '')
    error = request.args.get('error', 'false').lower() == 'true'
    return render_template('customer_menu.html',
                           message=message,
                           nombre=db.get(email)['nombre'],
                           balance=current_balance,
                           last_transactions=last_transactions,
                           error=error)



# Endpoint para leer un registro
@app.route('/records', methods=['GET'])
def read_record():
    if 'email' not in session:
        error_msg = "Por favor, inicia sesión para acceder a esta página."
        return render_template('login.html', error=error_msg)
    
    db = read_db("db.txt")
    user_email = session.get('email')
    user = db.get(user_email, None)
    message = request.args.get('message', '')

    # Si el usuario es admin, mostrar todos los registros con DNI ofuscado
    if session.get('role') == 'admin':

        for user in db:
            dni = db[user]["dni"]
            nonce = db[user]["nonce"]
            dni_decrypt = ofuscar_dni(decrypt_aes(dni,nonce,key))
            db[user]["dni"] = dni_decrypt
        
        return render_template('records.html',
                               users=db,
                               role=session.get('role'),
                               message=message,
                               )
    else:
        dni = db[user_email]["dni"]
        nonce = db[user_email]["nonce"]
        dni_decrypt = ofuscar_dni(decrypt_aes(dni,nonce,key))
        db[user_email]["dni"] = dni_decrypt
        return render_template('records.html',
                               users={user_email: user},
                               error=None,
                               message=message)


@app.route('/update_user/<email>', methods=['POST'])
def update_user(email):

    if 'email' not in session:
        error_msg = "Por favor, inicia sesión para acceder a esta página."
        return render_template('login.html', error=error_msg)
    

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
                               dni = decrypt_aes(db[email]["dni"],db[email]["nonce"],key),
                               email=email,
                               error=errores)

    dni_encrypt, nonce = encrypt_aes(dni,key)
    
    db[email]['dni'] = dni_encrypt
    db[email]['nonce'] = nonce
    db[email]['username'] = normalize_input(username)
    db[email]['nombre'] = normalize_input(nombre)
    db[email]['apellido'] = normalize_input(apellido)
    db[email]['dob'] = normalize_input(dob)


    write_db("db.txt", db)
    

    # Redirigir al usuario a la página de records con un mensaje de éxito
    return redirect(url_for('read_record', message="Información actualizada correctamente"))


# Endpoint para depósito
@app.route('/api/deposit', methods=['POST'])
def api_deposit():
    if 'email' not in session:
        error_msg = "Por favor, inicia sesión para acceder a esta página."
        return render_template('login.html', error=error_msg)

    deposit_balance = request.form['balance']
    deposit_email = session.get('email')

    db = read_db("db.txt")
    transactions = read_db("transaction.txt")

    # Verificamos si el usuario existe
    if deposit_email in db:
        # Guardamos la transacción
        transaction = {"balance": deposit_balance, "type": "Deposit", "timestamp": str(datetime.datetime.now())}

        # Verificamos si el usuario tiene transacciones previas
        if deposit_email in transactions:
            transactions[deposit_email].append(transaction)
        else:
            transactions[deposit_email] = [transaction]
        write_db("transaction.txt", transactions)

        return redirect(url_for('customer_menu', message="Depósito exitoso"))

    return redirect(url_for('customer_menu', message="Email no encontrado"))


# Endpoint para retiro
@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    if 'email' not in session:
        error_msg = "Por favor, inicia sesión para acceder a esta página."
        return render_template('login.html', error=error_msg)
    
    db = read_db("db.txt")

    email = session.get('email')
    amount = float(request.form['balance'])
    password = str(request.form['password'])

    stored_hash = db[email]["password"]
    stored_salt = db[email]["salt"]

    if verify_password(password, stored_hash, stored_salt):
        if amount <= 0:
            return redirect(url_for('customer_menu',
                                    message="La cantidad a retirar debe ser positiva",
                                    error=True))

        transactions = read_db("transaction.txt")
        current_balance = sum(float(t['balance']) for t in transactions.get(email, []))

        if amount > current_balance:
            return redirect(url_for('customer_menu',
                                    message="Saldo insuficiente para retiro",
                                    error=True))

        transaction = {"balance": -amount, "type": "Withdrawal", "timestamp": str(datetime.datetime.now())}

        if email in transactions:
            transactions[email].append(transaction)
        else:
            transactions[email] = [transaction]

        write_db("transaction.txt", transactions)

        return redirect(url_for('customer_menu',
                                message="Retiro exitoso",
                                error=False))
    else:
        return redirect(url_for('customer_menu',
                        message="Tu contraseña es incorrecta =(",
                        error=True))