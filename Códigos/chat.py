from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import datetime
from keys import connect_db

chat_bp = Blueprint('chat', __name__)

# Entrar no grupo para enviar mensagens
@chat_bp.route('/chat/<int:group_id>')
def chat(group_id):
    # Verificar se o usuario esta logado
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM "Group" WHERE id = ?', (group_id,))
    group_traits = cur.fetchone()
    group_limit = group_traits[5]
    active_users = group_traits[6]
    
    if active_users < group_limit:
        # Quando um usuario entra em um grupo
        cur.execute('UPDATE "Group" SET active_users = active_users + 1 WHERE id = ?', (group_id,))
        #Setar para online no chat
        cur.execute('UPDATE [User] SET isActive = ? WHERE username = ?', (True, session['user']))
        conn.commit()
        conn.close()
        return render_template('chat.html', group_id=group_id, group_code=group_traits[4], group_name=group_traits[2], group_details=group_traits[3])
    else:
        return redirect(url_for('groups.home'))
        

# Executar agora atualizacao independente de ter enviado mensagem
@chat_bp.route('/fetch_messages/<int:group_id>')
def fetch_messages(group_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM Message WHERE group_id = ? ORDER BY id', (group_id,))
    messages = cur.fetchall()

    conn.close()

    # Formatar as mensagens em HTML
    html_messages = ''
    for message in messages:
        message_text = message[1]
        if len(message_text) > 35:
            message_text = '<br>'.join([message_text[i:i+35] for i in range(0, len(message_text), 35)])
        if message[5] == session['user']:
            html_messages += '<li style="background-color: #008000; color: white;">'
            html_messages += '<span style="max-width: 50%; word-break: break-word;">' + '(' + message[5] + ')  ' +  message_text +'</span>'
            html_messages += '<span style="float: right;">' +message[2].strftime('%H:%M') +'</span>' 
            html_messages += '</li>'
        else:
            html_messages += '<li>'
            html_messages += '<span style="max-width: 50%; word-break: break-word;">' + '(' + message[5] + ')  ' +  message_text +'</span>'
            html_messages += '<span style="float: right;">' +message[2].strftime('%H:%M') +'</span>' 
            html_messages += '</li>'  

    return html_messages

# Enviar mensagem
@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    # Extrair o conteudo da mensagem e o ID do grupo do formulario
    group_id = request.form['group_id']
    message_content = request.form['messageText']
    timestamp = datetime.datetime.now()

    # Verificar se a mensagem nao esta vazia
    if message_content is None or not message_content.strip():
        return jsonify({'success': False, 'error': 'Empty message'})

    conn = connect_db()
    cur = conn.cursor()

    # Inserir a mensagem no banco de dados
    cur.execute("INSERT INTO Message (content, group_id, timestamp, sender_id, sender_name) VALUES (?, ?, ?, ?, ?)", ( message_content, group_id, timestamp, session['id'], session['user']))
    conn.commit()

    conn.close()

    return jsonify({'success': True})

# Rota para remover o usuario da lista de usuarios ativos
@chat_bp.route('/remove_user_from_active_list/<int:group_id>', methods=['POST'])
def remove_user_from_active_list(group_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE "Group" SET active_users = active_users - 1 WHERE id = ?', (group_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})