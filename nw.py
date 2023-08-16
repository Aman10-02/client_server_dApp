# import json
# # import asyncio
# import socketio
# from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

# sio = socketio.AsyncClient()

# # Dictionary to store peer connections
# peer_connections = {}

# async def send_offer_and_icecandidate(peer_id, call_back):
#     pc = create_peer_connection(peer_id, call_back)

#     # Create offer
#     offer = await pc.createOffer()
#     await pc.setLocalDescription(offer)
#     await sio.emit("message", {"event" : "offer", "payload" : {"sdp": offer.sdp, "type": offer.type}, "peerId": peer_id} )

    

#     channel = pc.createDataChannel("my-channel")
#     await channel.send({"type": "getChain"})

# def create_peer_connection(peer_id, call_back):
#     pc = RTCPeerConnection()

#     # peer_connections[peer_id] = pc

#     @pc.on("datachannel")
#     def on_datachannel(channel):
#         @channel.on("message")
#         async def on_message(message):
#             print(f"Received msg: {message}")
#             msg = message.get("type")
#             if msg == "getChain":
#                 channel.send({"type": "chain", "data": {'chain': blockchain.chain, 'length': len(blockchain.chain)} })
#             elif msg == "chain":
#                 print(f"Received data: {message.get('data')}")
#                 call_back(message.get('data'))

    

#     # Generate and send ICE candidates
#     @pc.on("icecandidate")
#     async def on_icecandidate(candidate):
#         if candidate:
#             await sio.emit("message", {"event":"ice-candidate","payload": candidate.to_sdp(), "peerId": peer_id})
#         else:
#             print("ICE Gathering Complete")

    
#     # Wait for ICE gathering to complete
#     pc.gather_candidates()

#     peer_connections[peer_id] = pc
#     return pc


# @sio.on("connect")
# async def connect():
#     print("Connected to signaling server")

# @sio.on("offer")
# async def offer(data):
#     peer_id = data["peerId"]
#     peer_connection = create_peer_connection(peer_id)

#     await peer_connection.setRemoteDescription(RTCSessionDescription(sdp=data["offer"]["sdp"], type=data["offer"]["type"]))

#     # Create an answer
#     answer = await peer_connection.createAnswer()
#     await peer_connection.setLocalDescription(answer)
    
#     await sio.emit("message", {"event":"answer",  "payload": {"sdp": answer.sdp, "type": answer.type}, "peerId": peer_id})

# @sio.on("answer")
# async def answer(data):
#     peer_id = data["peerId"]
#     peer_connection = peer_connections.get(peer_id)
#     if peer_connection:
#         await peer_connection.setRemoteDescription(RTCSessionDescription(sdp=data["answer"]["sdp"], type=data["answer"]["type"]))

# @sio.on("ice-candidate")
# async def ice_candidate(data):
#     peer_id = data["peerId"]
#     peer_connection = peer_connections.get(peer_id)
#     if peer_connection:
#         ice_candidate = RTCIceCandidate(sdp=data["candidate"]["candidate"], sdpMid=data["candidate"]["sdpMid"], sdpMLineIndex=data["candidate"]["sdpMLineIndex"])
#         await peer_connection.addIceCandidate(ice_candidate)

# async def main():
#     await sio.connect('http://localhost:3000')
#     await sio.wait()

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
