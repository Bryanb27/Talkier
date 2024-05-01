from flask import Flask
from flask_socketio import SocketIO
import keys
from auth import auth_bp
from groups import groups_bp
from chat import chat_bp

app = Flask(__name__)
app.secret_key = keys.secret_key
socketio = SocketIO(app)

# Registro dos Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(chat_bp) 


# Funcao principal
if __name__ == '__main__':
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True, host='localhost', port=5000)
    #socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0', port=5000)