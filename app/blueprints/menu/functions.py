import os
import requests
import json
from flask import current_app
from icecream import ic
from werkzeug.utils import secure_filename

def make_headers(table_id):
    headers = {
        "xc-token": current_app['NOCO_DB_API_TOKEN']
        }
    ic(current_app['NOCO_DB_BASE_URL'], 
       table_id, 
       headers)
    return headers

def update_record_with_attachment(record_id, attachment_metadata, table_id):

    headers = make_headers(table_id)
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
    url = f"{current_app['NOCO_DB_BASE_URL']}/tables/{current_app['NOCO_DB_TABLE_ID']}/records"
    
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

def upload_file_to_storage(file_path, table_id):
    target_path = f"download/noco/{table_id}/{secure_filename(os.path.basename(file_path))}"
    url = f"{current_app['NOCO_DB_BASE_URL']}/storage/upload?path={target_path}"
    filename = secure_filename(file_path.split("/")[-1])
    file_size = os.path.getsize(file_path)
    mime_type = "image/jpeg"  # Adjust MIME type as needed

    headers = make_headers(table_id)

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
    
def save_recipe(recipe, table_id):
    """
    Save the updated recipe data to the NoCoDB API.
    
    Parameters:
        recipe (NoCoRecipes): The recipe object containing updated data.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    # Use the table's records endpoint without specifying the ID in the URL
    url = f"{current_app['NOCO_DB_BASE_URL']}/tables/{table_id}/records"
    headers = {
        "xc-token": current_app['NOCO_DB_API_TOKEN'],
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