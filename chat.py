from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import datetime
from keys import connect_db
from auth import user_has_permission

chat_bp = Blueprint('chat', __name__)

# Entrar no grupo para enviar mensagens
@chat_bp.route('/chat/<int:group_id>')
def chat(group_id):
    # Verificar se o usuario esta logado
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    # Impedir URL injection
    if not user_has_permission(session['id'], group_id):
        return redirect(url_for('auth.index'))

    # Se o usuario estiver autenticado e tiver permissao
    return render_template('chat.html', group_id=group_id)

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
        html_messages += '<li>'
        html_messages += '<span>' +message[1] +'</span>'
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

    # Dividir a mensagem em partes de 70 caracteres pra quebrar linha
    message_parts = [message_content[i:i+70] for i in range(0, len(message_content), 70)]
    formatted_message = '\n'.join(message_parts)

    # Inserir a mensagem no banco de dados
    cur.execute("INSERT INTO Message (content, group_id, timestamp) VALUES (?, ?, ?)", ( formatted_message, group_id, timestamp))
    conn.commit()

    conn.close()

    return jsonify({'success': True})