# python -m venv .venv
#
# source .venv/bin/activate
#
# pip install Flask
# pip install Flask-BasicAuth
#
# python main.py

from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth
import json

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'taiga'
app.config['BASIC_AUTH_PASSWORD'] = 'secret'

basic_auth = BasicAuth(app)

# Load JSON data (replace 'large_data.json' with the path to your JSON file)
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

data = load_json('taiga-dump.json')

# Utility function for pagination
def paginate(data, page, page_size):
    start = (page - 1) * page_size
    end = start + page_size
    return data[start:end]

# Endpoint for issues
@app.route('/issues', methods=['GET'])
@basic_auth.required
def get_issues():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    issues = data.get('issues', [])
    
    paginated_issues = paginate(issues, page, page_size)
    
    return jsonify({
        'page': page,
        'page_size': page_size,
        'total_items': len(issues),
        'total_pages': (len(issues) + page_size - 1) // page_size,
        'data': paginated_issues
    })

# Endpoint for user stories
@app.route('/user-stories', methods=['GET'])
@basic_auth.required
def get_user_stories():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    user_stories = data.get('user_stories', [])
    
    paginated_user_stories = paginate(user_stories, page, page_size)
    
    return jsonify({
        'page': page,
        'page_size': page_size,
        'total_items': len(user_stories),
        'total_pages': (len(user_stories) + page_size - 1) // page_size,
        'data': paginated_user_stories
    })

# Endpoint for tasks
@app.route('/tasks', methods=['GET'])
@basic_auth.required
def get_tasks():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    tasks = data.get('tasks', [])
    
    paginated_tasks = paginate(tasks, page, page_size)
    
    return jsonify({
        'page': page,
        'page_size': page_size,
        'total_items': len(tasks),
        'total_pages': (len(tasks) + page_size - 1) // page_size,
        'data': paginated_tasks
    })

# Endpoint for epics
@app.route('/epics', methods=['GET'])
@basic_auth.required
def get_epics():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    epics = data.get('epics', [])
    
    paginated_epics = paginate(epics, page, page_size)
    
    return jsonify({
        'page': page,
        'page_size': page_size,
        'total_items': len(epics),
        'total_pages': (len(epics) + page_size - 1) // page_size,
        'data': paginated_epics
    })

# Endpoint for users
@app.route('/users', methods=['GET'])
@basic_auth.required
def get_users():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    memberships = data.get('memberships', [])
    
    return jsonify({
        'total_items': len(memberships),
        'data': memberships
    })

# Endpoint for status (total count of each entity)
@app.route('/status', methods=['GET'])
@basic_auth.required
def get_status():
    # Calculate the total number of each entity
    total_issues = len(data.get('issues', []))
    total_user_stories = len(data.get('user_stories', []))
    total_tasks = len(data.get('tasks', []))
    total_epics = len(data.get('epics', []))
    
    # Return the counts in a JSON response
    return jsonify({
        'total_issues': total_issues,
        'total_user_stories': total_user_stories,
        'total_tasks': total_tasks,
        'total_epics': total_epics
    })

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8888)