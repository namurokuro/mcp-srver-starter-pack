"""
Agent Viewport Web Server
Flask server with WebSocket support for real-time agent activity visualization
"""

import json
import threading
import time
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from agent_activity_tracker import tracker
import sys
from typing import Dict, Any


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'agent-viewport-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Track connected clients
connected_clients = set()


def on_activity_update(data: Dict):
    """Callback for activity tracker updates"""
    socketio.emit('activity_update', data, broadcast=True, namespace='/')
    socketio.emit('update', data, broadcast=True, namespace='/')  # Generic update


@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('viewport.html')


@app.route('/api/dashboard')
def get_dashboard():
    """Get current dashboard data"""
    return jsonify(tracker.get_dashboard_data())


@app.route('/api/agents')
def get_agents():
    """Get all agent statuses"""
    return jsonify(tracker.get_all_agent_statuses())


@app.route('/api/activities')
def get_activities():
    """Get all current activities"""
    return jsonify(tracker.get_all_activities())


@app.route('/api/activities/<activity_id>')
def get_activity(activity_id: str):
    """Get a specific activity"""
    activities = tracker.get_all_activities()
    for activity in activities:
        if activity.get('activity_id') == activity_id:
            return jsonify(activity)
    return jsonify({"error": "Activity not found"}), 404


@app.route('/api/agents/<agent_name>')
def get_agent(agent_name: str):
    """Get status and activities for a specific agent"""
    status = tracker.get_agent_status(agent_name)
    activities = tracker.get_agent_activities(agent_name)
    
    if not status:
        return jsonify({"error": "Agent not found"}), 404
    
    return jsonify({
        "status": status,
        "activities": activities
    })


@app.route('/api/history')
def get_history():
    """Get activity history"""
    limit = 100
    try:
        limit = int(request.args.get('limit', 100))
    except:
        pass
    
    return jsonify(tracker.get_activity_history(limit=limit))


@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    statuses = tracker.get_all_agent_statuses()
    activities = tracker.get_all_activities()
    
    total_operations = sum(s.get('total_operations', 0) for s in statuses)
    successful_operations = sum(s.get('successful_operations', 0) for s in statuses)
    failed_operations = sum(s.get('failed_operations', 0) for s in statuses)
    
    active_agents = sum(1 for s in statuses if s.get('is_active', False))
    active_activities = len([a for a in activities if a.get('status') not in ['success', 'error', 'cancelled']])
    
    return jsonify({
        "total_agents": len(statuses),
        "active_agents": active_agents,
        "total_operations": total_operations,
        "successful_operations": successful_operations,
        "failed_operations": failed_operations,
        "active_activities": active_activities,
        "success_rate": (
            successful_operations / total_operations * 100
            if total_operations > 0 else 0
        )
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    connected_clients.add(request.sid)
    print(f"Client connected: {request.sid}. Total clients: {len(connected_clients)}", file=sys.stderr, flush=True)
    
    # Send current state to new client
    emit('dashboard_data', tracker.get_dashboard_data())
    emit('connected', {'message': 'Connected to agent viewport'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    connected_clients.discard(request.sid)
    print(f"Client disconnected: {request.sid}. Total clients: {len(connected_clients)}", file=sys.stderr, flush=True)


@socketio.on('request_update')
def handle_request_update():
    """Handle update request from client"""
    emit('dashboard_data', tracker.get_dashboard_data())


@socketio.on('subscribe_agent')
def handle_subscribe_agent(data):
    """Subscribe to updates for a specific agent"""
    agent_name = data.get('agent_name')
    if agent_name:
        emit('agent_data', {
            'status': tracker.get_agent_status(agent_name),
            'activities': tracker.get_agent_activities(agent_name)
        })


def start_viewport_server(host='localhost', port=5000, debug=False):
    """Start the viewport web server"""
    # Subscribe to activity tracker updates
    tracker.subscribe(on_activity_update)
    
    # Start background thread for periodic updates
    def periodic_updates():
        while True:
            time.sleep(5)  # Send periodic updates every 5 seconds
            if connected_clients:
                socketio.emit('heartbeat', {
                    'timestamp': time.time(),
                    'connected_clients': len(connected_clients)
                }, broadcast=True, namespace='/')
    
    update_thread = threading.Thread(target=periodic_updates, daemon=True)
    update_thread.start()
    
    print(f"\n{'='*60}", file=sys.stderr, flush=True)
    print(f"🚀 Agent Viewport Server Starting...", file=sys.stderr, flush=True)
    print(f"{'='*60}", file=sys.stderr, flush=True)
    print(f"📊 Dashboard URL: http://{host}:{port}", file=sys.stderr, flush=True)
    print(f"📡 WebSocket: ws://{host}:{port}", file=sys.stderr, flush=True)
    print(f"{'='*60}\n", file=sys.stderr, flush=True)
    
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Agent Viewport Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    start_viewport_server(host=args.host, port=args.port, debug=args.debug)

