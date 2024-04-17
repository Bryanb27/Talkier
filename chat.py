from flask import Blueprint, render_template, request, session, redirect
import datetime
from keys import connect_db

chat_bp = Blueprint('chat', __name__)

# Entrar no grupo para enviar mensagens
@chat_bp.route('/chat/<int:group_id>')
def chat(group_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM Message WHERE group_id = ? ORDER BY id', (group_id,))
   
    messages = cur.fetchall()

    conn.close()
    return render_template('chat.html', group_id=group_id, messages=messages)

# Enviar mensagem
@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    # Verificar se o usuario esta logado
    if 'user' not in session:
        return redirect('auth.login')

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