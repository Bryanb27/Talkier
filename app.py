from flask import Flask, render_template, request, session, redirect, url_for
import bcrypt
import secrets
import string
from flask_socketio import SocketIO
import pyodbc
import kickbox
import datetime
import keys

app = Flask(__name__)
app.secret_key = keys.secret_key
socketio = SocketIO(app)

# Conectar ao banco de dados
def connect_db():
    conn = pyodbc.connect('DRIVER='+keys.driver+';SERVER='+keys.server+';PORT=1433;DATABASE='+keys.database+';UID='+keys.username+';PWD='+keys.password)
    return conn

# Gerar codigo para entrar em grupo
def generate_join_code(length=8):
    characters = string.ascii_letters + string.digits
    join_code = ''.join(secrets.choice(characters) for _ in range(length))
    return join_code

# Defesa contra SQL Injection 
def parse_input(user_input):
    special_characters = ["'", '"', ";", "--", "/*", "*/"]
    for char in special_characters:
        if char in user_input:
            user_input = user_input.replace(char, "")

# Rotas
@app.route('/')
def index():
    # Verifica se ha erro de login na sessao
    login_error = session.pop('login_error', None)
    return render_template('login.html', login_error=login_error)

@app.route('/login', methods=['POST'])
def login():
    if 'create_new_user' in request.form:
        return redirect(url_for('register'))
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
                return redirect(url_for('home'))
            else:
                session['login_error'] = 'Invalid username or password'
                return redirect(url_for('index'))
        else:
            session['login_error'] = 'Invalid username or password'
            return redirect(url_for('index'))

# Checagem de email com Kickbox
def is_email_address_valid(email):
    client = kickbox.Client(keys.api_key)
    kbx = client.kickbox()
    response = kbx.verify(email)
    return response.body['result'] != "undeliverable"

# Cadastro de usuario
@app.route('/register', methods=['GET', 'POST'])
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
                return redirect(url_for('index'))
            else:
                session['register_stats'] = 'Please enter a valid email!'
                return render_template('register.html', register_stats=register_stats)
    else:
        return render_template('register.html')

# Pagina principal
@app.route('/home')
def home():
    # Redirecionar se o usuario nao estiver logado
    if 'user' not in session:
        return redirect('/login')
    
    # Renderizar status do app
    join_stats = session.pop('join_stats', None)
    create_stats = session.pop('create_stats', None)
    group_stats = session.pop('group_stats', None)

    conn = connect_db()
    cur = conn.cursor()

    # Recuperar o ID do usuario atual
    cur.execute('SELECT id FROM "User" WHERE username = ?', (session['user'],))
    user_id = cur.fetchone()[0]

    # Esvaziar a lista de grupos
    groups = []

    # Recuperar os grupos associados ao usuario atual
    cur.execute('SELECT * FROM "Group" JOIN UserGroup ON "Group".id = UserGroup.group_id WHERE UserGroup.user_id = ?', (user_id,))
    groups = cur.fetchall()

    conn.close()
    return render_template('home.html', groups = groups, user_id = user_id, join_stats = join_stats, create_stats = create_stats, group_stats = group_stats)

# Criar um novo grupo
@app.route('/create_group', methods=['POST'])
def create_group():
    if request.method == 'POST':
        new_group_name = request.form['new_group_name']
        
        # Gerar um codigo de acesso aleatorio
        join_code = generate_join_code().lower()

        conn = connect_db()
        cur = conn.cursor()
        
        try:
            # Inserir novo grupo no banco de dados com o codigo gerado
            cur.execute('INSERT INTO "Group" (name, join_code) VALUES (?, ?)', (new_group_name, join_code))

            # Recuperar o ID do grupo
            cur.execute('SELECT @@IDENTITY')
            group_id = cur.fetchone()[0]

            # Inserir o usuario atual no grupo
            if 'user' in session:
                # Recuperar o ID do usuario atual
                cur.execute('SELECT id FROM "User" WHERE username = ?', (session['user'],))
                user_id = cur.fetchone()[0]
                cur.execute('INSERT INTO "UserGroup" (user_id, group_id) VALUES (?, ?)', (user_id, group_id))

            conn.commit()
            conn.close()
            session['create_stats'] = f'Group created successfully! Join code: {join_code}'
            return redirect(url_for('home'))
        except Exception as e:
            conn.rollback()
            session['create_stats'] = f'Error creating group: {str(e)}'
            return redirect(url_for('home'))
        
# Entrar em um grupo
@app.route('/join_group', methods=['POST'])
def join_group():
    group_code = request.form['group_code'].lower()

    conn = connect_db()
    cur = conn.cursor()

    # Encontrar o grupo com o codigo fornecido
    cur.execute('SELECT * FROM "Group" WHERE join_code = ?', (group_code,))
    group = cur.fetchone()

    if group:
        username = session['user']
        cur.execute('SELECT * FROM "User" WHERE username = ?', (username,))
        user = cur.fetchone()
        
        cur.execute('SELECT * FROM "UserGroup" WHERE user_id = ? AND group_id = ?', (user[0], group[0]))
        UserGroup = cur.fetchone()

        # Verificar se o usuario ja pertence ao grupo
        if UserGroup:
            conn.close()
            session['join_stats'] = 'Already a member of this group!'
            return redirect(url_for('home'))
        else:
            # Adicionar o usuario ao grupo
            cur.execute('INSERT INTO "UserGroup" (user_id, group_id) VALUES (?, ?)', (user[0], group[0]))
            conn.commit()
            conn.close()
            session['join_stats'] = 'Successfully joined the group!'
            return redirect(url_for('home')) 
    else:
        # Se o grupo com o codigo fornecido nao existir, redirecione de volta para a pagina inicial
        conn.close()
        session['join_stats'] = 'Group not found!'
        return redirect(url_for('home')) 

# Sair de um grupo 
@app.route('/exit_group', methods=['POST'])
def exit_group():
    if request.method == 'POST':
        group_id = request.form['group_id']
        user_id = request.form['user_id']

        try:
            conn = connect_db()
            cur = conn.cursor()

            # Deletar o usuario
            cur.execute('DELETE FROM UserGroup WHERE group_id = ? AND user_id = ?', (group_id, user_id))
            conn.commit()
            conn.close()

            return redirect(url_for('home'))
        except Exception as e:
            session['group_stats'] = f'Error removing user from group: {str(e)}'
            return redirect(url_for('home')) 

# Entrar no grupo para enviar mensagens
@app.route('/chat/<int:group_id>')
def chat(group_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM Message WHERE group_id = ? ORDER BY id', (group_id,))
   
    messages = cur.fetchall()

    conn.close()
    return render_template('chat.html', group_id=group_id, messages=messages)

# Enviar mensagem
@app.route('/send_message', methods=['POST'])
def send_message():
    # Verificar se o usuario esta logado
    if 'user' not in session:
        return redirect('/login')

    # Extrair o conteudo da mensagem e o ID do grupo do formulario
    message_content = request.form.get('message')
    group_id = request.form['group_id']
    timestamp = datetime.datetime.now()

    conn = connect_db()
    cur = conn.cursor()
    
    #Para o caso do usuario clicar sem querer em enviar com o campo vazio
    if message_content is not None and message_content.strip():
        # Inserir a mensagem no banco de dados
        cur.execute('INSERT INTO Message (content, group_id, timestamp) VALUES (?, ?, ?)', (message_content, group_id, timestamp))
        conn.commit()
        # Fechar a conexao com o banco de dados
        conn.close()

    # Redirecionar de volta para a pagina do chat
    return redirect(f'/chat/{group_id}')

# Fazer Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# Funcao principal
if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0', port=5000)