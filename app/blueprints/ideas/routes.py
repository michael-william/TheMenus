from flask import request, render_template, redirect, url_for, Blueprint  # noqa: F401
import requests
from flask import jsonify
import os
from dotenv import load_dotenv

from app.blueprints.ideas.models import Ideas

# Define a base URL and API token for NocoDB
# Load the .env file
load_dotenv()

NOCO_DB_BASE_URL = os.getenv("NOCO_DB_BASE_URL")
NOCO_DB_TABLE_ID = os.getenv("NOCO_DB_IDEAS_TABLE_ID")  
NOCO_DB_API_TOKEN = os.getenv("NOCO_DB_API_TOKEN")  

headers = {
    "xc-token": NOCO_DB_API_TOKEN
}

ideas = Blueprint("ideas", __name__, template_folder='templates') 

def get_idea_by_id(idea_id):
    """Fetch a recipe by ID from the NoCoDB API."""
    # Use the table ID in the URL
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records/{idea_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return Ideas.from_api_data(data)
    else:
        print(f"Failed to fetch recipe with ID {idea_id}: {response.status_code}")
        return None

@ideas.route('/')
def index():
    # Make a request to NocoDB to get all recipes
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Convert API data to NoCoShop instances
        data = response.json().get("list", [])
        ideas = [Ideas.from_api_data(item) for item in data]
        return render_template('ideas/index.html', ideas=ideas)
    else:
        print(jsonify({"error": "Failed to retrieve recipes", "status_code": response.status_code}), response.status_code)
        return render_template('/index.html')

@ideas.route('/add_idea', methods=['GET','POST'])
def add_idea():
    return render_template('ideas/add_idea.html')

@ideas.route('/save_new_idea', methods=['POST'])
def save_new_idea():
    # Collect form data
    title = request.form.get('title')
    meal = request.form.get('meal')
    core = request.form.get('core')
    source = request.form.get('source')
    notes = request.form.get('notes')

    # Prepare the payload for creating a new record in NoCoDB
    payload = {
        "Title": title,
        "Meal": meal,
        "Core": core,
        "Source": source,
        "Notes": notes,
    }

    # Make the API request to NoCoDB to create a new record
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    headers_with_content_type = {**headers, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers_with_content_type, json=payload)

    if response.status_code == 200:
        print("Idea uploaded successfully.")
        # Optionally redirect or render the index page with updated data
        return redirect(url_for('ideas.index'))
    else:
        print(f"Failed to upload idea: {response.status_code} - {response.text}")
        # Render the add_idea template with an error message
        return render_template('ideas/add_idea.html', error="Failed to save the idea. Please try again.")
    
@ideas.route('/search', methods=['GET', 'POST'])
def search():
    # Get the 'search' query parameter from the request, split by whitespace to get each word
    query = request.args.get('idea-search', '').strip()
    words = query.lower().split()  # Split by space and convert to lowercase for case-insensitive search
    
    # Fetch all recipes from NoCo DB (you may later optimize this if NoCo supports more advanced filtering)
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("list", [])
        ideas = [Ideas.from_api_data(item) for item in data]
        
        # Filter recipes: check if any word is in any relevant field
        if words:
            idea_results = [
                idea for idea in ideas if all(
                    word in (idea.Title or '').lower() or
                    word in (idea.Meal or '').lower() or
                    word in (idea.Core or '').lower() or
                    word in (idea.Source or '').lower()
                    for word in words
                )
            ]
        else:
            idea_results = ideas  # No search query, return all recipes

        return render_template('ideas/search.html', idea_results=idea_results)
    else:
        return jsonify({"error": "Failed to retrieve ideas", "status_code": response.status_code}), response.status_code
    
@ideas.route('/delete/<int:idea_id>', methods=['DELETE'])
def delete_idea(idea_id):
    # Prepare the payload as an array with a single object containing the Id
    payload = [{"Id": idea_id}]
    
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    headers_with_content_type = {**headers, "Content-Type": "application/json"}
    
    response = requests.delete(url, headers=headers_with_content_type, json=payload)

    if response.status_code == 200:
        # Return JavaScript to reload the page
        return """
            <script>
                window.location.reload();
            </script>
        """, 200  # 200 OK response with JavaScript to reload the page
    
    
    else:
        print(f"Failed to delete idea: {response.status_code} - {response.text}")  # Debug info
        return "Failed to delete idea", 500

@ideas.route('/move_to_recipes/<int:idea_id>', methods=['POST'])
def move_to_recipes(idea_id):
    # Step 1: Fetch the record data from the existing NoCoDB table
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records/{idea_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch idea: {response.status_code} - {response.text}")
        return jsonify({"error": "Failed to fetch the idea"}), 500

    idea_data = response.json()

    # Prepare the payload for creating a new record in the target NoCoDB table
    payload = {
        "Title": idea_data.get("Title"),
        "Meal": idea_data.get("Meal"),
        "Core": idea_data.get("Core"),
        "Source": idea_data.get("Source"),
        "Notes": idea_data.get("Notes"),
    }

    # Step 2: Create a new record in the target NoCoDB table (e.g., recipes table)
    # Replace with the target table ID for recipes
    recipe_table_id = "mk4go4bhd91cihe"  
    new_url = f"{NOCO_DB_BASE_URL}/tables/{recipe_table_id}/records"
    response = requests.post(new_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Failed to create new recipe: {response.status_code} - {response.text}")
        return jsonify({"error": "Failed to create new recipe"}), 500

    new_recipe_id = response.json()["Id"]

    # Step 3: Delete the record from the current NoCoDB table
    delete_payload = [{"Id": idea_id}]
    delete_url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    delete_response = requests.delete(delete_url, headers=headers, json=delete_payload)
    
    if delete_response.status_code != 200:
        print(f"Failed to delete idea: {delete_response.status_code} - {delete_response.text}")
        return jsonify({"error": "Failed to delete the original idea"}), 500

    # Generate the URL to redirect to
    new_recipe_url = url_for('core.recipe', Id=new_recipe_id)
    print("Redirecting to:", new_recipe_url)  # Debugging log

    # Return the response with HX-Location header
    return "", 200, {'HX-Location': new_recipe_url}