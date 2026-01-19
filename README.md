# ChromaFlowStudio
**Python GUI Client For ChromaDB**<br>
_Full Management and Visualisations_

![image](https://github.com/user-attachments/assets/61e12d9e-7d91-41e3-bb93-94158b2faa18)

![image](https://github.com/user-attachments/assets/b24f0fef-0834-4038-8a23-5a21e115089e)

![image](https://github.com/user-attachments/assets/0cd4a43e-5079-4232-8c3a-38271e553699)

Introducing Chroma Flow Studio.
<br>

The swiss-army knife to ChromaDB - with every management task at your fingertips! <br>
Promising to be **the most comprehensive ChromaDB GUI client available!**<br>
<br>
Small changes to allow to work with ChromaDB > v7<br>

~~~~~~~~~~~~~
Intended for Windows OS
But could be adapted for linux by creating the equivilant .sh scripts instead of .bat files
~~~~~~~~~~~~~
<br>

Whether you're a total beginner or veteran,<Br>
The aim is to lower the barrier to entry, and make learning, using, or developing with ChromaDB fast, easy, <br>
and,<br>
<br>
dare I say, even a little fun?<Br>
<br>
<br>

A **Pure Python** ChromaDB Client,<br>
Using Flask HTML and javascript for the Front End UI.<br>
Persists ChromaDB Data to disk by default<br>
<Br>


With over 15,000 Lines of code, this is one mighty App! <bR>
Here's a peek at what Chroma Flow Studio can do for you: <br>

- **Dashboard Overview:**
  Get a clear, concise snapshot of your entire ChromaDB setup right from the dashboard.
  
- **Collections Page:**
  View all your collections, and perform essential actions like adding, copying, cloning, or deleting them – all with just a click. Plus, we've got handy templates for metadata and default settings to help you hit the ground running without the fuss.
  
- **Add Documents with Ease:**
  No need to manually assign IDs! Documents can be added with auto-generated IDs, plus customizable metadata templates to save you time.
  
- **Bulk Document Imports and Updates:**
  Need to add or update a lot of documents at once? No problem. Import documents in bulk with a simple JSON file, or update them in bulk too.
  
- **Document Management:**
  Whether you need to update a single document, copy one, or delete them (individually, in groups, or all at once), Chroma Flow Studio makes it easy to manage your documents at lightning speed.
  
- **Document Overview:**
  See all the important details of your documents – from IDs and contents to metadata and embeddings. Want to filter, edit, delete, or review your documents? It's all at your fingertips
  
- **Document Export:**
  You can easily export documents to JSON, select the content and records you want, and even choose where to send them. Simple as that!
  
- **Similarity Searches:**
  Run similarity searches - including the ability to filter for both documents and metadata. Precision searching has never been easier.
  
- **Quick Embedding Model Swaps:**
  Test out different embedding models and compare their performance in mere seconds – perfect for finding the best one for your use case.
  
- **Cloning and Re-Embedding:**
  Clone your data and re-embed it with a different model – a feature that ChromaDB's Python library doesn't even support natively, but I've added it here just for you!
  
- **Bulk Deletions**
  Another feature that ChromaDB's Python library doesn't support natively - Clear all documents from a Collection instantly in just a click!
  
- **Flask Server Configuration:**
  Easily configure the Flask server endpoint to suit your needs, with the flexibility to point to any ChromaDB SQLite file. Switching between them is as easy as flipping a switch.
  
- **Proxy Support:**
  Using a proxy? No problem! Chroma Flow Studio supports that too.
  
- **Built-in Tools:**
  UUIDs, Hashes, Timestamps, Embedding generation – all available on the fly. Need to generate synthetic data for testing? It's all ready to go. Plus, there's a handy token counter built right in.

- **Visualize your Data!:**
  Get a graphical representation of your collections by Visualizing your data points! (NOTE: requires chrome/firefox/edge to render, if you have issues, try other browsers)
  
- **Python Code Snippets:**
  At the bottom of the Collections / Documents / Update / Search Pages are Python code snippets showing how to perform those actions programatically. Just copy, paste, run, and done!
  
- **And More!**

Chroma Flow Studio brings everything you need in one place, wrapped in a simple UI,
with a range of tools built-in, detailed overviews, and embedded knowledge, everything is just a click away.

~~~~~~~~~~~~~~~
ChromaFlowStudio supports ChromaDB Versions 0.5.20+
including latest version (ChromaDB 0.6.1 as of writing this)
(if later versions of chromadb introduce a breaking change, try downgrading)
~~~~~~~~~~~~~~~
<Br>

So...<bR>
Enough talk <bR>
How do we get started? <br>
<br>

**Pre-Requisites:**
~~~~~~~~~~~~~~~~~~~~~~~~~
- ~300MB for the basic app, but ~1.7GB in Drive Space for all other libraries and dependancies (mainly torch)
- Python 3.10 (may also work in 3.11, but hasnt been tested)
- Pip 24.3.1
- VENV installed (optional, but HIGHLY, and STRONGLY recommended)
- ChromaDB 0.5.20+ to support hnsw config specified in metadata - tested and works on v0.6.1 too (latest as of writing this)
- Chroma-hnswlib==0.7.6+
- Set environment variable CHROMA_SERVER_CORS_ALLOW_ORIGINS=["*"]
- Check the requirements.txt for package version info
~~~~~~~~~~~~~~~~~~~~~~~~~
<Br>
<br>
<br>


**Install Instructions: (EASY METHOD)**

1. Download the **ChromaFlowStudio#.#.#.####.zip** _(latest version)_ <Br>
and extract to any folder you like, for example **C:\Program Files\ChromaDB\ChromaFlowStudio** <br>
<Br>

2. Edit the **VENV_Create.bat** <br>
Amend the pythonPath to YOUR python 3.10 folder _(where python.exe is located)_ <br>
<Br>

3. Run the **VENV_Create.bat** to create the Virtual Environment<br>
_(it'll create a new 'venv' folder for you)_ <br>
<Br>

4. Run the **Install.bat** <br>
Let it install everything in the requirements.txt <br>
<Br>

5. Use the **Run.bat** to launch Chroma Flow Studio!<br>
<Br>

<br>
<br>
<br>

**OR**

**Install Instructions: (MANUAL METHOD)**

1. Download the **ChromaFlowStudio#.#.#.####.zip** _(latest version)_ <Br>
and extract to any folder you like, for example **C:\Program Files\ChromaDB\ChromaFlowStudio** <br>
<Br>


2. Open a new command prompt window (cmd.exe)<Br>
change to the directory where you decided to unzip ChromaFlowStudio:
~~~~~~~~~~~~~~~~~~~~~
cd "C:\Path\to\where\you\decided\to\install"
~~~~~~~~~~~~~~~~~~~~~
For example:
~~~~~~~~~~~~~~~~~~~~~
cd "C:\Program File\ChromaDB\ChromaFlowStudio"
~~~~~~~~~~~~~~~~~~~~~
<Br>


3. assuming you already have python 3.10 installed,<br>
enter this command and press enter _(this creates the virtual environment)_:
~~~~~~~~~~~~~~~~~~~~~
python -m venv venv
~~~~~~~~~~~~~~~~~~~~~
<Br>


4. activate the virtual environment with this command: <Br>
~~~~~~~~~~~~~~~~~~~~~
venv\Scripts\activate.bat
~~~~~~~~~~~~~~~~~~~~~
<Br>


5. Upgrade pip first<br>
~~~~~~~~~~~~~~~~~~~~~
venv\Scripts\python.exe -m pip install --upgrade pip
~~~~~~~~~~~~~~~~~~~~~
<Br>


6. Install the requirements.txt<br>
~~~~~~~~~~~~~~~~~~~~~
venv\Scripts\python.exe -m pip install -r requirements.txt
~~~~~~~~~~~~~~~~~~~~~
<Br>

7. Launch Chroma Flow Studio:<br>
~~~~~~~~~~~~~~~~~~~~~
venv\Scripts\python.exe" app.py
~~~~~~~~~~~~~~~~~~~~~
<Br>

<br>
<Br>
<br>

**Getting Started with Chroma Flow Studio**<br>

**Creating Collections:** <Br>
On the collections page, creating a collection is simple and easy. <Br>
Collection names are autogenerated for convenience, as are the configuration fields and metadata—but you can still configure all of them. <Br>
There are options to copy a collection's details to a new empty collection, or clone an existing collection, including all its data. <Br>
Deleting collections one at a time or in bulk is just a single button click. <Br>
<br>
![image](https://github.com/user-attachments/assets/914df285-d343-450b-b4a7-3352260c139f)
<br>
![image](https://github.com/user-attachments/assets/a35fe74d-5e7e-4a5c-a120-a00c2d03e80d)
<br>
<br>

**Adding Documents:** <Br>
You can add documents one at a time, including setting metadata. <br>
There are quick buttons to set metadata templates with many useful attributes you could apply for a document. <br>
Or, import documents in bulk. <br>
You can also update documents individually or in bulk. <br>
<br>
![image](https://github.com/user-attachments/assets/606ef84e-74a7-4b75-a5d3-1c5299f14891)
<br>
![image](https://github.com/user-attachments/assets/d94ca657-776a-426f-97af-c6dd64564e02)
<br>
<br>

**Viewing Documents:** <Br>
On the view documents page:<br>
- select your collection,
- apply filters,
- choose how many results to return,
and quickly see your document IDs, contents, metadata, and embeddings.<br>
<br>

![image](https://github.com/user-attachments/assets/38a3ef9e-d2bd-4eaf-9da0-161d7e7b2b7b)

<br>
<br>

**Searching:** <br>
Similarity search is simple and easy to use. <bR>
Plus, there are filter options for specific document contents and/or metadata fields to create dynamic and specific queries. <br>
Quick buttons are provided to create your desired filters with speed, with full customization. <br>
<br>
![image](https://github.com/user-attachments/assets/87fb30df-f5da-4d84-af74-4d70b4fcbd8a)
<br>
![image](https://github.com/user-attachments/assets/91cb4b59-9662-432c-b05d-5e0d868f72a3)
<br>
![image](https://github.com/user-attachments/assets/4b875fcb-c544-4eec-84fb-d4ae0276043a)
<br>
![image](https://github.com/user-attachments/assets/cc5a8072-6743-4d28-a220-66607b6be45c)
<Br>
<br>

**Visualize Data:** <br>
The Visualize page gives you a graphical representation of your collections so you can see how similar groups of documents are to one another. <br>
It's also helpful to see how different embedding models generate different visuals on the same data, as a quicker way to see if they’re more accurate for your use case. <bR>
<Br>
![image](https://github.com/user-attachments/assets/5efb9c5b-9598-4558-ac4b-62792db290d1)
<br>
<br>

**Exporting Data:** <br>
The export page lets you pick documents, metadata, embeddings, or all of them to export into a JSON file. <br>
You can preview what data would be exported before committing to it <br>
And configure the filename and output directory. <br>
Simple. <br>
<br>
![image](https://github.com/user-attachments/assets/eae76b1f-5f18-4117-85b2-1ef1b9bf4b23)
<br>
![image](https://github.com/user-attachments/assets/f9822bfd-61bd-465d-bf7d-779a1b2f9570)
<Br>
![image](https://github.com/user-attachments/assets/bc40dad2-cc83-4db6-aa36-5e33241a37ea)
<br>
<Br>



**Embedded Python Snippets** <Br>
At the bottom of the Collections / Documents / Update / Search Pages<Br>
are Python code snippets showing how to perform those actions programatically.<Br>
Just copy, paste, run, and done!<br>
<br>
![image](https://github.com/user-attachments/assets/0a3255ac-e58c-42d2-bfeb-a554eaae7d94)
<br>
![image](https://github.com/user-attachments/assets/5f918b21-d1fd-400d-b1d3-6d8c7cc61583)
<bR>
![image](https://github.com/user-attachments/assets/d85927ad-f38f-41ea-88a2-e57a46ed1ace)
<br>
![image](https://github.com/user-attachments/assets/35549cd5-0c4d-4f44-bb7c-deb166b59f71)
<br>
<br>


**Configure Flask Server and ChromaDB Database File** <Br>
on the Settings page, you can change the port that Flask runs on if it conflicts with anything else you're running<br>
You can also configure the path the the ChromaDB file - if one doesnt exist, it creates a blank one automatically, but can be used to point to existing chroma.sqlite3 files.<br>
Also, if you're using a proxy, it can be set - leave field blank if proxy is not used.<br>
<br>
![image](https://github.com/user-attachments/assets/05125d3e-360c-423c-b0b1-1896abf3f574)
<br>
<br>
**Configure a prefix for collection names**<br>
Ability to set a prefix used in the Auto-name generation during the collection creation process.<br>
Theres also language setting, that if configured, and if you specify a "languague":"" json metadata key, it automatically uses this value<br>
<br>
![image](https://github.com/user-attachments/assets/f32d6872-1db4-490e-8435-f30495d43b48)
<br>
<br>

**Customize the Embedding Model**<Br>
Select from a range of embedding models (as the default one that chroma installs with isn't great)<br>
theres plenty to choose from, but you can also specify a custom one from hugging face (not all will work, its trial and error)<br>
<br>
![image](https://github.com/user-attachments/assets/e3d714dc-62fe-4f81-b85a-0f8937145c4e)
<br>
![image](https://github.com/user-attachments/assets/e9379811-9b3e-401b-bff1-9237e10c97c8)
<br>
<br>

**import data in bulk**<br>
upload a josn file to import 1000s x documents at once rapidly!<br>
<br>
![image](https://github.com/user-attachments/assets/1fbdfcd9-8570-40dd-81da-d2f109f435b2)
<br>
<br>
<br>
<br>
<br>

**Links to Other Chroma DB GUI Clients**<br>
heres a list of other GitHub projects for Chroma GUI clients:<br>
<br>

**ChromaDash** <Br>
https://github.com/coffeecodeconverter/ChromaDash <Br>
This is a HTTP Client UI, only works if you also have a HTTP ChromaDB Server running (default listens on 127.0.0.1:8000). <br>
Ignore, if you're interested in python clients. <br>
<br>

**Chroma UI** <br>
https://github.com/thakkaryash94/chroma-ui <br>
https://chroma-ui.vercel.app/ <br>
This is a HTTP Client UI, only works if you also have a HTTP ChromaDB Server running (default listens on 127.0.0.1:8000). <br>
Ignore, if you're interested in python clients. <br>
<br>

**Chroma Peek** <Br>
https://github.com/Pawandeep-prog/chroma-peek <br>
A Python client for quickly viewing documents in your collections. Can run basic queries for similarity search <br>
<br>

**Chromagraphic** <br>
https://github.com/msteele3/chromagraphic <BR>
A Python client for quickly viewing documents in your collections. Can add documents, but not search them. <Br>
<br>

**Vector Admin** <Br>
https://github.com/Mintplex-Labs/vector-admin <br>
This is a universal management tool that supports Chroma and pinecone databases, with the aim to support more in future. <bR>
Good UI that aims to simplify managing multiple vector databases through a unified interface. <br>
<br>

**Chroma DB Viewer** <br>
https://github.com/ill-yes/chromadb-viewer <br>
This application is a simple ChromaDB viewer developed with Streamlit and Python. It allows you to visualize and manipulate collections from ChromaDB. You can select collections, add, update, and delete items. <br>
<br>

**Chroma Viewer** <br>
https://github.com/avantrio/chroma-viewer <br>
A quick viewer for local Chrome DB <br>
<br>

**Chroma View Master** <br>
https://github.com/clearsitedesigns/chromaViewMaster <br>
ChromaView Master is a Streamlit-based tool designed to help you understand, visualize, and manipulate Chroma database collections. <br>
<br>

**ChromaDB Web UI** <br>
https://github.com/treeleaves30760/chromadb-WebUI <br>
This is a NodeJS Client with a Web UI Front End for viewing Chroma Collections. <br>
<br>

**ChromaDB UI** <br>
https://github.com/BlackyDrum/chromadb-ui <br>
This is a NodeJS Client with a Web UI Front End for viewing Chroma Collections. <br>
<br>

**ChromaDB UI** <br>
https://github.com/seancheong/chroma-ui <br>
This is a NodeJS Client with a Web UI Front End for viewing Chroma Collections. <br>
<br>

**ChromaDB UI** <br>
https://github.com/keval9098/chromadb-ui <br>
This is a Python Client with a Web UI Front End for viewing Chroma Collections. <br>
<br>

**ChromaDB RAG** <Br>
https://github.com/leporejoseph/streamlit_Rag <br>
RAG System using ChromaDB to drive it <br>
<br>
<br>
