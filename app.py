from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

class Order(db.Model):
    __tablename__ = 'orders'  

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, nullable=False)  
    user_id = db.Column(db.Integer, nullable=False)  
    status = db.Column(db.Enum('pending', 'completed', 'canceled'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')

#
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('update_order')
def handle_order_update(data):
    order_id = data['order_id']
    new_status = data['status']
    
    
    order = Order.query.get(order_id)
    if order:
        order.status = new_status
        db.session.commit()
        
        
        socketio.emit('order_status_update', {'order_id': order_id, 'status': new_status})

if __name__ == '__main__':
    socketio.run(app)