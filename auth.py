from flask import Blueprint, render_template, request, session, redirect, url_for
import bcrypt
import kickbox
import keys
from keys import connect_db

auth_bp = Blueprint('auth', __name__)

# Checagem de email com Kickbox
def is_email_address_valid(email):
    client = kickbox.Client(keys.api_key)
    kbx = client.kickbox()
    response = kbx.verify(email)
    return response.body['result'] != "undeliverable"

# Impedir url injection
def user_has_permission(user_id, group_id):
    conn = connect_db()
    cur = conn.cursor()

    # Executar a consulta para verificar se usuario tem permissao para acessar o grupo
    cur.execute('SELECT * FROM "Group" JOIN UserGroup ON "Group".id = UserGroup.group_id WHERE UserGroup.user_id = ? AND "Group".id = ?', (user_id, group_id))
    result = cur.fetchone()

    conn.close()

    # Verificar se a consulta retornou alguma linha
    if result:
        return True  
    else:
        return False

# Rotas
@auth_bp.route('/')
def index():
    # Verifica se ha erro de login na sessao
    login_error = session.pop('login_error', None)
    return render_template('login.html', login_error=login_error)

@auth_bp.route('/login', methods=['POST'])
def login():
    if 'create_new_user' in request.form:
        return redirect(url_for('auth.register'))
    else:
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM "User" WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()

        if user:
            # Obtenha o hash da senha do banco de dados
            stored_password_hash = user[3]

            # Verifique se a senha fornecida corresponde ao hash armazenado
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
                session['user'] = username
                session['id'] = user[0]
                return redirect(url_for('groups.home'))
            else:
                session['login_error'] = 'Invalid username or password'
                return redirect(url_for('auth.index'))
        else:
            session['login_error'] = 'Invalid username or password'
            return redirect(url_for('auth.index'))
        
# Fazer Logout
@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.index'))

# Cadastro de usuario
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        register_stats = session.pop('register_stats', None)
        conn = connect_db()
        cur = conn.cursor()

        cur.execute('SELECT * FROM "User" WHERE username = ?', (username,))
        existing_user = cur.fetchone()
        cur.execute('SELECT * FROM "User" WHERE email = ?', (email,))
        existing_email = cur.fetchone()

        # Verifica se o usuario ou o e-mail ja existem
        if existing_user:
            conn.close()
            session['register_stats'] = 'Username already exists. Please choose another username.'
            return render_template('register.html', register_stats=register_stats)
        elif existing_email:
            conn.close()
            session['register_stats'] = 'Email already exists. Please use another email.'
            return render_template('register.html', register_stats=register_stats)
        else:
            valid = is_email_address_valid(email)
            if valid:
                # Gerar o hash da senha antes de armazena-la no banco de dados
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cur.execute('INSERT INTO "User" (username, email, password_hash) VALUES (?, ?, ?)', (username, email, hashed_password))
                conn.commit()
                conn.close()
                session['login_error'] = 'User created successfully'
                return redirect(url_for('auth.index'))
            else:
                session['register_stats'] = 'Please enter a valid email!'
                return render_template('register.html', register_stats=register_stats)
    else:
        return render_template('register.html')
