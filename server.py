import os
import urllib.request
from my_constants import app, sio
import pyAesCrypt
from flask import Flask, flash, request, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
# from flask_socketio import SocketIO, send, emit
# from "web3.storage" import Web3Storage
from web3storage import Client

# from utils import send_offer_and_icecandidate, create_peer_connection
import socket
import pickle
from blockchain import Blockchain
import requests

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

# The package requests is used in the 'hash_user_file' and 'retrieve_from hash' functions to send http post requests.
# Notice that 'requests' is different than the package 'request'.
# 'request' package is used in the 'add_file' function for multiple actions.

client_ip = app.config['ADDR']
connection_status = False

peer_connections = {}
blockchain = Blockchain()

async def replace_chain():
        network = blockchain.nodes
        print("network")
        longest_chain = None
        initial = len(blockchain.chain)
        response = requests.get(f'{app.config["SERVER_IP"]}/get_chain')
        
        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']
            if length > initial and blockchain.is_chain_valid(chain):
                blockchain.chain = chain



        # network = self.nodes
        # initial = len(self.chain)
        def call_back(data):
                length = data.get('length')
                max_length = len(blockchain.chain)
                chain = data.get('chain')
                print("from ch",chain)
                if length > max_length and blockchain.is_chain_valid(chain):
                    blockchain.chain = chain
        
        
        for node in network:
            print("insidenode")
            await send_offer_and_icecandidate(node, call_back)

        if initial < len(blockchain.chain):
            return True
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def append_file_extension(uploaded_file, file_path):
    file_extension = uploaded_file.filename.rsplit('.', 1)[1].lower()
    user_file = open(file_path, 'a')
    user_file.write('\n' + file_extension)
    user_file.close()

def decrypt_file(file_path, file_key):
    encrypted_file = file_path + ".aes"
    print("decr", encrypted_file)
    os.rename(file_path, encrypted_file)
    pyAesCrypt.decryptFile(encrypted_file, file_path,  file_key, app.config['BUFFER_SIZE'])

def encrypt_file(file_path, file_key):
    pyAesCrypt.encryptFile(file_path, file_path + ".aes",  file_key, app.config['BUFFER_SIZE'])

def hash_user_file(user_file, file_key):
    encrypt_file(user_file, file_key)
    encrypted_file_path = user_file + ".aes"
    # client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    client = Client(api_key = app.config['KEY'] )
    response = client.upload_file(encrypted_file_path)
    file_hash = response['cid']
    return file_hash

def retrieve_from_hash(file_hash, file_key):
    # client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    # client = Client(api_key= app.config['KEY'] )
    # # file_content = bytes.fromhex(file_hex)
    # client.download(file_hash)
    response = requests.get(f'https://{file_hash}.ipfs.dweb.link') # add error handelling
    file_content = response.content

    # print(file_content)
    file_path = os.path.join("./downloads",file_hash) 

    # print("file-content: ",file_content)

    user_file = open(file_path, 'wb')
    user_file.write(file_content)
    user_file.close()
    print("inside line 62", file_path)
    decrypt_file(file_path, file_key)
    print("inside line 64", file_path)
    with open(file_path, 'rb') as f:
        lines = f.read().splitlines()
        last_line = lines[-1]
    user_file.close()
    file_extension = last_line
    saved_file = file_path + '.' + file_extension.decode()
    os.rename(file_path, saved_file)
    print("save-file",saved_file)
    return saved_file
    # return file_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html' , message = "Welcome!")

@app.route('/download')
def download():
    return render_template('download.html' , message = "Welcome!")

@app.route('/add_file', methods=['POST'])
async def add_file():
    
    is_chain_replaced = await replace_chain()

    if is_chain_replaced:
        print('The nodes had different chains so the chain was replaced by the longest one.')
    else:
        print('All good. The chain is the largest one.')

    if request.method == 'POST':
        error_flag = True
        if 'file' not in request.files:
            message = 'No file part'
        else:
            user_file = request.files['file']
            if user_file.filename == '':
                message = 'No file selected for uploading'

            if user_file and allowed_file(user_file.filename):
                error_flag = False
                filename = secure_filename(user_file.filename)
                # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_path = os.path.join("./uploads", filename)
                print(file_path)
                user_file.save(file_path)
                append_file_extension(user_file, file_path)
                sender = request.form['sender_name']
                receiver = request.form['receiver_name']
                file_key = request.form['file_key']
                try:
                    hashed_output1 = hash_user_file(file_path, file_key)
                    index = blockchain.add_file(sender, receiver, hashed_output1)
                except Exception as err:
                    message = str(err)
                    error_flag = True
                    if "ConnectionError:" in message:
                        message = "Gateway down or bad Internet!"
                # message = f'File successfully uploaded'
                # message2 =  f'It will be added to Block {index-1}'
            else:
                error_flag = True
                message = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'
    
        if error_flag == True:
            return render_template('upload.html' , message = message)
        else:
            return render_template('upload.html' , message = "File succesfully uploaded")

@app.route('/retrieve_file', methods=['POST'])
async def retrieve_file():

    is_chain_replaced = await replace_chain()

    if is_chain_replaced:
        print('The nodes had different chains so the chain was replaced by the longest one.')
    else:
        print('All good. The chain is the largest one.')

    if request.method == 'POST':

        error_flag = True

        if request.form['file_hash'] == '':
            message = 'No file hash entered.'
        elif request.form['file_key'] == '':
            message = 'No file key entered.'
        else:
            error_flag = False
            file_key = request.form['file_key']
            file_hash = request.form['file_hash']
            try:
                file_path = retrieve_from_hash(file_hash, file_key)
            except Exception as err:
                message = str(err)
                error_flag = True
                if "ConnectionError:" in message:
                    message = "Gateway down or bad Internet!"

        if error_flag == True:
            return render_template('download.html' , message = message)
        else:
            return render_template('download.html' , message = "File successfully downloaded")


async def send_offer_and_icecandidate(peer_id, call_back):
    pc = await create_peer_connection(peer_id, call_back)

    channel = pc.createDataChannel("my-channel")
    # channel.send({"type": "getChain"})
    # Create offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    sio.emit("message", {"event" : "offer", "payload" : {"sdp": offer.sdp, "type": offer.type}, "peerId": peer_id} )

async def create_peer_connection(peer_id, call_back):
    pc = RTCPeerConnection()

    # peer_connections[peer_id] = pc

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        async def on_message(message):
            print(f"Received msg: {message}")
            msg = message.get("type")
            print("message type", msg)
            if msg == "getChain":
                channel.send({"type": "chain", "data": {'chain': blockchain.chain, 'length': len(blockchain.chain)} })
            elif msg == "chain":
                print(f"Received data: {message.get('data')}")
                call_back(message.get('data'))

    

    # Generate and send ICE candidates
    @pc.on("icecandidate")
    def on_icecandidate(candidate):
        if candidate:
            print("icecandidate")
            sio.emit("message", {"event":"ice-candidate","payload": candidate.to_sdp(), "peerId": peer_id})
        else:
            print("ICE Gathering Complete")

    
    # # Wait for ICE gathering to complete
    # pc.gather_candidates()

    peer_connections[peer_id] = pc
    return pc


@sio.on("connect")
def connect():
    print("Connected to signaling server")

@sio.on("disconnect")
def disconnect():
    print("disconnected from signaling server")

@sio.on("offer")
def offer(data):
    peer_id = data["peerId"]
    peer_connection = create_peer_connection(peer_id)

    peer_connection.setRemoteDescription(RTCSessionDescription(sdp=data["offer"]["sdp"], type=data["offer"]["type"]))
    print("offer")
    # Create an answer
    answer = peer_connection.createAnswer()
    peer_connection.setLocalDescription(answer)
    
    sio.emit("message", {"event":"answer",  "payload": {"sdp": answer.sdp, "type": answer.type}, "peerId": peer_id})

@sio.on("answer")
def answer(data):
    peer_id = data["peerId"]
    peer_connection = peer_connections.get(peer_id)
    print("answer",data)
    if peer_connection:
        peer_connection.setRemoteDescription(RTCSessionDescription(sdp=data["answer"]["sdp"], type=data["answer"]["type"]))

@sio.on("ice-candidate")
def ice_candidate(data):
    peer_id = data["peerId"]
    peer_connection = peer_connections.get(peer_id)
    print("on icecandi",data)
    if peer_connection:
        ice_candidate = RTCIceCandidate(sdp=data["candidate"]["candidate"], sdpMid=data["candidate"]["sdpMid"], sdpMLineIndex=data["candidate"]["sdpMLineIndex"])
        peer_connection.addIceCandidate(ice_candidate)

@sio.on("my_response")
def my_response(message):
    print("message", message)
    print(pickle.loads(message['data']))
    blockchain.nodes = pickle.loads(message['data'])

@app.route('/connect_blockchain')
async def connect_blockchain():
    # print("sio:", sio.id)
    global connection_status
    nodes = len(blockchain.nodes)
    if connection_status is False:
       sio.connect(app.config['SERVER_IP'])
    # sio.wait()
    is_chain_replaced = await replace_chain()
    connection_status = True
    return render_template('connect_blockchain.html', messages = {'message1' : "Welcome to the services page",
                                                                  'message2' : "Congratulations , you are now connected to the blockchain.",
                                                                 } , chain = blockchain.chain, nodes = nodes)

@app.route('/disconnect_blockchain')
def disconnect_blockchain():
    global connection_status
    connection_status = False
    sio.disconnect()
    # sio.wait()
    
    return render_template('index.html')

@sio.on("get_chain")
def get_chain():
    print("getChain")
    # sio.emit("get_chain_response", {'chain': blockchain.chain, 'length': len(blockchain.chain)} )

if __name__ == '__main__':
    app.run(host = client_ip['Host'], port= client_ip['Port'], debug=True)
    # app.run(app.config['NODE_ADDR'], debug=True)