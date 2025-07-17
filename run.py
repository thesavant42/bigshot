# Flask application factory and core API
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use SocketIO's run method for WebSocket support
    app.socketio.run(app, debug=True, host='0.0.0.0', port=5000)