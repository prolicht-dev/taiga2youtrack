# python -m venv .venv
#
# source .venv/bin/activate
#
# pip install Flask
# pip install Flask-BasicAuth
#
# python main.py

import math
from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth
import json
import logging

# constants
ISSUE = "issues"
EPIC = "epics"
TASK = "tasks"
STORY = "user_stories"

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'taiga'
app.config['BASIC_AUTH_PASSWORD'] = 'secret'

logging.basicConfig(level=logging.DEBUG)
basic_auth = BasicAuth(app)

# Load JSON data (replace "large_data.json" with the path to your JSON file)
def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

data = load_json("taiga-dump.json")

# total counts
total_counts = {
    ISSUE: len(data.get("issues", [])),
    EPIC: len(data.get("epics", [])),
    STORY: len(data.get("user_stories", [])),
    TASK: len(data.get("tasks", []))
}

sum_totals = total_counts[ISSUE] + total_counts[EPIC] + total_counts[STORY] + total_counts[TASK]

types_in_order = [ISSUE, TASK, STORY, EPIC]

# Endpoint for issues
@app.route("/issues", methods=["GET"])
@basic_auth.required
def get_issues():
    skip = int(request.args.get("skip", 1))
    page_size = int(request.args.get("page_size", 10))
  
    if skip < 0:
        logging.error("could not return pagingated issues with skip size < 0. size: %d", skip)
        return jsonify("could not return issues wirth empty skip")
    
    if skip > sum_totals or skip > sum_totals:
        logging.error("requested more issues than totally available")
        return jsonify("requested more issues than totally available")
    
    if page_size < 0:
        logging.error("could not return pagingated issues with page size < 0. size: %d", page_size)
        return jsonify("could not return issues with empty page_size")

    result = {}
    remaining = page_size
    current_skip = skip
    total_items = 0
    for issue_type in types_in_order:
        total = total_counts[issue_type]
        if current_skip >= total:
            current_skip -= total
            continue

        # Determine how many we can fetch for this type
        fetch_count = min(total - current_skip, remaining)
        data_array = data.get(issue_type, [])
        paginated = paginate(data_array, current_skip, fetch_count)

        # Track initialized count
        remaining -= len(paginated)
        current_skip = 0  # only skip the first type

        # Add to response if any issues returned
        if paginated:
            result[issue_type] = paginated
            total_items += len(paginated)

        # Stop if we reached our limit
        if remaining <= 0:
            break

    json = jsonify(result)
    logging.info("returned empty ids: %s", json)    
    logging.info("sum_totals: %d, page_size: %d, pages: %d", sum_totals, page_size, sum_totals/page_size)
    return jsonify({
        "skip": skip,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": math.ceil(sum_totals/page_size),
        "data": result
    })

# Endpoint for users
@app.route("/users", methods=["GET"])
@basic_auth.required
def get_users():    
    memberships = data.get("memberships", [])
    
    return jsonify({
        "total_items": len(memberships),
        "data": memberships
    })

# Endpoint for status (total count of each entity)
@app.route("/status", methods=["GET"])
@basic_auth.required
def get_status():    
    # Return the counts in a JSON response
    return jsonify({
        "total_issues": total_counts.get(ISSUE),
        "total_user_stories": total_counts.get(STORY),
        "total_tasks": total_counts.get(TASK),
        "total_epics": total_counts.get(EPIC)
    })

# Endpoint for create empty issues. After calling this all ids are guranteed to be available
# empty issues are not supposed to be linked yet, this has to be done at a later stage
@app.route("/getIdsByType", methods=["GET"])
@basic_auth.required
def get_getIdsByType():
    skip = int(request.args.get("skip", 1))
    page_size = int(request.args.get("page_size", 10))
    
    if skip < 0:
        logging.error("could not return pagingated issues with skip size < 0. size: %d", skip)
        return jsonify("could not return issues wirth empty skip")
    
    if skip > sum_totals or skip > sum_totals:
        logging.error("requested more issues than totally available")
        return jsonify("requested more issues than totally available")
    
    if page_size < 0:
        logging.error("could not return pagingated issues with page size < 0. size: %d", page_size)
        return jsonify("could not return issues with empty page_size")

    result = {}
    remaining = page_size
    current_skip = skip
    total_items = 0
    for issue_type in types_in_order:
        total = total_counts[issue_type]
        if current_skip >= total:
            current_skip -= total
            continue

        # Determine how many we can fetch for this type
        fetch_count = min(total - current_skip, remaining)
        data_array = data.get(issue_type, [])
        paginated = paginate(data_array, current_skip, fetch_count)
        if paginated is None:
            logging.error("can not get ids of empty paginate")
            return []
        ids = getIds(paginated)

        # Track initialized count
        remaining -= len(ids)
        current_skip = 0  # only skip the first type

        # Add to response if any ids returned
        if ids:
            result[issue_type] = ids
            total_items += len(paginated)

        # Stop if we reached our limit
        if remaining <= 0:
            break

    json = jsonify(result)
    logging.info("returned empty ids: %s", json)
    return jsonify({
        "skip": skip,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": math.ceil(sum_totals/page_size),
        "data": result
    })
    
# Utility function for pagination
def paginate(data, skip, page_size):
    start = skip
    end = start + page_size
    return data[start:end]

# gets all ids from the data array
def getIds(data):
    ids = []
    for issue in data:
       if type(issue) != dict:
           logging.error("did not provide a dict for issue")
           continue
       ids.append(issue["ref"])
    return ids        

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=8888)