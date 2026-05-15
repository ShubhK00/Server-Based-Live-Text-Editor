import socketio
import eventlet

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

# Dictionary to store document content for each room
documents = {}

@sio.event
def connect(sid, environ):
    print(f"User Connected: {sid}")

@sio.event
def join_doc(sid, doc_id):
    sio.enter_room(sid, doc_id)
    # Send the current state of the document to the new user
    content = documents.get(doc_id, "")
    sio.emit('document_state', content, room=sid)
    print(f"User {sid} joined room: {doc_id}")

@sio.event
def edit_text(sid, data):
    doc_id = data['doc_id']
    content = data['content']
    documents[doc_id] = content
    # Broadcast the change to everyone else in the room
    sio.emit('update_text', content, room=doc_id, skip_sid=sid)

@sio.event
def disconnect(sid):
    print(f"User Disconnected: {sid}")

if __name__ == '__main__':
    print("Server running on http://localhost:5000")
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)