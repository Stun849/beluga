from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
# ระบบสตรีมมิ่งข้อมูล Real-time ความเร็วสูงผ่าน WebSockets
socketio = SocketIO(app, cors_allowed_origins="*")

# ฐานข้อมูลและสิทธิ์เข้าถึง (อัปเดตรหัสลับใหม่ตามคำสั่ง)
ACCOUNTS = {
    "admin": {"pass": "1234", "role": "user"},
    "stun": {"pass": "nice_tryh@h@h@", "role": "admin"},
    "player1": {"pass": "tetris", "role": "user"}
}

GAMES = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('login')
def on_login(data):
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    if username in ACCOUNTS and ACCOUNTS[username]['pass'] == password:
        role = ACCOUNTS[username]['role']
        
        # จำลองข้อมูลการขุดแต่งแร่ (Stats) ในอวกาศสำหรับ User Dashboard
        user_stats = {'matches': 84, 'win_rate': '89%', 'skins': 12}
        
        # 🔐 กฎพิเศษ: ถ้าเป็น ADMIN จะได้รับสิทธิ์และเข้าถึงข้อมูลของ USER ได้ด้วยทันที!
        emit('login_success', {
            'username': username,
            'role': role,
            'stats': user_stats # แอดมินสามารถดึงแผงข้อมูลผู้เล่นไปทดสอบระบบได้เช่นกัน
        })
        print(f"[SPACE-AUTH] '{username}' logged in successfully as [{role.upper()}]")
    else:
        emit('error_message', {'msg': 'Baka Transmission Error: Invalid ID or Password!'})

@socketio.on('create_room')
def on_create(data):
    host_name = data.get('name', 'CosmoHost')
    role = data.get('role', 'guest')
    game_mode = data.get('mode', 'versus')
    
    if role == 'guest':
        emit('error_message', {'msg': 'Access Denied: Ghost profiles cannot host space sectors!'})
        return
        
    room_pin = str(random.randint(100000, 999999))
    GAMES[room_pin] = {
        'host': host_name,
        'mode': game_mode,
        'players': {request.sid: {'name': host_name, 'score': 0, 'alive': True}}
    }
    
    join_room(room_pin)
    emit('room_created', {'pin': room_pin, 'mode': game_mode})
    update_admin_galaxy_stats()

@socketio.on('admin_nuke_room')
def on_nuke(data):
    room_pin = data.get('pin')
    if room_pin in GAMES:
        del GAMES[room_pin]
        emit('room_nuked_by_admin', {}, to=room_pin)
        update_admin_galaxy_stats()
        print(f"[💥 GALAXY NUKE] Admin vaporized space sector {room_pin}!")

def update_admin_galaxy_stats():
    active_rooms = [{'pin': pin, 'host': details['host'], 'mode': details['mode'], 'players': len(details['players'])} for pin, details in GAMES.items()]
    socketio.emit('admin_update_stats', {'rooms': active_rooms})

if __name__ == '__main__':
    import os
    # บังคับให้ระบบดึงค่าพอร์ตสากลประจำเครื่องโฮสติ้งมาเปิดทำงานอัตโนมัติ
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)

