import requests
from flask import Flask, jsonify, request, render_template
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from chromaviz import visualize_collection
import socket
import webbrowser
import threading
from datetime import datetime
from urllib.parse import urlparse
import numpy as np
import json
import subprocess
import psutil
import shutil
import os
from sentence_transformers import SentenceTransformer
import time
import sys
import signal
import pprint
import re
import random





# Static variable, i update this manually each time i make a change
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
appversion_flask = "1.0.0.3000"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




# Initialize Flask app
app = Flask(__name__)




# NOTES FOR THE BELOW:
# DO NOT CONFIGURE THESE - they are merely placeholders 
# ALL settings are now extracted from appSettings.json in the root folder
# if one doesnt exist, a default is copied in from /default-config
# if that doesnt exist (for any reason)  a manual one is written out instead to cover all bases. 
# =========================================================================================
address_flask = ''
CHROMA_DATA_PATH = ""
EMBEDMODEL = ""
EMBEDMODEL_LOCAL_PATH = ""
EMBEDMODEL_CONTEXTWINDOW = 128
PROXY_URL = "" 
CHROMAVIZ_PORT = 5013
CHROMAVIZ_HOST = "127.0.0.1"
# ==========================================================================================



# Function to check for appSettings.json, and copy one or create one if it doesnt exist. 
def check_or_create_app_settings_json():
    print("\nChecking for appsettings.json...\n")
    
    # Define file paths
    root_path = os.getcwd()
    appsettings_path = os.path.join(root_path, 'appsettings.json')
    default_config_path = os.path.join(root_path, 'default-config', 'appsettings.json')
    
    # Check if appsettings.json exists in the root folder
    if os.path.exists(appsettings_path):
        print(f"###############################################")
        print("appsettings.json found in the root folder.")
        print(f"###############################################")

    # If not, check the default-config folder
    elif os.path.exists(default_config_path):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("appsettings.json not found in the root folder.")
        print("Found default config at /default-config/appsettings.json.")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        print("Copying default config to root...\n")
        shutil.copy(default_config_path, appsettings_path)
        print(f"##############################################################")
        print(f"Default config copied to\n{appsettings_path}")
        print(f"##############################################################")

    # If neither exists, create a default appsettings.json in the root
    else:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("No appsettings.json found in the root folder.")
        print("No default config found in /default-config.")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        print("Creating a default appsettings.json file in the root...\n")
        
        default_config = {
            "flask_server_endpoint": "http://127.0.0.1:5000",
            "proxy_endpoint": "",
            "chromaDB_path": os.path.join(os.getcwd(), "chroma_db"),
            "embedding_model_selected_preset": "all-MiniLM-L6-v2",
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_context_window": 512,
            "embedding_model_dimension": 384,
            "embedding_model_path": os.path.join(os.getcwd(), "models", "all-MiniLM-L6-v2"),
            "language": "en-GB",
            "CPURAMIntervalEnabled": False,
            "CPURAMInterval": 2000,
            "autoGenCollectionName": "testCollection",
            "bugFix100DocumentsEnabled": True,
            "bugFix100DocumentsBatchSize": 50000
        }

        with open(appsettings_path, 'w') as f:
            json.dump(default_config, f, indent=4)

        print(f"###############################################################")
        print(f"Default appsettings.json Manually written to\n{appsettings_path}")
        print(f"###############################################################")




# Check for the appSettings.json file before doing anything 
check_or_create_app_settings_json()






# Function to load settings from appSettings.json
def load_settings_from_json(file_path):
    with open(file_path, 'r') as f:
        settings = json.load(f)

    # Update the global variables with values from the JSON file
    global address_flask, CHROMA_DATA_PATH, EMBEDMODEL, EMBEDMODEL_LOCAL_PATH, EMBEDMODEL_CONTEXTWINDOW, PROXY_URL
    address_flask = settings.get("flask_server_endpoint", address_flask)
    CHROMA_DATA_PATH = settings.get("chromaDB_path", CHROMA_DATA_PATH)
    EMBEDMODEL = settings.get("embedding_model", EMBEDMODEL)
    EMBEDMODEL_LOCAL_PATH = settings.get("embedding_model_path", EMBEDMODEL_LOCAL_PATH)
    EMBEDMODEL_CONTEXTWINDOW = settings.get("embedding_context_window", EMBEDMODEL_CONTEXTWINDOW)
    PROXY_URL = settings.get("proxy_endpoint", PROXY_URL)

    # Parse the URL
    chromaviz_parsed_url = urlparse(address_flask)
    #print(f"Flask Address:\n{chromaviz_parsed_url}")

    # Extract the server address and port number
    #CHROMAVIZ_HOST = chromaviz_parsed_url.hostname
    CHROMAVIZ_PORT = chromaviz_parsed_url.port + 1

    #print(f"Global variable at start of Visualisation 2 Chroma Viz Port:{CHROMAVIZ_PORT}")

# Call this function to update global variables at the start of your application
load_settings_from_json("appSettings.json")







# If you're not using a proxy, simply comment out or leave these lines out
if PROXY_URL:
    os.environ['HTTP_PROXY'] = PROXY_URL
    os.environ['HTTPS_PROXY'] = PROXY_URL






# Print the config in a clean and readable format
print(f"\n\nFlask Web App:")
print(f"================================")
print(f"  Name:      Chroma Flow Studio")
print(f"  Version:   {appversion_flask}")
print("============================= Configuration ===========================================================")
print(f"  Flask Address:             {address_flask}")
print(f"  Chroma Data Path:          {CHROMA_DATA_PATH}")
print(f"  Embedding Model:           {EMBEDMODEL}")
print(f"  Embedding Model Path:      {EMBEDMODEL_LOCAL_PATH}")
print(f"  Embedding Context Window:  {EMBEDMODEL_CONTEXTWINDOW}")
print(f"  Proxy URL:                 {PROXY_URL if PROXY_URL else 'Not used'}")
print("=======================================================================================================")


print("""
        __                                  ______                      __            ___     
  _____/ /_  _________  ____ ___  ____ _   / __/ /___ _      __   _____/ /___  ______/ (_)___ 
 / ___/ __ \/ ___/ __ \/ __ `__ \/ __ `/  / /_/ / __ \ | /| / /  / ___/ __/ / / / __  / / __ \\
/ /__/ / / / /  / /_/ / / / / / / /_/ /  / __/ / /_/ / |/ |/ /  (__  ) /_/ /_/ / /_/ / / /_/ /
\___/_/ /_/_/   \____/_/ /_/ /_/\__,_/  /_/ /_/\____/|__/|__/  /____/\__/\__,_/\__,_/_/\____/ 
""")
print("\n\n")
time.sleep(3) 





# Get Port numbers as seperate variables from the host variables
# Parse the URLs and extract the port numbers
parsed_flask = urlparse(address_flask)

# Assign port numbers and host based on the parsed URLs
port_flask = parsed_flask.port
host_flask = parsed_flask.hostname




# Global variable to track connection status
client = None



# Create a persistent Chroma client
persistentChromaClient = chromadb.PersistentClient(path=CHROMA_DATA_PATH)




# OLD WAY - Initialize the embedding function
#pyEmbedFunction = embedding_functions.SentenceTransformerEmbeddingFunction(EMBEDMODEL)


# NEW WAY - Initialize the embedding function with the model from the specified local path or Hugging Face hub
# Initialize the embedding function with local or Hugging Face model
try:
    # Check if the model path exists locally
    print(f"\n\nPre-checks from embedding function...\nChecking Embedding Model Path exists and contains models....")
    if os.path.exists(EMBEDMODEL_LOCAL_PATH):
        # If model is already downloaded and saved locally, load from there
        pyEmbedFunction = embedding_functions.SentenceTransformerEmbeddingFunction(EMBEDMODEL_LOCAL_PATH)
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Found - Loaded model from local path:\n{EMBEDMODEL_LOCAL_PATH}")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    else:
        # If not found locally, download from Hugging Face
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Not Found Locally - Downloading model {EMBEDMODEL} from Hugging Face...")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        model = SentenceTransformer(EMBEDMODEL)
        
        # Save the model locally
        print(f"")
        print(f"Saving Model to Embedding Path...")
        os.makedirs(EMBEDMODEL_LOCAL_PATH, exist_ok=True)
        model.save(EMBEDMODEL_LOCAL_PATH)
        print(f"Model downloaded and saved to: {EMBEDMODEL_LOCAL_PATH}")
        
        # Now initialize the embedding function with the local path
        print(f"Now Loading locally...")
        pyEmbedFunction = embedding_functions.SentenceTransformerEmbeddingFunction(EMBEDMODEL_LOCAL_PATH)
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Loaded model from local path:\n{EMBEDMODEL_LOCAL_PATH}")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

except Exception as e:
    print(f"")
    print(f"Error loading model: {e}")
    print(f"Also check your internet connection, any proxy settings, and your connectivity to huggingface.")
    print(f"If all of that is working, then this model is not compatible with ChromaFlow Studio / Chroma, either outright, or without further code changes..")
    # Short summary and prompt user for next steps
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"Unable to load the embedding model.")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("Continuing without embeddings - model failed to load.")
    pyEmbedFunction = None  # Set to None to indicate no embeddings








# Indicate that Flask will continue launching regardless of ChromaDB status
print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print(f"Launching Flask Web App on:\n{host_flask}:{port_flask}...")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")






# Auto Launch Flask and Web App 
def open_browser():
    time.sleep(4) 
    webbrowser.open(address_flask)






@app.route('/')
def index():
    # Serve the HTML page when the root is accessed
    return app.send_static_file('index.html')







# Function to clear and reinitialize the app components
def reinitialize_app():

    # Call this function to update global variables at the start of your application
    load_settings_from_json("appSettings.json")

    global client, persistentChromaClient, pyEmbedFunction

    # Clear the client variable and reinitialize it (simulating restart)
    client = None

    # Reinitialize the persistent Chroma client
    print("Reinitializing Chroma client...")
    persistentChromaClient = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    
    # Reinitialize the embedding model
    try:
        print(f"\n\nReinitializing embedding model...\nChecking if model exists locally...")
        if os.path.exists(EMBEDMODEL_LOCAL_PATH):
            pyEmbedFunction = embedding_functions.SentenceTransformerEmbeddingFunction(EMBEDMODEL_LOCAL_PATH)
            print(f"Loaded model from local path: {EMBEDMODEL_LOCAL_PATH}")
        else:
            print(f"Model not found locally. Downloading from Hugging Face: {EMBEDMODEL}...")
            model = SentenceTransformer(EMBEDMODEL)
            os.makedirs(EMBEDMODEL_LOCAL_PATH, exist_ok=True)
            model.save(EMBEDMODEL_LOCAL_PATH)
            pyEmbedFunction = embedding_functions.SentenceTransformerEmbeddingFunction(EMBEDMODEL_LOCAL_PATH)
            print(f"Model downloaded and saved to: {EMBEDMODEL_LOCAL_PATH}")

    except Exception as e:
        print(f"Error reinitializing the embedding model: {e}")







# Example route to restart (reinitialize) the Flask server without killing the process
@app.route('/restart', methods=['GET'])
def restart():
    # Call this function to update global variables at the start of your application
    load_settings_from_json("appSettings.json")

    """Endpoint to restart/reinitialize the server"""
    print("Reinitializing the app components...")
    
    # Run the reinitialization in a separate thread to avoid blocking the request
    threading.Thread(target=reinitialize_app).start()
    
    time.sleep(2) 
    return jsonify(message="Server components are being reinitialized. Please wait..."), 200











@app.route('/read-settings', methods=['GET'])
def read_settings():
    try:
        # Open and read the appsettings.json file
        with open('appsettings.json', 'r') as file:
            settings = json.load(file)
        
        # Print the settings to the console
        print(json.dumps(settings, indent=4))  # Print nicely formatted JSON

        # Call this function to update global variables at the start of your application
        load_settings_from_json('appsettings.json')

        # Return a response (could be the same data or a success message)
        return jsonify({"status": "success", "settings": settings}), 200

    except Exception as e:
        # Handle error (file not found, JSON parse error, etc.)
        print(f"Error reading settings: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500






@app.route('/save-settings', methods=['POST'])
def save_settings():
    try:
        # Get the JSON data from the request
        updated_settings = request.get_json()
        
        # Save the settings back to appsettings.json
        with open('appsettings.json', 'w') as file:
            json.dump(updated_settings, file, indent=4)
        
        # Call this function to update global variables at the start of your application
        load_settings_from_json("appSettings.json")

        # Return a success response
        return jsonify({"status": "success", "message": "Settings saved successfully!"}), 200
    except Exception as e:
        # Handle errors (e.g., file write errors, invalid JSON)
        print(f"Error saving settings: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500







@app.route('/write-default-config', methods=['POST'])
def write_default_config_route():

    print(f"Recevied Request to manually write default config file.")
    print(f"Creating default JSON object...")

    # Hardcoded default configuration
    default_config = {
        "flask_server_endpoint": "http://127.0.0.1:5000",
        "proxy_endpoint": "",
        "chromaDB_path": os.path.join(os.getcwd(), "chroma_db"),
        "embedding_model_selected_preset": "all-MiniLM-L6-v2",
        "embedding_model": "all-MiniLM-L6-v2",
        "embedding_context_window": 512,
        "embedding_model_dimension": 384,
        "embedding_model_path": os.path.join(os.getcwd(), "models", "all-MiniLM-L6-v2"),
        "language": "en-GB",
        "CPURAMIntervalEnabled": False,
        "CPURAMInterval": 2000,
        "autoGenCollectionName": "testCollection",
        "bugFix100DocumentsEnabled": True,
        "bugFix100DocumentsBatchSize": 50000
    }
    
    appsettings_path = 'appsettings.json'

    print(f"DEBUG\nShowing Config that will be Written:\n{default_config}")


    try:
        # Always overwrite the file with the default config
        with open(appsettings_path, 'w') as f:
            json.dump(default_config, f, indent=4)

        return jsonify({"message": "Default configuration written successfully!"}), 200

    except Exception as e:
        return jsonify({"message": f"Error writing default config: {e}"}), 500





@app.route('/system-stats', methods=['GET'])
def system_stats():
    # Get the system stats
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    return jsonify(cpu=cpu_usage, ram=ram_usage)








@app.route('/python-stats', methods=['GET'])
def python_stats():
    # Get the current process ID (PID)
    pid = os.getpid()
    
    # Get the process object for the current Python app
    process = psutil.Process(pid)
    
    # Get CPU usage of the current Python process
    cpu_usage = process.cpu_percent(interval=1)
    
    # Get memory usage of the current Python process
    ram_usage = process.memory_percent()
    
    return jsonify(cpu=cpu_usage, ram=ram_usage)










@app.route('/chromadb-path-sqllite', methods=['GET'])
def chromadb_path_sqllite():

    try:
        # Return global variable appversion_flask as a JSON object
        return jsonify({'chromadb_path_sqllite': CHROMA_DATA_PATH})

    except Exception as e:
        # Handle any error that occurs during the ChromaDB request
        return jsonify({'error': str(e)}), 500








@app.route('/version', methods=['GET'])
def get_flask_app_version():

    if persistentChromaClient is None:
        # If the ChromaDB client is not initialized, return an error message
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    try:
        # Return global variable appversion_flask as a JSON object
        return jsonify({'flaskAppVersion': appversion_flask})

    except Exception as e:
        # Handle any error that occurs during the ChromaDB request
        return jsonify({'error': str(e)}), 500







@app.route('/version-chroma', methods=['GET'])
def get_chromadb_app_version():
    try:
        # Run the command and capture the output
        result = subprocess.run(['pip', 'show', 'chromadb'], capture_output=True, text=True, check=True)
        
        # Filter the output for the version line using 'findstr'
        version_line = subprocess.run(['findstr', 'Version'], input=result.stdout, capture_output=True, text=True, check=True)
        
        # Return the version line
        return f"{version_line.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        return f"Error occurred: {e}"







@app.route('/embedmodelinfo', methods=['GET'])
def get_embedding_model_info():

    if persistentChromaClient is None:
        # If the ChromaDB client is not initialized, return an error message
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    try:
        result = {        
            "embedding_model": EMBEDMODEL,
            "embedding_model_path": EMBEDMODEL_LOCAL_PATH,
            "embedding_model_context_window": EMBEDMODEL_CONTEXTWINDOW
        }

        return jsonify(result)

    except Exception as e:
        # Handle any error that occurs during the ChromaDB request
        return jsonify({'error': str(e)}), 500







@app.route('/flask-heartbeat', methods=['GET'])
def flask_heartbeat():
    if persistentChromaClient is None:
        # If the ChromaDB client is not initialized, return an error message
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    try:
        # Send a heartbeat to the 'address_flask' variable
        response = requests.get(address_flask)

        if response.status_code == 200:
            # If heartbeat was successful, return the app version
            return jsonify({'heartbeat': "true"})
        else:
            # If heartbeat failed, return an error message
            return jsonify({'error getting heartbeat': str(e)}), 500

    except Exception as e:
        # Handle any error that occurs during the request
        return jsonify({'error': str(e)}), 500










@app.route('/get-collections', methods=['GET'])
def get_collections():
    print(f"=======================================")
    print(f"Recevied request for: /get-collections")
    print(f"=======================================")

    if persistentChromaClient is None:
        print(f"   FROM: /get-collections   ERROR: ChromaDB server is unavailable")
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    try:
        print(f"   FROM: /get-collections   Fetching all collections...")
        collections = persistentChromaClient.list_collections()
        print(f"   FROM: /get-collections   Collections Fetched...")

        # Convert each collection into a serializable dictionary
        print(f"   FROM: /get-collections   Converting Collection to Dictionary Object...")
        collections_list = []
        for collection in collections:
            if isinstance(collection, str):
                # New version, collection is string (name)
                collections_list.append({"name": collection, "id": collection})
            else:
                # Old version, collection is object
                collections_list.append({"name": collection.name, "id": str(collection.id)})

        print(f"   FROM: /get-collections   Returned Fetched Collections as JSON")
        return jsonify(collections_list)

    except Exception as e:
        print(f"   FROM: /get-collections   Error Fetching Collections: {str(e)}")
        return jsonify({'error': str(e)}), 500













@app.route('/count-collections', methods=['GET'])
def count_collections():
    print(f"=========================================")
    print(f"Recevied request for: /count-collections")
    print(f"=========================================")

    if persistentChromaClient is None:
        print(f"   FROM: /count-collections   ERROR: ChromaDB server is unavailable")
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    try:
        # Fetch collections using the ChromaDB client (defaults to v2)
        print(f"   FROM: /count-collections   Fetching all Collections...")
        allCollections = persistentChromaClient.list_collections()
        print(f"   FROM: /count-collections   Collections Fetched")

        # Count the collections
        collectionCount = len(allCollections)

        # Return the list of collections as a JSON response
        print(f"   FROM: /count-collections   Returning Collection Count: {collectionCount}")
        return jsonify(collectionCount )

    except Exception as e:
        # Handle any error that occurs during the ChromaDB request
        print(f"   FROM: /count-collections  Error counting Collections: {str(e)}")
        return jsonify({'error': str(e)}), 500











@app.route('/get-collection-overview', methods=['GET'])
def get_collection_overview():
    print(f"================================================")
    print(f"Recevied request for: /get-collection-overview")
    print(f"================================================")

    if persistentChromaClient is None:
        print(f"   FROM: /get-collection-overview   ERROR: ChromaDB server is unavailable")
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    try:
        # Retrieve all collections from the Chroma client
        print(f"   FROM: /get-collection-overview   Fetching all Collections...")
        allCollections = persistentChromaClient.list_collections()
        print(f"   FROM: /get-collection-overview   Collections Fetched")

        # Prepare the response structure
        collection_overview = []

        if allCollections and isinstance(allCollections[0], str):
            # New version: collections are strings
            for collection_name in allCollections:
                try:
                    # Fetch collection details using the collection name
                    collection = persistentChromaClient.get_collection(collection_name)
                    collection_id = str(collection.id)
                    document_count = collection.count() if collection.count() is not None else "Invalid"

                    # Add collection information to the response list
                    collection_overview.append({
                        'id': collection_id,
                        'name': collection_name,
                        'document_count': document_count
                    })

                except Exception as e:
                    print(f"   FROM: /get-collection-overview   ERROR accessing collection {collection_name}: {str(e)}")
                    collection_overview.append({
                        'error': f"Error accessing collection {collection_name}: {str(e)}"
                    })
        else:
            # Old version: collections are objects
            for collection in allCollections:
                try:
                    collection_name = collection.name
                    collection_id = collection.id
                    document_count = collection.count() if collection.count() is not None else "Invalid"

                    # Add collection information to the response list
                    collection_overview.append({
                        'id': collection_id,
                        'name': collection_name,
                        'document_count': document_count
                    })
                except Exception as e:
                    print(f"   FROM: /get-collection-overview   ERROR accessing collection {collection.name}: {str(e)}")
                    collection_overview.append({
                        'error': f"Error accessing collection {collection.name}: {str(e)}"
                    })

        # Return the overview as a JSON response
        print(f"   FROM: /get-collection-overview   SUCCESS - Returning Collection Overview as JSON")
        return jsonify({
            'status': 'success',
            'total_collections': len(collection_overview),
            'collections': collection_overview
        })

    except Exception as e:
        print(f"   FROM: /get-collection-overview   Error getting Collection Overview: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"An error occurred while retrieving collections: {str(e)}"
        }), 500
















@app.route('/api/get-collection-details', methods=['GET'])
def get_collection_details():
    print(f"===================================================")
    print(f"Recevied request for: /api/get-collection-details")
    print(f"===================================================")

    if persistentChromaClient is None:
        print(f"   FROM: /api/get-collection-details   ERROR: ChromaDB server is unavailable")
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Extract collection name from the request's query parameters
    passed_collection_name = request.args.get("collection_name")
    
    if not passed_collection_name:
        print(f"   FROM: /api/get-collection-details   Collection name is required")
        return jsonify({'error': 'Collection name is required'}), 400

    print(f"   FROM: /api/get-collection-details   Passed Collection: {passed_collection_name}")

    try:
        # Dynamically retrieve the collection
        coll = persistentChromaClient.get_collection(passed_collection_name)

        # Extract the collection details and convert UUID fields to string
        collection_details = {
            'id': str(coll.id),  # Convert UUID to string
            'name': coll.name,
            'tenant': coll.tenant,
            'database': coll.database,
            'metadata': coll.metadata,  # Assuming metadata is a JSON object
        }

        # Read HNSW configuration from metadata
        hnsw_config = coll.metadata or {}

        collection_details.update({
            'config_name': hnsw_config.get('name', 'N/A'),
            'config_space': hnsw_config.get('hnsw:space', 'N/A'),
            'config_ef_construction': hnsw_config.get('hnsw:construction_ef', 'N/A'),
            'config_ef_search': hnsw_config.get('hnsw:search_ef', 'N/A'),
            'config_num_threads': hnsw_config.get('hnsw:num_threads', 'N/A'),
            'config_m': hnsw_config.get('hnsw:M', 'N/A'),
            'config_resize_factor': hnsw_config.get('hnsw:resize_factor', 'N/A'),
            'config_batch_size': hnsw_config.get('hnsw:batch_size', 'N/A'),
            'config_sync_threshold': hnsw_config.get('hnsw:sync_threshold', 'N/A'),
        })

        # Return the collection details as a JSON response
        print(f"   FROM: /api/get-collection-details   SUCCESS - Returning {passed_collection_name} Details as JSON")
        return jsonify(collection_details)

    except Exception as e:
        print(f"   FROM: /api/get-collection-details   Error getting {passed_collection_name} Details: {str(e)}")
        return jsonify({'error': str(e)}), 500











@app.route('/api/create-new-collection', methods=['POST'])
def create_new_collection():
    if persistentChromaClient is None:  # Assuming client is defined elsewhere
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Extract collection data from the request's JSON payload
    data = request.json
    passed_collection_name = data.get("collection_name")
    space = data.get("space")
    ef_construction = data.get("ef_construction")
    ef_search = data.get("ef_search")
    num_of_threads = data.get("num_of_threads")
    m = data.get("m")
    resize_factor = data.get("resize_factor")
    batch_size = data.get("batch_size")
    sync_threshold = data.get("sync_threshold")
    passed_metadata = data.get("metadata", {})

    # Debugging: print all extracted values to the server's log
    print(f"Received data:\ncollection_name={passed_collection_name},\nspace={space},\n"
          f"ef_construction={ef_construction},\nef_search={ef_search},\n"
          f"num_of_threads={num_of_threads},\nm={m},\nresize_factor={resize_factor},\n"
          f"batch_size={batch_size},\nsync_threshold={sync_threshold},\nmetadata={passed_metadata}\n")

    # Ensure collection name is provided
    if not passed_collection_name:
        return jsonify({'error': 'Collection name is required'}), 400

    try:
        # Try getting the collection first (doesn't raise exception if collection is not found)
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"Existing Collection '{passed_collection_name}' found.")

        # If collection is found, no need to create it again, just return success
        return jsonify({"message": f"Collection '{passed_collection_name}' already exists."}), 200

    except Exception as e:
        # Handle unexpected errors
        print(f"{str(e)}")
        print(f"Collection not found, proceeding to create it...")

    try:
        # If collection is not found, proceed to create it
        # Check if metadata is provided and use it accordingly
        if passed_metadata:  # If metadata is not empty (not None or empty dict)
            pycollection = persistentChromaClient.create_collection(
                passed_collection_name,
                embedding_function=pyEmbedFunction,
                metadata=passed_metadata
            )
        else:
            pycollection = persistentChromaClient.create_collection(
                passed_collection_name,
                embedding_function=pyEmbedFunction
            )
    
        print(f"Created new collection '{passed_collection_name}' successfully.")
        
        return jsonify({"message": f"Collection '{passed_collection_name}' created successfully."}), 200
    
    except Exception as e:
        # Catch the error and return the actual error message
        error_message = str(e)
        print(f"Error occurred while creating collection '{passed_collection_name}': {error_message}")
        return jsonify({"error": f"Failed to create collection: {error_message}"}), 500












@app.route('/clone-new-collection', methods=['POST'])
def clone_new_collection():
    if persistentChromaClient is None:  # Assuming client is defined elsewhere
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Extract collection data from the request's JSON payload
    data = request.json
    passed_collection_name = data.get("collection_name")
    new_collection_name = data.get("new_collection_name")
    batch_limit = data.get('batch_limit', 100)  # Default to 100 if not provided

    # Debugging: print all extracted values to the server's log
    print(f"Received data:\ncollection_name={passed_collection_name}")
    print(f"Received data:\nnew_collection_name={new_collection_name}")
    print(f"Batch Limit: {batch_limit}")

    # Ensure collection name is provided
    if not passed_collection_name or not new_collection_name:
        return jsonify({'error': 'Collection name and new collection name are required'}), 400

    try:
        # Try getting the collection first (doesn't raise exception if collection is not found)
        pycollection_old = persistentChromaClient.get_collection(passed_collection_name)
        print(f"Existing Collection '{passed_collection_name}' found.")

    except Exception as e:
        # Handle unexpected errors
        print(f"{str(e)}")
        return jsonify({"message": f"Collection '{passed_collection_name}' Not Found, aborting..."}), 404

    # Also confirm the new name doesn't already exist
    try:
        pycollection_new = persistentChromaClient.get_collection(new_collection_name)
        print(f"New Collection Name '{new_collection_name}' already exists, aborting.")
        return jsonify({"message": f"New Collection Name '{new_collection_name}' already exists, aborting."}), 567

    except Exception as e:
        # Handle unexpected errors
        print(f"New Collection Name '{new_collection_name}' is available...proceeding...")

    # Now extract the old ids, documents, and metadata into object variables
    old_collection_metadata = pycollection_old.metadata

    # Fetch the documents and their metadata
    old_results = pycollection_old.get(include=["documents", "metadatas"])

    old_doc_ids = old_results['ids']
    old_documents = old_results['documents']
    old_document_metadata = old_results['metadatas']

    # Now we need to create a new one with the same parameters
    try:
        if old_collection_metadata:  # If metadata is not empty
            pycollection_new = persistentChromaClient.create_collection(
                new_collection_name,
                embedding_function=pyEmbedFunction,
                metadata=old_collection_metadata
            )
        else:
            pycollection_new = persistentChromaClient.create_collection(
                new_collection_name,
                embedding_function=pyEmbedFunction
            )

        print(f"Created new collection '{new_collection_name}' from '{passed_collection_name}' successfully.")
    except Exception as e:
        print(f"Failed to create collection '{new_collection_name}': {str(e)}")
        return jsonify({'error': f'Failed to create new collection: {str(e)}'}), 500

    # Function to split documents into smaller batches
    def chunk_records(doc_ids, documents, metadata, batch_size):
        for i in range(0, len(doc_ids), batch_size):
            yield doc_ids[i:i + batch_size], documents[i:i + batch_size], metadata[i:i + batch_size]

    batches = chunk_records(old_doc_ids, old_documents, old_document_metadata, batch_limit)

    # Now we need to copy the data in batches
    try:
        print(f"Copying Data into New Cloned Collection...")
        
        # Process each batch separately
        for batch_ids, batch_documents, batch_metadata in batches:
            try:
                print(f"Upserting batch of size {len(batch_ids)}...")
                pycollection_new.upsert(
                    documents=batch_documents,
                    metadatas=batch_metadata,
                    ids=batch_ids
                )
                print(f"Upsert for batch successful!")

            except Exception as e:
                print(f"Error during upsert: {str(e)}")
                print(f"Deleting Cloned Collection to Rollback Changes...")
                persistentChromaClient.delete_collection(name=new_collection_name)

                # Check if the exception message contains "exceeds maximum batch size"
                if "exceeds maximum batch size" in str(e):
                    return jsonify({'error': f'Batch exceeds maximum size: {str(e)}'}), 566

                return jsonify({'error': f'Failed to upsert documents: {str(e)}'}), 500

        print(f"Clone Complete - Data migrated successfully.")
        return jsonify({"message": "Clone Complete - Data migrated successfully."}), 200

    except Exception as e:
        print(f"Error migrating documents to Cloned Collection: {str(e)}")
        print(f"Deleting Cloned Collection to Rollback Changes...")
        persistentChromaClient.delete_collection(name=new_collection_name)
        return jsonify({"error": f"Error migrating documents to Cloned Collection: {str(e)}"}), 500

















@app.route('/api/delete-collection-v2', methods=['POST'])
def delete_collection():
    if persistentChromaClient is None:  # Assuming client is defined elsewhere
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Extract collection data from the request's JSON payload
    data = request.json
    passed_collection_name = data.get("collection_name")

    # Debugging: print all extracted values to the server's log
    print(f"Received data:\ncollection_name={passed_collection_name}")

    # Ensure collection name is provided
    if not passed_collection_name:
        return jsonify({'error': 'Collection name is required'}), 400

    try:
        # Try getting the collection first (doesn't raise exception if collection is not found)
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"Existing Collection '{passed_collection_name}' found.")

        # If the collection exists, delete it
        persistentChromaClient.delete_collection(passed_collection_name)
        print(f"Collection '{passed_collection_name}' deleted successfully.")
        return jsonify({'message': f"Collection '{passed_collection_name}' deleted successfully."}), 200

    except Exception as e:
        # Handle unexpected errors
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred while deleting the collection'}), 500










@app.route('/api/delete-all-collections-v2', methods=['POST'])
def delete_all_collections():
    print(f"=====================================================")
    print(f"Recevied request for: /api/delete-all-collections-v2")
    print(f"=====================================================")

    if persistentChromaClient is None:
        print(f"   FROM: /api/delete-all-collections-v2   ERROR: ChromaDB server is unavailable")
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    try:
        # Fetch collections using the ChromaDB client
        collections = persistentChromaClient.list_collections()
        print(f"   FROM: /api/delete-all-collections-v2   Collections Fetched")

        # If no collections are found, return a message
        if not collections:
            print(f"   FROM: /api/delete-all-collections-v2   No collections found to delete")
            return jsonify({'message': 'No collections found to delete.'}), 200

        # Attempt to delete each collection
        deleted_collections = []
        failed_collections = []

        if collections and isinstance(collections[0], str):
            # New version: collections are strings
            for collection in collections:
                try:
                    persistentChromaClient.delete_collection(collection)
                    deleted_collections.append(collection)
                    print(f"Deleted collection: {collection}")
                except Exception as e:
                    failed_collections.append({
                        'collection': collection,
                        'error': str(e)
                    })
                    print(f"Failed to delete collection {collection}: {str(e)}")
        else:
            # Old version: collections are objects
            for collection in collections:
                try:
                    persistentChromaClient.delete_collection(collection.name)
                    deleted_collections.append(collection.name)
                    print(f"Deleted collection: {collection.name}")
                except Exception as e:
                    failed_collections.append({
                        'collection': collection.name,
                        'error': str(e)
                    })
                    print(f"Failed to delete collection {collection.name}: {str(e)}")

        # Define the response to return
        response = {
            'deleted_collections': deleted_collections,
            'failed_collections': failed_collections
        }

        return jsonify(response), 200

    except Exception as e:
        # Handle unexpected errors at the route level
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred while deleting all collections'}), 500












@app.route('/generate-embedding', methods=['POST'])
def generate_embedding():

    # Step 1: Get the input string from the request
    data = request.get_json()  # This assumes you're sending JSON

    input_string = data.get('text')  # Extract the text field from the JSON
    
    if not input_string:
        return jsonify({"error": "No text provided"}), 400

    # Step 2: Generate the embedding for the input string with try-catch block
    try:
        embeddingToReturn = pyEmbedFunction([input_string])
    except Exception as e:
        return jsonify({"error": f"An error occurred while generating the embedding: {str(e)}"}), 500

    # Step 3: Return the embedding in the response
    return jsonify({"embedding": embeddingToReturn[0].tolist()})











@app.route('/api/add-document', methods=['POST'])
def add_document():
    print(f"=====================================================")
    print(f"Recevied request for: /api/add-document")
    print(f"=====================================================")

    # Get the data from the request body
    doc_data = request.get_json()

    if not doc_data:
        return jsonify({'error': 'No document data provided'}), 400

    # Extract data from the request
    collection_name = doc_data.get("collection_name")
    doc_id = doc_data.get("id")
    doc_content = doc_data.get("document")
    metadata = doc_data.get("metadata", {})

    if not collection_name or not doc_id or not doc_content:
        return jsonify({'error': 'Missing required fields (collection_name, id, document)'}), 400

    try:
        # Dynamically retrieve the collection
        pycollection = persistentChromaClient.get_collection(collection_name)
        print(f"Collection {collection_name} found and retrieved.")

    except Exception as e:
        return jsonify({'error': f"Collection {collection_name} not found: {str(e)}"}), 500

    try:
        # Fetch all document IDs (you may want to optimize this if the collection is large)
        results = pycollection.get(include=["documents"])
    
        # Check if the document with the specific ID already exists
        if doc_id in results['ids']:
            return jsonify({'message': 'Document already exists'}), 543
    
        # If no existing document, set modified_date and embedding_model if missing
        if not metadata.get("date_modified"):
            metadata["date_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        if not metadata.get("embedding_model"):
            metadata["embedding_model"] = EMBEDMODEL

        if not metadata.get("embedding_model_context_window"):
            metadata["embedding_model_context_window"] = EMBEDMODEL_CONTEXTWINDOW

    
        # Add the document to the collection
        pycollection.add(
            documents=[doc_content],
            metadatas=[metadata],
            ids=[doc_id]
        )
    
        return jsonify({'message': 'Document added successfully'}), 200

    except Exception as e:
        # Handle errors during document insertion
        return jsonify({'error': f"Error adding document: {str(e)}"}), 500


    
    




@app.route('/api/add-many-test-document', methods=['POST'])
def add_many_test_documents():

    if persistentChromaClient is None:
        # If the ChromaDB client is not initialized, return an error message
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Get the data from the request body
    doc_data = request.get_json()

    if not doc_data:
        return jsonify({'error': 'No document data provided'}), 400

    # Extract data from the request
    passed_collection_name = doc_data.get("collection_name")

    if not passed_collection_name:
        return jsonify({'error': 'Missing required field: collection name'}), 400
    
    print(f"Request to add multiple documents to collection.")
    print(f"Passed Collection Name: {passed_collection_name}")

    try:
        # Dynamically retrieve the collection
        print(f"Checking for collection: {passed_collection_name}")
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"Collection {passed_collection_name} found and retrieved.")

    except Exception as e:
        return jsonify({'error': f"Collection {passed_collection_name} not found: {str(e)}"}), 500

    
    # Dummy document generation
    documents = [
        {"id": "doc_1", 
        "document": "The football team trained intensely for the upcoming match. The football team dedicated themselves to an intense training regimen as they prepared for their upcoming match. Every player understood the importance of this game, and the atmosphere during practice was filled with focus and determination. Coaches pushed them harder than ever before, emphasizing fitness, technique, and mental toughness. Each drill was designed to sharpen their skills and build chemistry on the field. They practiced set pieces, defensive formations, and quick transitions, all with the goal of achieving perfection when game time arrived. The intensity of the training sessions was palpable. Sweat poured down the players' faces as they tirelessly ran drills under the watchful eyes of their coaches. Despite the exhaustion, there was a palpable sense of unity within the team. They were no longer just individuals; they were a collective, working toward a single goal. The upcoming match loomed large in their minds, and they knew that every moment spent on the field during training was one step closer to success. The players pushed each other to their limits, knowing that victory would depend on how well they executed everything they practiced.",
        "metadata": {
            "source": "sports",
            "team_focus": True,
            "intensity_level": 8,
            "training_sessions": 5,
            "days_until_match": 4,
            "players_determined": True,
            "coaches_involved": True,
            "exhaustion_level": 7.5,
            "match_importance": 10,
            "team_spirit": True,
            "mental_preparation": True
            }
        },
        {"id": "doc_2", 
        "document": "The basketball game was thrilling. The tension was palpable as the teams faced off in an exciting contest that kept the audience on the edge of their seats. The court was alive with the sound of sneakers sliding, basketballs bouncing, and the roar of the crowd. Every pass, every shot, and every defensive maneuver was met with enthusiasm. The players were locked in, giving it their all, with the score neck-and-neck for most of the game. Key players rose to the occasion, hitting critical shots under pressure, and making defensive plays that could turn the tide of the game. As the final buzzer sounded, the fans erupted in cheers, recognizing the players' dedication and skill that made the game a memorable spectacle.",
        "metadata": {
            "source": "sports",
            "game_intensity": 9,
            "audience_engagement": True,
            "score_close": True,
            "key_players_shining": True,
            "crowd_cheering": True,
            "momentum_shift": True,
            "game_outcome": "exciting"
            }
        },
        {"id": "doc_3", 
        "document": "Technology is constantly evolving. In recent years, the pace of technological advancements has accelerated at an unprecedented rate. Innovations like artificial intelligence, quantum computing, and blockchain are disrupting industries across the globe. Devices are becoming smarter, more intuitive, and deeply integrated into our daily lives. From self-driving cars to advanced medical diagnostics, technology is changing the way we live and work. The rapid pace of change can be overwhelming, but it also offers incredible opportunities for growth and improvement. As we continue to push the boundaries of what is possible, it's exciting to imagine where technology will take us next.",
        "metadata": {
            "source": "technology",
            "evolution_speed": "fast",
            "disruptive_technologies":"AI, quantum computing, blockchain",
            "impact_on_life": True,
            "innovation_opportunities": True,
            "transformation_in_life": True,
            "growth_potential": True
            }
        },
        {"id": "doc_4", 
        "document": "The latest smartphone models feature AI capabilities. New smartphone models now come equipped with advanced artificial intelligence technologies that enhance user experience. From camera optimization to voice assistants, AI is helping to make smartphones smarter and more intuitive. These devices can analyze user behavior to predict needs, automate tasks, and even provide personalized recommendations. With the integration of AI, smartphones have become powerful tools for everything from productivity to entertainment. As the technology continues to evolve, we can expect even more sophisticated features that blur the line between user interaction and automation.",
        "metadata": {
            "source": "technology",
            "ai_integration": True,
            "device_features":"camera optimization, voice assistants, personalization",
            "user_experience_improvement": True,
            "automation": True,
            "advancement_rate": "high"
            }
        },
        {"id": "doc_5", 
        "document": "Artificial intelligence is reshaping how businesses operate. AI is transforming the business landscape by automating processes, improving decision-making, and enhancing customer experiences. With the ability to analyze vast amounts of data, AI algorithms can uncover patterns and insights that humans might miss. From personalized marketing to predictive analytics, businesses are leveraging AI to streamline operations and drive growth. However, the integration of AI also raises important ethical and privacy concerns, as the technology collects and processes personal data at an unprecedented scale. Businesses must carefully consider these implications as they adopt AI solutions.",
        "metadata": {
            "source": "technology",
            "business_impact": True,
            "ai_applications":"automation, decision-making, customer experience",
            "data_analysis": True,
            "ethical_concerns": True,
            "privacy_issues": True,
            "growth_acceleration": True
            }
        },
        {"id": "doc_6", 
        "document": "Good health is important for longevity. Maintaining good health is crucial for living a long and fulfilling life. A balanced diet, regular exercise, and mental well-being are key components of overall health. Research has shown that individuals who prioritize healthy habits are more likely to live longer and enjoy a higher quality of life. Regular physical activity not only helps to prevent chronic diseases, but it also boosts mood, energy levels, and cognitive function. Good health is not just the absence of illness, but the presence of a lifestyle that supports vitality and longevity.",
        "metadata": {
            "source": "health",
            "importance_of_health": True,
            "healthy_habits":"balanced diet, exercise, mental well-being",
            "life_expectancy": "longer",
            "disease_prevention": True,
            "mood_boosting": True,
            "cognitive_benefits": True
            }
        },
        {"id": "doc_7", 
        "document": "A balanced diet is key to staying in good shape. A well-rounded diet rich in fruits, vegetables, lean proteins, and whole grains is essential for maintaining optimal physical health. Nutrients like vitamins, minerals, and antioxidants support bodily functions and boost the immune system. Moreover, staying hydrated and moderating sugar and processed food intake can prevent lifestyle-related diseases such as obesity, heart disease, and diabetes. Maintaining a balanced diet not only helps manage weight but also improves energy levels, mental clarity, and overall well-being.",
        "metadata": {
            "source": "health",
            "balanced_diet_essential": True,
            "nutrient_sources":"fruits, vegetables, lean proteins, whole grains",
            "disease_prevention": "obesity, heart disease, diabetes",
            "energy_boosting": True,
            "mental_clarity_improvement": True,
            "weight_management": True
            }
        },
        {"id": "doc_8", 
        "document": "AI is revolutionizing healthcare diagnostics. Artificial intelligence is significantly improving the way medical diagnoses are made. By analyzing medical images, genetic data, and patient histories, AI can assist doctors in identifying diseases more quickly and accurately. This technology helps to reduce human error, speed up diagnoses, and even predict potential health risks before they become severe. From detecting early-stage cancers to assessing cardiovascular risks, AI is playing a crucial role in improving patient outcomes and making healthcare more efficient.",
        "metadata": {
            "source": "technology-health",
            "ai_impact_on_healthcare": True,
            "diagnostic_accuracy": True,
            "healthcare_efficiency": True,
            "disease_detection": "cancer, cardiovascular risks",
            "early_detection": True,
            "risk_assessment": True
            }
        },
        {
        "id": "doc_9", 
        "document": "AI-powered applications in healthcare are helping doctors. With the integration of AI tools, healthcare professionals are now able to provide better care and treatment to patients. AI-powered applications assist doctors in making more informed decisions by analyzing large amounts of medical data, suggesting potential diagnoses, and recommending personalized treatment plans. These applications have been particularly useful in fields like radiology, pathology, and oncology, where the precision and speed of AI algorithms can save lives. Additionally, AI helps streamline administrative tasks, allowing healthcare providers to focus more on patient care.",
        "metadata": {
            "source": "technology-health",
            "ai_in_healthcare_applications": True,
            "doctor_assistance": True,
            "data_analysis": True,
            "personalized_treatment": True,
            "radiology_oncology_pathology": True,
            "administrative_efficiency": True
            }
        },
        {"id": "doc_10", 
        "document": "The impact of technology on sports is growing. Technology has become an integral part of modern sports, from training to performance analysis and fan engagement. Devices like wearables track athletes' performance in real-time, while advanced analytics tools help coaches and teams make better decisions. In addition, augmented reality and virtual reality are enhancing the fan experience, bringing stadiums and sports events directly into people's homes. As the integration of technology continues to evolve, sports organizations are looking for new ways to leverage innovation to improve both on-field performance and fan satisfaction.",
        "metadata": {
            "source": "sports-technology",
            "tech_in_sports": True,
            "performance_tracking": True,
            "fan_engagement": True,
            "real_time_analysis": True,
            "augmented_reality": True,
            "virtual_reality": True,
            "innovation_in_sports": True
            }
        }
    ]

    
    # Prepare the documents
    document_texts = [doc["document"] for doc in documents]
    document_ids = [doc["id"] for doc in documents]
    document_metadatas = [doc["metadata"] for doc in documents]

    print(f"Test Documents, IDs and Metadatas generated - ready for insert")

    print(f"DEBUG: all docs:\n{document_texts}\n\n\n")
    print(f"DEBUG: all ids:\n{document_ids}\n\n\n")
    print(f"DEBUG: all metadatas:\n{document_metadatas}\n\n\n")
	
    try:
        print(f"Trying insert...")
        pycollection.upsert(
            documents=document_texts,
            metadatas=document_metadatas,
            ids=document_ids
        )
        return jsonify({"message": "Documents added successfully to the collection."}), 200

    except Exception as e:
        print(f"Error inserting multiple test documents: {str(e)}")
        return jsonify({"error": str(e)}), 500















@app.route('/import-data-file', methods=['POST'])
def import_data_file():
    print(f"=====================================")
    print(f"Received Request: /import-data-file")
    print(f"=====================================")

    if persistentChromaClient is None:
        print(f"   FROM: /import-data-file   ChromaDB server is unavailable")
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Get the JSON data from the request
    data = request.get_json()

    # Extract collection name, records, and batch_limit from the incoming data
    passed_collection_name = data.get('collection_name')
    records = data.get('records', [])
    batch_limit = data.get('batch_limit', 100)  # Default to 100 if not provided

    print(f"Collection: {passed_collection_name}")
    print(f"Batch Limit: {batch_limit}")
    print(f"Number of Records: {len(records)}")

    # Get the collection and assign the embedding function
    try:
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"Collection {passed_collection_name} retrieved.")
    except Exception as e:
        print(f"Collection {passed_collection_name} not found.")
        return jsonify({'error': 'Collection not found. Create the collection first.'}), 500

    # Function to split the records into smaller batches
    def chunk_records(records, batch_size):
        for i in range(0, len(records), batch_size):
            yield records[i:i + batch_size]

    # Split the records into batches based on the batch_limit
    batches = chunk_records(records, batch_limit)

    # Loop through each record and extract id, document, and metadata
    #print(f"DEBUG - Looping through Records just to check...")
    #for record in records:
    #    record_id = record.get('id')
    #    document = record.get('document')
    #    metadata = record.get('metadata')
    #
    #    # Print the extracted variables to the console
    #    print(f"ID: {record_id}")
    #    print(f"Document: {document}")
    #    print(f"Metadata: {metadata}")


    # Process each batch separately
    for batch in batches:
        # Extract document ids and texts
        document_ids = [record.get('id') for record in batch]
        document_texts = [record.get('document') for record in batch]
        
        # Check if metadata is available
        document_metadatas = [record.get('metadata', {}) for record in batch]
        
        # If metadata is empty (default is empty dict), we won't include it in the upsert
        if all(not metadata for metadata in document_metadatas):
            try:
                print(f"Upserting batch of size {len(batch)} without metadata...")
                pycollection.upsert(
                    documents=document_texts,
                    ids=document_ids
                )
                print(f"Upsert for batch successful!")
            except Exception as e:
                print(f"Error during upsert: {str(e)}")
                # Handle the exception
                return jsonify({'error': f'Failed to upsert documents without metadata: {str(e)}'}), 500
        else:
            # When metadata is available, proceed with upserting it as well
            try:
                print(f"Upserting batch of size {len(batch)} with metadata...")
                pycollection.upsert(
                    documents=document_texts,
                    metadatas=document_metadatas,
                    ids=document_ids
                )
                print(f"Upsert for batch successful!")
            except Exception as e:
                print(f"Error during upsert: {str(e)}")
                # Check if the exception message contains "exceeds maximum batch size"
                if "exceeds maximum batch size" in str(e):
                    return jsonify({'error': str(e)}), 566
                return jsonify({'error': f'Failed to upsert documents: {str(e)}'}), 500
    
    # Return a success response once all batches are processed
    return jsonify({"message": "Data received and imported successfully!"}), 200
    
    
















@app.route('/gather-export-data', methods=['POST'])
def gather_export_data():
    print(f"######################################################")
    print(f"REQUEST RECEVIED: /gather-export-data")
    print(f"######################################################")

    # Check if ChromaDB client is available
    if persistentChromaClient is None:
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Get the JSON data from the request
    data = request.get_json()

    # Extract collection name and export choices from the incoming data
    print(f"Extracting data from JSON Payload...")
    passed_collection_name = data.get('collectionName')
    export_choices = data.get('exportOptions', {})

    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"Received Collection Name:\n{passed_collection_name}\n")
    print(f"Received Export Choices:\n{export_choices}")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    # Get the collection and assign the embedding function
    print(f"Checking collection exists...")
    try:
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"{passed_collection_name} found.")
    except Exception as e:
        print(f"Collection {passed_collection_name} not found.\n")
        return jsonify({'error': 'Collection not found. Create the collection first.'}), 500

    # Check if the collection is empty
    print(f"Checking Document Count...")
    if pycollection.count() == 0:
        print(f"No documents found in collection")
        return jsonify({'message': 'No documents found in collection'}), 200
    print(f"Collection contains documents to export. Proceeding...\n")

    # Gather the fields to include based on the user's selection
    include_fields = []

    print(f"Building Object for - Content Options")
    
    # Accessing the contentOptions from the nested structure
    content_options = export_choices.get('contentOptions', {})

    # Check if user selected specific fields
    if content_options.get('documents', False):
        include_fields.append('documents')
    if content_options.get('metadata', False):
        include_fields.append('metadatas')
    if content_options.get('embeddings', False):
        include_fields.append('embeddings')

    # If no fields were explicitly set to True or present, fallback to default behavior
    if not include_fields:
        # If none of the fields are provided, include 'documents' by default
        include_fields.append('documents')
        print(f"No Content Options were included - falling back to including documents as default")

    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"DEBUG: These are the include fields we'll use:\n{include_fields}")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    # Retrieve the results based on the selected export options
    print(f"Gathering Results...")
    results = pycollection.get(include=include_fields)



    print(f"Building Object for - Record Options")
    
    # Accessing the contentOptions from the nested structure
    record_options = export_choices.get('recordOptions', {})
    print(f"Record Options:        {record_options}")

    # Assigning corresponding values based on the record_options value
    if record_options == 'all_documents':
        record_options_values = export_choices.get('all_documents', {})
        print(f"Record Options Values: {record_options_values}\n")
    
    elif record_options == 'list_of_ids':
        record_options_values = export_choices.get('listOfIds', {})
        print(f"Record Options Values: {record_options_values}\n")
    
    elif record_options == 'from_to_record':
        record_options_values = export_choices.get('fromToRecord', {})
        print(f"Record Options Values: {record_options_values}\n")
    
    else:
        print("Invalid record option provided.\n")



    # Loop through the results based on the selected record options
    documents = []
    print(f"Looping through Results...")
    
    if record_options == 'all_documents':
        # Loop for all documents
        for i, doc_id in enumerate(results['ids']):
            # Prepare the document dictionary based on available fields
            document_data = {'id': doc_id}
            
            if 'documents' in include_fields:
                document_data['document'] = results['documents'][i]
            if 'metadatas' in include_fields:
                document_data['metadata'] = results['metadatas'][i]
            if 'embeddings' in include_fields:
                embedding = results['embeddings'][i]
                # Convert embedding to a serializable list if it's a NumPy array
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                document_data['embedding'] = embedding
            
            documents.append(document_data)
    

    elif record_options == 'list_of_ids':
        # Split the incoming string into a list of IDs
        list_of_ids = record_options_values.split(',')  # List of IDs in the payload, separated by commas
        
        for doc_id in list_of_ids:
            doc_id = doc_id.strip()
            # print(f"DEBUG 001 --- doc id: {doc_id} --- results['ids']: {results['ids']}")
            
            if doc_id in results['ids']:
                idx = results['ids'].index(doc_id)
                # print(f"DEBUG 002 --- doc_id {doc_id} found at index {idx}")
                document_data = {'id': doc_id}
                
                if 'documents' in include_fields:
                    document_data['document'] = results['documents'][idx]
                if 'metadatas' in include_fields:
                    document_data['metadata'] = results['metadatas'][idx]
                if 'embeddings' in include_fields:
                    embedding = results['embeddings'][idx]
                    # Convert embedding to a serializable list if it's a NumPy array
                    if isinstance(embedding, np.ndarray):
                        embedding = embedding.tolist()
                    document_data['embedding'] = embedding
    
                documents.append(document_data)


    elif record_options == 'from_to_record':
        # Loop for records starting from 'from' to 'to'
        from_record = int(record_options_values.get('from', 0))  # Convert 'from' to int
        to_record = int(record_options_values.get('to', len(results['ids'])))  # Convert 'to' to int
        print(f"DEBUG3 extracted from: {from_record} --- extracted to: {to_record}")

        try:
            # Slice the results to get only the desired range
            for i in range(from_record - 1, min(to_record, len(results['ids']))):
                doc_id = results['ids'][i]
                document_data = {'id': doc_id}
                
                if 'documents' in include_fields:
                    document_data['document'] = results['documents'][i]
                if 'metadatas' in include_fields:
                    document_data['metadata'] = results['metadatas'][i]
                if 'embeddings' in include_fields:
                    embedding = results['embeddings'][i]
                    # Convert embedding to a serializable list if it's a NumPy array
                    if isinstance(embedding, np.ndarray):
                        embedding = embedding.tolist()
                    document_data['embedding'] = embedding
                
                documents.append(document_data)
        
        except KeyError as e:
            print(f"KeyError: Missing expected key - {e}")
        except ValueError as e:
            print(f"ValueError: Invalid value encountered - {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    else:
        print("Invalid record option provided.\n")
    
    # Return the gathered documents as a response
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"Sending Response Data back to Web App")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    return jsonify({'documents': documents}), 200















@app.route('/export-data-to-json', methods=['POST'])
def export_data_to_json():
    print(f"######################################################")
    print(f"REQUEST RECEVIED: /export-data-to-json")
    print(f"######################################################")

    # Check if ChromaDB client is available
    if persistentChromaClient is None:
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Get the JSON data from the request
    data = request.get_json()

    # Extract collection name and export choices from the incoming data
    passed_collection_name = data.get('collectionName')
    export_choices = data.get('exportOptions', {})

    # Extract the output directory and filename from the incoming data
    output_directory = data.get('outputFolder')
    filename = data.get('outputFilename')

    # Validate output filename
    if not filename:
        return jsonify({'error': 'Filename is mandatory'}), 400

    # Validate output directory, if not, default to current directory
    if not output_directory:
        output_directory = os.getcwd()

    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"Received Collection Name:\n{passed_collection_name}\n")
    print(f"Received Export Choices:\n{export_choices}\n")
    print(f"Output Directory: {output_directory}")
    print(f"Filename:         {filename}")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")


    # Get the collection and assign the embedding function
    print(f"Checking collection exists...")
    try:
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"{passed_collection_name} found.")
    except Exception as e:
        print(f"Collection {passed_collection_name} not found.\n")
        return jsonify({'error': 'Collection not found. Create the collection first.'}), 500

    # Check if the collection is empty
    print(f"Checking Document Count...")
    if pycollection.count() == 0:
        print(f"No documents found in collection")
        return jsonify({'message': 'No documents found in collection'}), 200
    print(f"Collection contains documents to export. Proceeding...\n")


    # Gather the fields to include based on the user's selection
    include_fields = []

    print(f"Building Object for - Content Options")
    
    # Accessing the contentOptions from the nested structure
    content_options = export_choices.get('contentOptions', {})

    # Check if user selected specific fields
    if content_options.get('documents', False):
        include_fields.append('documents')
    if content_options.get('metadata', False):
        include_fields.append('metadatas')
    if content_options.get('embeddings', False):
        include_fields.append('embeddings')

    # If no fields were explicitly set to True or present, fallback to default behavior
    if not include_fields:
        # If none of the fields are provided, include 'documents' by default
        include_fields.append('documents')
        print(f"No Content Options were included - falling back to including documents as default")

    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"DEBUG: These are the include fields we'll use:\n{include_fields}")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")


    # Retrieve the results based on the selected export options
    print(f"Gathering Results...")
    results = pycollection.get(include=include_fields)


    documents = []
    print(f"Looping through Results...")


    print(f"Building Object for - Record Options")
    
    # Accessing the contentOptions from the nested structure
    record_options = export_choices.get('recordOptions', {})
    print(f"Record Options:        {record_options}")

    # Assigning corresponding values based on the record_options value
    if record_options == 'all_documents':
        record_options_values = export_choices.get('all_documents', {})
        print(f"Record Options Values: {record_options_values}\n")

        # Loop through all documents
        print(f"Exporting all documents.")
        for i, doc_id in enumerate(results['ids']):
            document_data = {'id': doc_id}
            
            if 'documents' in include_fields:
                document_data['document'] = results['documents'][i]
            if 'metadatas' in include_fields:
                document_data['metadata'] = results['metadatas'][i]
            if 'embeddings' in include_fields:
                embedding = results['embeddings'][i]
                # Convert embedding to a serializable list if it's a NumPy array
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                document_data['embedding'] = embedding
            
            documents.append(document_data)


    elif record_options == 'list_of_ids':
        record_options_values = export_choices.get('listOfIds', {})
        print(f"Record Options Values: {record_options_values}\n")
    
        # Export based on a list of IDs
        list_of_ids = record_options_values.split(',')
        print(f"Exporting based on provided list of IDs: {list_of_ids}")
        
        for doc_id in list_of_ids:
            doc_id = doc_id.strip()
            if doc_id in results['ids']:
                idx = results['ids'].index(doc_id)
                document_data = {'id': doc_id}
                
                if 'documents' in include_fields:
                    document_data['document'] = results['documents'][idx]
                if 'metadatas' in include_fields:
                    document_data['metadata'] = results['metadatas'][idx]
                if 'embeddings' in include_fields:
                    embedding = results['embeddings'][idx]
                    if isinstance(embedding, np.ndarray):
                        embedding = embedding.tolist()
                    document_data['embedding'] = embedding
    
                documents.append(document_data)

    elif record_options == 'from_to_record':
        record_options_values = export_choices.get('fromToRecord', {})
        print(f"Record Options Values: {record_options_values}\n")
    
        # Ensure 'from' and 'to' are integers
        try:
            from_record = int(record_options_values.get('from', 1))  # Convert 'from' to int
            to_record = int(record_options_values.get('to', len(results['ids'])))  # Convert 'to' to int
        except ValueError as e:
            print(f"Error: Invalid value for 'from' or 'to'. They must be integers. Error: {e}")
            return jsonify({'error': 'Invalid value for "from" or "to". They must be integers.'}), 400
    
        print(f"DEBUG: Extracted from: {from_record} --- Extracted to: {to_record}")
    
        try:
            # Slice the results to get only the desired range
            for i in range(from_record - 1, min(to_record, len(results['ids']))):
                doc_id = results['ids'][i]
                document_data = {'id': doc_id}
                
                if 'documents' in include_fields:
                    document_data['document'] = results['documents'][i]
                if 'metadatas' in include_fields:
                    document_data['metadata'] = results['metadatas'][i]
                if 'embeddings' in include_fields:
                    embedding = results['embeddings'][i]
                    if isinstance(embedding, np.ndarray):
                        embedding = embedding.tolist()
                    document_data['embedding'] = embedding
                
                documents.append(document_data)
    
        except KeyError as e:
            print(f"KeyError: Missing expected key - {e}")
        except ValueError as e:
            print(f"ValueError: Invalid value encountered - {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
    else:
        print("Invalid record option provided.\n")


    # Define the full output file path, combining output directory and filename
    output_path = os.path.join(output_directory, filename)

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            print(f"Created missing output directory: {output_directory}")
        except Exception as e:
            print(f"Error creating output directory: {e}")
            return jsonify({'error': f'Failed to create directory: {output_directory}'}), 500

    # Write the documents to the file in JSON format
    try:
        with open(output_path, 'w') as json_file:
            json.dump(documents, json_file, indent=2)
        print(f"Data successfully written to {output_path}")
        return jsonify({'message': f'Data successfully exported to {output_path}'}), 200
    except Exception as e:
        print(f"Error writing to file: {e}")
        return jsonify({'error': 'Failed to write data to file'}), 500
















@app.route('/count-documents', methods=['GET'])
def count_collection_documents():
    if persistentChromaClient is None:
        # If the ChromaDB client is not initialized, return an error message
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Get the collection name from the URL query parameters
    passed_collection_name = request.args.get("collection_name")

    if not passed_collection_name:
        return jsonify({'error': 'Collection name not provided'}), 400
    print(f"Passed Collection Name: {passed_collection_name}")

    try:
        # Attempt to get the collection
        pycollection = persistentChromaClient.get_collection(passed_collection_name)

        # Check if the collection is empty
        print(f"Checking if '{passed_collection_name}' has any documents")
        collection_count = pycollection.count()
        if collection_count == 0:
            print(f"No documents found in collection")
            return jsonify({'document_count': 0}), 200

        # Return the count of documents
        print(f"Documents found")
        print(f"Count: {collection_count}")
        return jsonify({'document_count': collection_count}), 200

    except Exception as e:
        # Handle any error that occurs during the ChromaDB request
        return jsonify({'error': f"Error accessing collection {passed_collection_name}: {str(e)}"}), 500













@app.route('/count-all-documents', methods=['GET'])
def count_all_documents():
    print(f"==========================================")
    print(f"Recevied request for: /count-all-documents")
    print(f"==========================================")

    if persistentChromaClient is None:
        print(f"   FROM: /count-all-documents   ChromaDB server is unavailable - Error 500")
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    try:
        # Retrieve all collections
        print(f"   FROM: /count-all-documents   Fetching all Collections...")
        allCollections = persistentChromaClient.list_collections()
        print(f"   FROM: /count-all-documents   Collections Fetched")

        # Initialize the total document count
        total_document_count = 0

        if allCollections and isinstance(allCollections[0], str):
            # New version: collections are strings
            for collection in allCollections:
                try:
                    # Attempt to get the collection
                    tempCollection = persistentChromaClient.get_collection(collection)

                    # Avoid trying to count documents in empty or corrupted collections
                    if tempCollection.count() is not None:
                        document_count = tempCollection.count()
                        total_document_count += document_count
                    else:
                        # Handle the case where collection count is invalid or empty
                        print(f"   FROM: /count-all-documents   Collection {collection} is invalid or empty.")
                except Exception as e:
                    print(f"   FROM: /count-all-documents   Error accessing collection {collection}: {str(e)}")
        else:
            # Old version: collections are objects
            for collection in allCollections:
                try:
                    collection_name = collection.name
                    collection_id = collection.id

                    # Avoid trying to count documents in empty or corrupted collections
                    if collection.count() is not None:
                        document_count = collection.count()
                        total_document_count += document_count
                    else:
                        print(f"   FROM: /count-all-documents   Collection {collection_name} is invalid or empty.")
                except Exception as e:
                    print(f"   FROM: /count-all-documents   Error accessing collection {collection.name}: {str(e)}")

        # Return the total document count as a JSON response
        print(f"   FROM: /count-all-documents   Total Document Count: {total_document_count}")
        print(f"   FROM: /count-all-documents   Returned Count as JSON")
        return jsonify({'total_document_count': total_document_count})

    except Exception as e:
        # Handle any error that occurs during the ChromaDB request
        print(f"   FROM: /count-all-documents   Error counting Total Documents from all Collections: {str(e)}")
        return jsonify({'error': str(e)}), 500










    
@app.route('/api/get-all-documents', methods=['POST'])
def get_all_documents():

    # Get the collection name from the request body
    collection_name = request.json.get("collection_name")

    if not collection_name:
        return jsonify({'error': 'Collection name not provided'}), 400
    
    try:
        pycollection = persistentChromaClient.get_collection(collection_name)
    except Exception as e:
        return jsonify({'error': f"Collection {collection_name} not found: {str(e)}"}), 500

    # Check if the collection is empty
    if pycollection.count() == 0:
        return jsonify({'message': 'No documents found in collection'}), 200

    # Fetch the documents and their embeddings
    results = pycollection.get(include=["embeddings", "documents", "metadatas"])

    documents = []
    for i, doc_id in enumerate(results['ids']):
        # Convert embedding to a serializable list
        embedding = results['embeddings'][i].tolist() if isinstance(results['embeddings'][i], np.ndarray) else results['embeddings'][i]
        
        documents.append({
            'id': doc_id,
            'document': results['documents'][i],
            'metadata': results['metadatas'][i],
            'embedding': embedding
        })

    return jsonify({'documents': documents}), 200










# Route to handle document deletion
@app.route('/api/delete-document', methods=['POST'])
def delete_document():
    # Get the data from the POST request
    data = request.json
    
    # Extract the document ID and collection name from the request
    doc_id_to_delete = data.get('id')
    collection_name = data.get('collection_name')

    if not doc_id_to_delete or not collection_name:
        return jsonify({"error": "Document ID and collection name are required."}), 400
    
    try:
        # Get the Collection and assign the Embedding Function to it
        pycollection = persistentChromaClient.get_collection(collection_name)
        print(f"Collection {collection_name} found and retrieved.")
    except Exception as e:
        return jsonify({"error": f"Collection {collection_name} not found: {str(e)}"}), 500
    
    try:
        # Delete the document
        pycollection.delete([doc_id_to_delete])
        print(f"Document with ID {doc_id_to_delete} has been deleted.")
        return jsonify({"message": f"Document with ID {doc_id_to_delete} has been deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete document: {str(e)}"}), 500










# Route to handle document deletion
@app.route('/api/delete-all-documents', methods=['POST'])
def delete_all_documents():

    if persistentChromaClient is None:  # Assuming client is defined elsewhere
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Extract collection data from the request's JSON payload
    data = request.json
    passed_collection_name = data.get("collection_name")

    # Debugging: print all extracted values to the server's log
    print(f"Received data:\ncollection_name={passed_collection_name}")

    # Ensure collection name is provided
    if not passed_collection_name:
        return jsonify({'error': 'Collection name required'}), 400

    try:
        # Try getting the collection first (doesn't raise exception if collection is not found)
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"Existing Collection '{passed_collection_name}' found.")

    except Exception as e:
        # Handle unexpected errors
        print(f"Collection '{passed_collection_name}' Not Found, aborting...\n{str(e)}")
        return jsonify({"message": f"Collection '{passed_collection_name}' Not Found, aborting..."}), 404

    # Now extract the ids, documents, and metadata into object variables
    old_collection_metadata = pycollection.metadata

    # Fetch the documents and their metadata
    old_results = pycollection.get(include=["documents", "metadatas"])

    old_doc_ids = old_results['ids']
    old_documents = old_results['documents']
    old_document_metadata = old_results['metadatas']

    # Now Delete the Collection to free up its name 
    print(f"Deleting Collection to Free Up Collection Name...")
    try:
        persistentChromaClient.delete_collection(name=passed_collection_name)
    except Exception as e:
        print(f"Error deleting collection: {str(e)}")
        return jsonify({'error': f'Failed to delete collection: {str(e)}'}), 500

    # Now we need to create a new one with the same parameters
    try:
        if old_collection_metadata:  # If metadata is not empty
            pycollection_new = persistentChromaClient.create_collection(
                passed_collection_name,
                embedding_function=pyEmbedFunction,
                metadata=old_collection_metadata
            )
        else:
            pycollection_new = persistentChromaClient.create_collection(
                passed_collection_name,
                embedding_function=pyEmbedFunction
            )
        print(f"All Documents Deleted from '{passed_collection_name}' successfully.")
        return jsonify({"message": f"Documents deleted and collection recreated for '{passed_collection_name}' successfully."}), 200

    except Exception as e:
        print(f"Failed to Recreate collection when deleting all documents: {str(e)}")
        return jsonify({'error': f'Failed to Recreate collection when deleting all documents: {str(e)}'}), 500

















@app.route('/api/query-documents', methods=['POST'])
def query_documents():
    # Get the data from the request body
    query_data = request.get_json()

    if not query_data:
        return jsonify({'error': 'No query data provided'}), 400

    # Extract data from the request
    passed_collection_name = query_data.get("collection_name")
    query_text = query_data.get("query_text")
    num_of_returned_results = query_data.get("num_of_results", 5)

    # Attempt to extract document filters, but handle the case where they might not exist
    passed_where_document_filters = query_data.get("where_document")

    if passed_where_document_filters is None:
        print(f"No Document filters were passed, continuing without....")
    else:
        print(f"Passed Document filters (as string):\n{passed_where_document_filters}")

    # Attempt to extract metadata filters, but handle the case where they might not exist
    passed_where_metadata_filters = query_data.get("where")

    if passed_where_metadata_filters is None:
        print(f"No Metadata filters were passed, continuing without....")
    else:
        print(f"Passed Metadata filters (as string):\n{passed_where_metadata_filters}")

    if not passed_collection_name or not query_text:
        return jsonify({'error': 'Missing required fields (passed_collection_name, query_text)'}), 400

    try:
        # DEBUG 
        print(f"\n\n------------------------")
        print(f"Data from JSON payload:")
        print(f"------------------------")
        print(f"passed Collection Name:          {passed_collection_name}")
        print(f"passed Query Text:               {query_text}")
        print(f"passed Num of Results:           {num_of_returned_results}")
        print(f"passed Where Document Filters:   {passed_where_document_filters}")
        print(f"passed Where Metadata Filters:   {passed_where_metadata_filters}")
        print(f"\n")

        # Dynamically retrieve the collection
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"Collection {passed_collection_name} found and retrieved.")

    except Exception as e:
        return jsonify({'error': f"Collection {passed_collection_name} not found: {str(e)}"}), 500

    try:
        # Perform a vector search for the most similar documents in the collection
        print(f"Querying collection with the following parameters:")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Query Text:\n{query_text}\n")
        print(f"Number of Results:        {num_of_returned_results}")
        print(f"Where Document Filters:   {passed_where_document_filters}")
        print(f"Where Metadata Filters:   {passed_where_metadata_filters}")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

        # Construct the query parameters
        query_params = {
            "query_texts": [query_text],
            "n_results": num_of_returned_results
        }

        # Add filters dynamically if they exist
        if passed_where_document_filters:
            query_params["where_document"] = passed_where_document_filters
        if passed_where_metadata_filters:
            query_params["where"] = passed_where_metadata_filters

        # Execute the query with the constructed parameters
        results = pycollection.query(**query_params)

        # Print the raw query results for debugging
        # print(f"Query Results:\n{results}")

        # INSTEAD Use pprint to make it look better in the console
        pprint.pprint(f"Query Results:{results}")

        # Check if any results were found
        if not results['documents']:
            return jsonify({'error': 'No results found for the query'}), 404

        # Extract the results into a list of dictionaries
        query_results = []
        for i, result in enumerate(results['documents']):
            query_results.append({
                'result_index': i,
                'similarity_score': results['distances'][i],
                'doc_id': results['ids'][i],
                'metadata': results['metadatas'][i],
                'document': result
            })

        return jsonify({'results': query_results}), 200

    except Exception as e:
        # Handle errors during query execution
        return jsonify({'error': f"Error querying documents: {str(e)}"}), 500










@app.route('/api/update-document', methods=['POST'])
def update_document():
    try:
        # Retrieve JSON data from request
        data = request.get_json()
        
        # Extract required fields
        passed_collection_name = data.get('collection_name')
        passed_doc_id = data.get('doc_id')
        passed_document_content = data.get('document_content')
        
        # Optional: Retrieve metadata if provided
        passed_metadata = data.get('metadata', None)
        
        # If metadata is a string, attempt to convert it to a dictionary
        if passed_metadata and isinstance(passed_metadata, str):
            try:
                passed_metadata = json.loads(passed_metadata)
            except json.JSONDecodeError:
                return jsonify({"error": "Metadata is not a valid JSON string"}), 400
        
        # Get the Collection and assign the Embedding Function to it
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"Collection {passed_collection_name} found and retrieved.")
        

        # Fetch all the documents and their embeddings
        #results = pycollection.get(include=["documents"])

        # Find the document with the specific ID
        #doc_found = False
        #for i, loop_doc_id in enumerate(results['ids']):
        #    if loop_doc_id == passed_doc_id:
        #        doc_found = True
        #        print(f"Matching Doc ID found: {passed_doc_id}")
        #        break
        #
        #if not doc_found:
        #    # Document with the given ID doesn't exist
        #    print(f"Error: Document with ID {passed_doc_id} does not exist.")
        #    return jsonify({"message": f"Error: Document with ID {passed_doc_id} does not exist."}), 400

        # Update the document content (mandatory part)
        #pycollection.upsert([passed_doc_id])

       
        try:
            # Check if metadata was provided and update if needed
            if passed_metadata:
                pycollection.upsert(
                    documents=[passed_document_content],
                    metadatas=[passed_metadata],
                    ids=[passed_doc_id]
                )
            else:
                pycollection.upsert(
                    documents=[passed_document_content],
                    ids=[passed_doc_id],
                    metadatas=[None] 
                )
        
        except Exception as e:
            # If there is an error, return error message with the exception details
            return jsonify({
                "message": f"Error Updating Document: {str(e)}",
                "status_code": 500
            }), 500

        return jsonify({"message": f"Document with ID {passed_doc_id} has been updated successfully."}), 200


    except Exception as e:
        return jsonify({"error": f"Failed to update document: {str(e)}"}), 500













@app.route('/visualize-collection', methods=['POST'])
def visualize_my_collection():

    if persistentChromaClient is None:  # Assuming client is defined elsewhere
        return jsonify({'error': 'ChromaDB server is unavailable'}), 500

    # Parse the URL
    chromaviz_parsed_url = urlparse(address_flask)
    print(f"Flask Address:\n{chromaviz_parsed_url}")

    # Extract the server address and port number
    #CHROMAVIZ_HOST = chromaviz_parsed_url.hostname
    CHROMAVIZ_PORT = chromaviz_parsed_url.port + 1

    print(f"Global variable at start of Visualisation 2 Chroma Viz Port:{CHROMAVIZ_PORT}")

    # Extract collection data from the request's JSON payload
    data = request.json
    passed_collection_name = data.get("collection_name")

    # Debugging: print all extracted values to the server's log
    print(f"Received data:\ncollection_name={passed_collection_name}")

    # Ensure collection name is provided
    if not passed_collection_name:
        return jsonify({'error': 'Collection name required'}), 400

    # Check Collection Exists
    try:
        # Try getting the collection first (doesn't raise exception if collection is not found)
        pycollection = persistentChromaClient.get_collection(passed_collection_name)
        print(f"=======================================================")
        print(f"Existing Collection '{passed_collection_name}' found.")
        print(f"=======================================================")
    except Exception as e:
        # Handle unexpected errors
        print(f"========================================================================")
        print(f"Collection '{passed_collection_name}' Not Found, aborting...\n{str(e)}")
        print(f"========================================================================")
        return jsonify({"message": f"Collection '{passed_collection_name}' Not Found, aborting..."}), 404


    # BEFORE LOADING CHROMAVIZ - WE NEED TO AMEND THE ENDPOINT IN THE JAVASCRIPT FILE SO IT DOESNT CONFLICT WITH OTHER PORTS 
    # THERES ONLY 1 X MENTION ON IT IN THE .JS FILE, SO THE BELOW DOES A FIND AND REPLACE 

    # Path to the ChromaViz JavaScript file, relative to THIS script 
    chromaviz_js_file_path = './chromaviz/index-351494fc.js'

    # Define the pattern to match the fetch URL and replace it - anything that starts 'fetch(https://' and ends with '/data")'
    pattern = r'fetch\("http://[^"]+/data"\)'

    # The new URL to Host ChromaViz On
    print(f'Overwriting URL in .JS File With:\nfetch("http://{CHROMAVIZ_HOST}:{CHROMAVIZ_PORT}/data")')
    new_url = f'fetch("http://{CHROMAVIZ_HOST}:{CHROMAVIZ_PORT}/data")'

    # Open the file in read mode
    with open(chromaviz_js_file_path, 'r') as file:
        file_content = file.read()
    
    # Replace the old URL with the new one
    updated_content = re.sub(pattern, new_url, file_content)
    
    # Open the file in write mode to save the changes
    with open(chromaviz_js_file_path, 'w') as file:
        file.write(updated_content)
    
    print(f"-------------------------------------------------------------------------------------")
    print(f"Endpoint in ChromaViz Javascript File:\n'{chromaviz_js_file_path}'\nHas been updated.")
    print(f"-------------------------------------------------------------------------------------")
    




    # SIMILARLY - WE NEED TO AMEND THE ENDPOINT IN THE CHROMVIZ INDEX.HTML TO DYNAMICALLY POINT BACK TO CHROMA FLOW STUDIO  
    # THERES ONLY 1 X MENTION of "window.location.href" SO WE'LL TARGET THAT 

    # Path to the ChromaViz index.html, relative to THIS script 
    chromaviz_index_html_path = './chromaviz/index.html'

    # Define the pattern to match the fetch URL and replace it - anything that starts 'fetch(https://' and ends with '/data")'
    pattern = r'(<a href="http:\/\/)[^"]+(" target="_self">)'

    # The new URL to Host ChromaViz On
    new_url = f'<a href="http://{CHROMAVIZ_HOST}:{CHROMAVIZ_PORT - 1}" target="_self">'
    print(f"Overwriting URL in index.html File With: {new_url}")

    # Open the file in read mode
    with open(chromaviz_index_html_path, 'r') as file:
        file_content = file.read()
    
    # Replace the old URL with the new one
    updated_content = re.sub(pattern, new_url, file_content)
    
    # Open the file in write mode to save the changes
    with open(chromaviz_index_html_path, 'w') as file:
        file.write(updated_content)
    
    print(f"-------------------------------------------------------------------------------------")
    print(f"Endpoint in ChromaViz index.html:\n'{chromaviz_index_html_path}'\nHas been updated.")
    print(f"-------------------------------------------------------------------------------------")
    

    # Finally, Run ChromaViz to Visualize the Data
    visualize_collection(pycollection, CHROMAVIZ_PORT)

    return jsonify({"message": "Visual Data is Generating... Please Wait..."}), 200














@app.route('/clear-console')
def clear_console():
    # This command clears the terminal/console where the Flask server is running
    os.system('cls')
    return "Flask Console Cleared!"








# Run the app locally
if __name__ == '__main__':
    # Start a separate thread to open the browser
    threading.Thread(target=open_browser).start()

    # Disable Flask's debugger reloader (prevents it from re-running the connection check)
    app.run(debug=True, port=port_flask, use_reloader=False)
