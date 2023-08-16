from flask import Flask
import socketio

# from flask_socketio import SocketIO

UPLOAD_FOLDER = '/uploads'
DOWNLOAD_FOLDER = '/downloads'

sio = socketio.Client()
app = Flask(__name__)
# app.secret_key = "secret key"
app.config['KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDhGNWNmMjczYzY1YjQ0ZmFCNzMyOGUwM2U0YkZGNEQ5RTg4NEE5YjMiLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2OTE5MjU2NDI4ODQsIm5hbWUiOiJkZWNlbnRyYWxpemVkRmlsZVNoYXJlIn0.rf7Jv5bCAvr06If4AX5ptIfIOxD-2RUx6PnLeFNK0zk"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['SERVER_IP'] = 'https://4e84-14-139-196-13.ngrok-free.app'
# app.config['SERVER_IP'] = 'http://127.0.0.1:5111'
app.config['ADDR'] = {'Host' : '127.0.0.1', 'Port' : 5113}
app.config['NODE_ADDR'] = 'https://825b-14-139-196-13.ngrok-free.app'
# app.config['NODE_ADDR'] = {'Host' : '0.0.0.0', 'Port' : 5113}
app.config['BUFFER_SIZE'] = 64 * 1024
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024