#!/usr/bin/env python3
"""
Test demo session functionality without requiring PyTorch
"""
import requests
import time
import json

API_URL = "http://localhost:5000/api"

def test_demo_session():
    """Test creating and monitoring a demo session"""
    print("Testing demo session functionality...")
    
    # Create a demo session
    session_data = {
        "task": "Test demo iteration loop",
        "project": "radeonsi",
        "max_iterations": 3,
        "demo_mode": True
    }
    
    print("\n1. Creating demo session...")
    response = requests.post(f"{API_URL}/sessions", json=session_data)
    result = response.json()
    
    if result['status'] != 'success':
        print(f"❌ Failed to create session: {result.get('message')}")
        return False
    
    print(f"✓ Session created: {result['session_id']}")
    print(f"  Demo mode: {result.get('demo_mode', False)}")
    
    session_id = result['session_id']
    
    # Monitor session progress
    print("\n2. Monitoring session progress...")
    for i in range(10):
        time.sleep(2)
        
        # Check iteration status
        response = requests.get(f"{API_URL}/iteration/status")
        status = response.json()
        
        if status['status'] in ['running', 'idle']:
            current = status.get('current_iteration', 0)
            total = status.get('total_iterations', 0)
            phase = status.get('current_phase', 'unknown')
            
            print(f"  Iteration {current}/{total} - Phase: {phase}")
        
        # Check agent status
        response = requests.get(f"{API_URL}/agents/status")
        agents = response.json()
        
        if agents['total_active'] > 0:
            print(f"  Active agents: {agents['total_active']}")
            for agent in agents['agents']:
                print(f"    - {agent['name']}: {agent['phase']}")
        
        # Check if completed
        if status.get('current_phase') == 'completed':
            print("\n✓ Session completed!")
            break
    
    # Verify session is listed
    print("\n3. Verifying session list...")
    response = requests.get(f"{API_URL}/sessions")
    sessions = response.json()
    
    found = False
    for session in sessions.get('sessions', []):
        if session['id'] == session_id:
            found = True
            print(f"✓ Session found in list:")
            print(f"  Status: {session['status']}")
            print(f"  Task: {session['task']}")
    
    if not found:
        print("❌ Session not found in list")
        return False
    
    print("\n✅ All tests passed!")
    return True

if __name__ == '__main__':
    try:
        test_demo_session()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to UI. Please start it with: cd ui && python app.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
