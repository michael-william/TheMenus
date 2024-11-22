from flask import request, render_template, Blueprint  # noqa: F401
import requests
from flask import jsonify, url_for, redirect
import os
from dotenv import load_dotenv
import json
from werkzeug.utils import secure_filename
import markdown2
from flask_ckeditor.utils import cleanify

from app.blueprints.core.models import NoCoRecipes
from icecream import ic

core = Blueprint("core", __name__, template_folder='templates')
 

# Define a base URL and API token for NocoDB
# Load the .env file
load_dotenv()

NOCO_DB_BASE_URL = os.getenv("NOCO_DB_BASE_URL")
NOCO_DB_TABLE_ID = os.getenv("NOCO_DB_RECIPES_TABLE_ID")  
NOCO_DB_API_TOKEN = os.getenv("NOCO_DB_API_TOKEN")  

headers = {
    "xc-token": NOCO_DB_API_TOKEN
}
ic(NOCO_DB_BASE_URL, NOCO_DB_TABLE_ID, NOCO_DB_API_TOKEN, headers)

def get_recipe_by_id(recipe_id):
    """Fetch a recipe by ID from the NoCoDB API."""
    # Use the table ID in the URL
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records/{recipe_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return NoCoRecipes.from_api_data(data)
    else:
        print(f"Failed to fetch recipe with ID {recipe_id}: {response.status_code}")
        return None

def save_recipe(recipe):
    """
    Save the updated recipe data to the NoCoDB API.
    
    Parameters:
        recipe (NoCoRecipes): The recipe object containing updated data.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    # Use the table's records endpoint without specifying the ID in the URL
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    headers = {
        "xc-token": NOCO_DB_API_TOKEN,
        "Content-Type": "application/json"
    }
    print('Saving recipe to NocoDB...')
    # Convert the recipe object to a dictionary format and include the ID
    data = recipe.to_dict()
    data['Id'] = recipe.Id  # Include the ID in the request body
    
    # Send the PATCH request to update the recipe
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Recipe updated successfully.")
        return None
    else:
        print(f"Failed to update recipe with ID {recipe.Id}: {response.status_code} - {response.text}")
        return None

# Upload file to storage and retrieve attachment metadata
def upload_file_to_storage(file_path):
    target_path = f"download/noco/{NOCO_DB_TABLE_ID}/{secure_filename(os.path.basename(file_path))}"
    url = f"{NOCO_DB_BASE_URL}/storage/upload?path={target_path}"
    filename = secure_filename(file_path.split("/")[-1])
    file_size = os.path.getsize(file_path)
    mime_type = "image/jpeg"  # Adjust MIME type as needed

    with open(file_path, 'rb') as file:
        files = {
            "mimetype": (None, mime_type),
            "path": (None, target_path),
            "size": (None, str(file_size)),
            "title": (None, filename),
            "file": (filename, file, mime_type)
        }
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        print("File uploaded successfully.")
        return response.json()
    else:
        print(f"File upload failed: {response.status_code} - {response.text}")
        return None

# Update the record with the attachment metadata
def update_record_with_attachment(record_id, attachment_metadata):
    # If metadata is a list, get the first item (assuming only one attachment)
    if isinstance(attachment_metadata, list):
        attachment_metadata = attachment_metadata[0]

    # Prepare the attachment JSON
    attachment_json = {
        "path": attachment_metadata.get("path"),
        "title": attachment_metadata.get("title"),
        "mimetype": attachment_metadata.get("mimetype"),
        "size": attachment_metadata.get("size"),
        "signedPath": attachment_metadata.get("signedPath", ""),
    }
    if "id" in attachment_metadata:
        attachment_json["id"] = attachment_metadata["id"]
    
    # The request URL without a specific record ID
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    
    # Payload now includes the record ID in the body, along with the updated attachment data
    payload = {
        "Id": record_id,  # Including record ID in the payload
        "Photo": json.dumps([attachment_json])  # Assuming "Photo" is the attachment column
    }
    headers_with_content_type = {**headers, "Content-Type": "application/json"}

    # Send the PATCH request
    response = requests.patch(url, headers=headers_with_content_type, json=payload)
    
    if response.status_code == 200:
        print("Record updated successfully with attachment.")
        return response.json()
    else:
        print(f"Failed to update record: {response.status_code} - {response.text}")
        return None

@core.route('/')
def index():
    # Make a request to NocoDB to get all recipes
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Convert API data to NoCoShop instances
        data = response.json().get("list", [])
        recipes = [NoCoRecipes.from_api_data(item) for item in data]
        return render_template('core/index.html', recipes=recipes)
    else:
        ic(url, response)
        return jsonify({"error": "Failed to retrieve recipes", "status_code": response.status_code}), response.status_code
    

@core.route('/search', methods=['GET', 'POST'])
def search():
    # Get the 'search' query parameter from the request, split by whitespace to get each word
    query = request.args.get('search', '').strip()
    words = query.lower().split()  # Split by space and convert to lowercase for case-insensitive search
    
    # Fetch all recipes from NoCo DB (you may later optimize this if NoCo supports more advanced filtering)
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("list", [])
        recipes_data = [NoCoRecipes.from_api_data(item) for item in data]
        
        # Filter recipes: check if any word is in any relevant field
        if words:
            recipes = [
                recipe for recipe in recipes_data if all(
                    word in (recipe.Title or '').lower() or
                    word in (recipe.Meal or '').lower() or
                    word in (recipe.Core or '').lower() or
                    word in (recipe.Source or '').lower()
                    for word in words
                )
            ]
        else:
            recipes = recipes_data  # No search query, return all recipes

        return render_template('core/search.html', recipes=recipes, noco_db_url = NOCO_DB_BASE_URL)
    else:
        return jsonify({"error": "Failed to retrieve recipes", "status_code": response.status_code}), response.status_code

@core.route('/recipe/<int:Id>')
def recipe(Id):
    # Make a request to NocoDB to get the specific recipe by Id
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records/{Id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Convert API data to a NoCoRecipe instance (or NoCoRecipe if different)
        data = response.json()
        recipe = NoCoRecipes.from_api_data(data)
        if recipe.Ingredients:
            ingredients_html = markdown2.markdown(recipe.Ingredients)
        else:
            ingredients_html = ""
        if recipe.Method:
            method_html = markdown2.markdown(recipe.Method)
        else:
            method_html = ""
        return render_template('core/recipe.html', recipe=recipe, ingredients_html=ingredients_html, method_html=method_html)
    else:
        return jsonify({"error": "Failed to retrieve recipe", "status_code": response.status_code}), response.status_code


@core.route('/edit_field/<int:recipe_id>/<field>', methods=['GET'])
def edit_field(recipe_id, field):
    # Retrieve the recipe based on `recipe_id`
    
    recipe = get_recipe_by_id(recipe_id)  
    print(recipe)
    current_value = getattr(recipe, field, "")
    print(current_value)
    
    # Render the editable field template with an input field
    return render_template('core/editable_field.html', field=field, recipe_id=recipe_id, current_value=current_value)

@core.route('/edit_rich_field/<int:recipe_id>/<field>', methods=['GET'])
def edit_rich_field(recipe_id, field):
    # Retrieve the recipe based on `recipe_id`
    recipe = get_recipe_by_id(recipe_id)  
    print(recipe)
    current_value = getattr(recipe, field, "")
    print(current_value)
    
    # Render the editable field template with an input field
    return render_template('core/editable_rich_field.html', field=field, recipe_id=recipe_id, current_value=current_value)


@core.route('/update_field/<int:recipe_id>/<field>', methods=['POST'])
def update_field(recipe_id, field):
    # Get the new value from the POST request
    new_value = request.form['value']
    
    # Retrieve and update the recipe in the database
    recipe = get_recipe_by_id(recipe_id)  # Replace with your own function to fetch the recipe
    setattr(recipe, field, new_value)  # Update the field
    save_recipe(recipe)  # Save the updated recipe to the database/API

    # Return the display field after updating
    return render_template('core/display_field.html', field=field, value=new_value, recipe_id=recipe_id)

@core.route('/update_rich_field/<int:recipe_id>/<field>', methods=['POST'])
def update_rich_field(recipe_id, field):
    # Get the new value from the POST request
    new_value = cleanify(request.form['value'])
    
    # Retrieve and update the recipe in the database
    recipe = get_recipe_by_id(recipe_id)  # Replace with your own function to fetch the recipe
    setattr(recipe, field, request.form['value'])  # Update the field
    save_recipe(recipe)  # Save the updated recipe to the database/API

    rich_html = markdown2.markdown(new_value)

    # Return the display field after updating
    return render_template('core/display_rich_field.html', field=field, value=rich_html, recipe_id=recipe_id)


@core.route('/display_field/<int:recipe_id>/<field>', methods=['GET'])
def display_field(recipe_id, field):
    # Retrieve the recipe by ID
    recipe = get_recipe_by_id(recipe_id)
    
    # Get the current value of the field
    value = getattr(recipe, field, "")
    
    # Render a simple span with the field value for display mode
    return render_template('core/display_field.html', field=field, value=value, recipe_id=recipe_id)

@core.route('/display_rich_field/<int:recipe_id>/<field>', methods=['GET'])
def display_rich_field(recipe_id, field):
    # Retrieve the recipe by ID
    recipe = get_recipe_by_id(recipe_id)
    
    # Get the current value of the field
    value = getattr(recipe, field, "")

    rich_html = markdown2.markdown(value)
    
    # Render a simple span with the field value for display mode
    return render_template('core/display_rich_field.html', field=field, value=rich_html, recipe_id=recipe_id)

@core.route('/upload_photo_field/<int:recipe_id>', methods=['GET'])
def upload_photo_field(recipe_id):
    # Render only the photo upload form partial, not the entire layout
    return render_template('core/upload_photo_field.html', recipe_id=recipe_id)


@core.route('/save_photo/<int:recipe_id>', methods=['POST'])
def save_photo(recipe_id):
    print("Request received:", request)  # Log the request itself
    print("Request files:", request.files)  # Log the contents of request.files

    if 'photo' not in request.files:
        print("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['photo']
    if file.filename == '':
        print("No file selected")
        return jsonify({"error": "No file selected"}), 400
    
    # Save the file and get metadata for NoCoDB
    filename = secure_filename(file.filename)
    file_path = os.path.join('static/uploads', filename)
    file.save(file_path)
    
    # Upload to NoCoDB
    attachment_metadata = upload_file_to_storage(file_path)
    if not attachment_metadata:
        return jsonify({"error": "Failed to upload to NoCoDB"}), 500
    
    # Update record in NoCoDB
    if not update_record_with_attachment(recipe_id, attachment_metadata):
        return jsonify({"error": "Failed to update record in NoCoDB"}), 500
    
    # If this is an HTMX request, set HX-Redirect header
    if "HX-Request" in request.headers:
        response = jsonify({"success": True})
        response.headers["HX-Redirect"] = url_for('core.recipe', Id=recipe_id)
        return response
    
    # For non-HTMX requests, do a direct redirect
    return redirect(url_for('core.recipe', Id=recipe_id))

@core.route('/create_recipe', methods=['GET'])
def create_recipe():
    # Render a template similar to `recipe.html` but customized for creating a new recipe
    return render_template('core/create_recipe.html')

@core.route('/save_new_recipe', methods=['POST'])
def save_new_recipe():
    # Collect form data
    title = request.form.get('title')
    meal = request.form.get('meal')
    core = request.form.get('core')
    source = request.form.get('source')
    notes = request.form.get('notes')
    ingredients = request.form.get('ingredients')

    # Prepare the payload for creating a new record in NoCoDB (without the photo initially)
    payload = {
        "Title": title,
        "Meal": meal,
        "Core": core,
        "Source": source,
        "Notes": notes,
        "Ingredients": ingredients
    }

    # Make the API request to NoCoDB to create a new record
    url = f"{NOCO_DB_BASE_URL}/tables/{NOCO_DB_TABLE_ID}/records"
    headers_with_content_type = {**headers, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers_with_content_type, json=payload)
    
    if response.status_code == 200:
        # Retrieve the new recipe ID from the response
        new_recipe_id = response.json()["Id"]
        
        # Handle photo upload if a file is provided
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo_file = request.files['photo']
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join('static/uploads', filename)
            photo_file.save(photo_path)
            
            # Upload the photo to NoCoDB storage and get metadata
            photo_metadata = upload_file_to_storage(photo_path)
            
            if photo_metadata:
                # Update the record with the photo metadata
                update_record_with_attachment(new_recipe_id, photo_metadata)

        # Redirect to the new recipe's page after creation
        return redirect(url_for('core.recipe', Id=new_recipe_id))
    else:
        # Handle error and show feedback to the user
        print(f"Failed to create new recipe: {response.status_code} - {response.text}")
        return jsonify({"error": "Failed to create recipe"}), 500