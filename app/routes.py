from flask import render_template, redirect, url_for, session, request, make_response
from app import app
from app.encryption import decrypt_aes, ofuscar_dni, get_master_key
from app.reading import read_db


key = get_master_key()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/deposit', methods=['GET'])
def deposit():
    modo = request.cookies.get('modo', 'light')
    return render_template('deposit.html',darkmode=modo)


@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template('form.html')


@app.route('/login', methods=["GET"])
def login():
    return render_template("login.html")


@app.route('/edit_user/<email>', methods=['GET'])
def edit_user(email):
    email_sesion = session.get('email')
    db = read_db("db.txt")

    if email not in db:
        return redirect(url_for('records', message="Usuario no encontrado"))

    user_info = db[email]
    dni_encrypt = db[email]["dni"]
    nonce = db[email]["nonce"]
    dni_decrypt = decrypt_aes(dni_encrypt,nonce,key)
    modo = request.cookies.get('modo', 'light')
    return render_template('edit_user.html',user_data=user_info,
                                            dni=dni_decrypt, 
                                            email=email,
                                            email_sesion = email_sesion,
                                            darkmode=modo)


# Formulario de retiro
@app.route('/withdraw', methods=['GET'])
def withdraw():
    email = session.get('email')
    print(email)
    modo = request.cookies.get('modo', 'light')
    transactions = read_db("transaction.txt")
    current_balance = sum(float(t['balance']) for t in transactions.get(email, []))
    return render_template('withdraw.html', balance=current_balance,
                           darkmode=modo)
