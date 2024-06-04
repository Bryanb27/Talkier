from flask import Blueprint, session, request, jsonify, redirect, url_for
from keys import connect_db
from groups import generate_join_code
import datetime

friends_bp = Blueprint('friends', __name__)

# Pesquisar por usuario
@friends_bp.route('/search-users')
def search_users():
    query = request.args.get('query', '').lower()

    # Conecta-se ao banco de dados
    conn = connect_db()
    cur = conn.cursor()

    # Executa a consulta para buscar usuario
    cur.execute('SELECT * FROM "User" WHERE username LIKE ?', ('%' + query + '%',))
    users = cur.fetchall()

    conn.close()

    # Dicionario JSON da lista de usuarios
    users_list = [{'id': user[0], 'name': user[1]} for user in users]
    
    return jsonify(users_list)

# Enviar convites
@friends_bp.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    user_id1 = session['id']  # ID do user que envia o convite
    user_id2 = request.json['user_id2']  # ID do user que recebera o convite

    conn = connect_db()
    cur = conn.cursor()

    timestamp = datetime.datetime.now()

    # Verifica se o convite ja foi enviado anteriormente
    existing_request = cur.execute('SELECT * FROM Friendship WHERE user_id1 = ? AND user_id2 = ?', (user_id1, user_id2)).fetchone()
    if existing_request:
        return redirect(url_for('groups.home'))

    # Insere o convite na tabela Friendship
    cur.execute('INSERT INTO Friendship (user_id1, user_id2, status_inv, created_at) VALUES (?, ?, ?, ?)', (user_id1, user_id2, 'pending', timestamp))
    conn.commit()
    conn.close()

    return redirect(url_for('groups.home'))

# Recuperar convites pendentes
@friends_bp.route('/pending_invitations')
def pending_invitations():
    user_id = session['id']

    conn = connect_db()
    cur = conn.cursor()

    cur.execute('''
        SELECT "User".username, Friendship.created_at, Friendship.user_id1, Friendship.user_id2, "User".username 
        FROM Friendship 
        JOIN "User" ON Friendship.user_id1 = "User".id 
        WHERE Friendship.user_id2 = ? AND Friendship.status_inv = 'pending'
    ''', (user_id,))
    invitations = cur.fetchall()
    
    conn.close()

    # Dicionario JSON da lista de convites
    invitations_list = [{'username': invite[0], 'created_at': invite[1], 'user_id1': invite[2], 'user_id2': invite[3]} for invite in invitations]
    
    return jsonify({'invitations': invitations_list})

# Responder ao request
@friends_bp.route('/respond_friend_request', methods=['POST'])
def respond_friend_request():
    user_id1 = request.json['user_id1']  # ID do usuario que enviou o convite
    user_id2 = request.json['user_id2']  # ID do usuario que recebeu o convite
    response = request.json['response']   

    conn = connect_db()
    cur = conn.cursor()

    # Verifica se o convite existe
    friend_request = cur.execute('SELECT * FROM Friendship WHERE user_id1 = ? AND user_id2 = ?', (user_id1, user_id2)).fetchone()
    if not friend_request:
        return jsonify({'message': 'Friend request not found'}), 404

    # Atualiza o status do convite
    cur.execute('UPDATE Friendship SET status_inv = ? WHERE user_id1 = ? AND user_id2 = ?', (response, user_id1, user_id2))
    cur.commit()

    # Se a resposta for aceita, cria automaticamente um grupo para conversa entre os usuarios
    if response == 'accepted':
        create_group_for_friends(user_id1, user_id2, conn)

    conn.close()

    return redirect(url_for('groups.home'))

# Funcao para criar um grupo entre dois amigos
def create_group_for_friends(user_id1, user_id2, conn):
    cur = conn.cursor()

    # Recupera os detalhes dos usuarios
    cur.execute('SELECT username FROM "User" WHERE id = ?', (user_id1,))
    username1 = cur.fetchone()[0]
    cur.execute('SELECT username FROM "User" WHERE id = ?', (user_id2,))
    username2 = cur.fetchone()[0]

    group_name = f'{username1}_{username2}'
    group_details = 'Direct communication group'

    join_code = generate_join_code().lower()

    cur.execute('INSERT INTO "Group" (administer, groupName, details, join_code, p_limit) VALUES (?, ?, ?, ?, ?)', (user_id1, group_name, group_details, join_code, 2))

    cur.execute('SELECT @@IDENTITY')
    group_id = cur.fetchone()[0]

    # Insere os usuarios no grupo
    cur.execute('INSERT INTO UserGroup (user_id, group_id) VALUES (?, ?)', (user_id1, group_id))
    cur.execute('INSERT INTO UserGroup (user_id, group_id) VALUES (?, ?)', (user_id2, group_id))

    conn.commit()

# Printar lista de amigos
@friends_bp.route('/friends_list')
def friends_list():
    user_id = session['id']

    conn = connect_db()
    cur = conn.cursor()

    # Seleciona todos os amigos do usuario atual
    cur.execute('''
    SELECT u.username, u.isActive
    FROM Friendship f
    JOIN "User" u ON (f.user_id1 = u.id OR f.user_id2 = u.id) AND u.id != ?
    WHERE (f.user_id1 = ? OR f.user_id2 = ?) AND f.status_inv = 'accepted'
    ''', (user_id, user_id, user_id))
    friends = cur.fetchall()

    conn.close()

    # Dicionario JSON da lista de amigos
    friends_list = [{'username': friend[0], 'isActive': bool(friend[1])} for friend in friends]

    return jsonify({'friends': friends_list})
