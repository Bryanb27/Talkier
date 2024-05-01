from flask import Blueprint, render_template, request, session, redirect, url_for
import secrets
import string
from keys import connect_db

groups_bp = Blueprint('groups', __name__)

# Gerar codigo para entrar em grupo
def generate_join_code(length=8):
    characters = string.ascii_letters + string.digits
    join_code = ''.join(secrets.choice(characters) for _ in range(length))
    return join_code

# Pagina principal
@groups_bp.route('/home')
def home():
    # Redirecionar se o usuario nao estiver logado
    if 'user' not in session:
        return redirect('auth.login')
    
    # Renderizar status do groups_bp
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
@groups_bp.route('/create_group', methods=['POST'])
def create_group():
    if request.method == 'POST':
        new_group_name = request.form['new_group_name']
        group_details  = request.form['group_details']
        
        # Gerar um codigo de acesso aleatorio
        join_code = generate_join_code().lower()

        conn = connect_db()
        cur = conn.cursor()
        
        try:
            # Inserir novo grupo no banco de dados com o codigo gerado
            cur.execute('INSERT INTO "Group" (administer, groupName, details, join_code) VALUES (?, ?, ?, ?)', (session['id'], new_group_name, group_details, join_code))

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
            return redirect(url_for('groups.home'))
        except Exception as e:
            conn.rollback()
            session['create_stats'] = f'Error creating group: {str(e)}'
            return redirect(url_for('groups.home'))
        
# Entrar em um grupo
@groups_bp.route('/join_group', methods=['POST'])
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
            return redirect(url_for('groups.home'))
        else:
            # Adicionar o usuario ao grupo
            cur.execute('INSERT INTO "UserGroup" (user_id, group_id) VALUES (?, ?)', (user[0], group[0]))
            conn.commit()
            conn.close()
            session['join_stats'] = 'Successfully joined the group!'
            return redirect(url_for('groups.home')) 
    else:
        # Se o grupo com o codigo fornecido nao existir, redirecione de volta para a pagina inicial
        conn.close()
        session['join_stats'] = 'Group not found!'
        return redirect(url_for('groups.home')) 

# Sair de um grupo 
@groups_bp.route('/exit_group', methods=['POST'])
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

            return redirect(url_for('groups.home'))
        except Exception as e:
            session['group_stats'] = f'Error removing user from group: {str(e)}'
            return redirect(url_for('groups.home'))