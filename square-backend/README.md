# :rocket: Overview
Square backend is a Flask webserver with basics funciton:
- manages user accounts 
- everyone can send question, however users have to registered to create and manage their skills
- only authorized skill owner can manage, each skill is a assigned with an user
- use flask-jwt to manage session
- handles the selection of skills for questions
- user registration and password reset via email

# :large_orange_diamond: Technicals:
- WebSocket is run with [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/) using [eventlet](http://eventlet.net/).  
- There are two options to communicate with square-fronten:
   - REST endpoints: result is returned once all skills have answered. Most actions from front-end are sent in this manner.
   - Websockets: then results are returned one by one as the skills answer. This is a less preferable and might be removed by the near future

# :large_orange_diamond: Project structure
* flask-manage.py: Managing the database with Flask Migration
* main.py: The entry point for the dev server
* config.yaml: The config file with the configuration for Flask, the Flask modules and the server code
* templates: html templates for emails
* squareapi: the Flask server  
    * emailService: module to send emails to the users   
    * skill: Skill selection and request handling  
      *     
    * app.py: The Flask App
    * api.py: contains all REST API endpoints
    * websocket.py: The WebSocket API
    * models.py: The models used in the database
 

# :heavy_check_mark: Basics commands
If you want to start a stand-alone square-backend server without docker, you can do as follows:
1. Install python and requirements.txt
2. Creating a database
If you create a fresh database with all required tables.
`python flask_manage.py db init` 
`python flask_manage.py db migrate`
`python flask-mange.py db upgrade` 
3.Starting the server
Run `python main.py`.

# API Documentation
The API is documented [here](squareapi/api.py) in the docstrings as YAML-formatted Swagger documentation.
The endpoint `/apidocs` of a running server renders the entire documentation as a webpage.

# :hammer: BACKEND DEBUG 
If you are running the square-backend as a container and still want to debug it line by line, which is very useful to print the variable values and determine what is going wrong with the code, please follow this: 
1. Set DEBUG=True in config.yaml to run flask server in debug mode
2. You must add following lines to be able to print to console  
`print("whatever you want print")`  
`import sys`  
`sys.stdout.flush() `  

# Postgres
- Stand-alone mode: `python flask-manage.py shell` starts a Python shell in the app context so you can easily manage the DB manually with it.
- Inside a docker container: Run `docker exec -it square-core_db_1 psql -U square` to get inside the postgre container
and then use psql command to inspect the db. You can read [psql documentation](http://postgresguide.com/utilities/psql.html) to write your own queries
![Data model](https://github.com/UKPLab/square-core/blob/master/doc/models.png)

# :open_file_folder: Detailed descriptions
### square-backend/templates
* contains different email HTML templates for the app

### square-backend/emailService
* implements utils functions that render the email template and send these emails to users

#### square-backend/skill
* implement the the different selector types/classes that uses voting strategy to choose the best answer out of the answer candidates
* handles the training of individuals skills a.k.a saving the sample training samples into elasticsearch and the postgresdb
* implement skill-selector classes to upvote the type of selector that best fit (based on the similarity between the questions) 

### square-backend/squareapi/skill/app.py
* initiate all of the additional components for the flask app: create websocker connection, loading app config, swagger hub, …

### square-backend/squareapi/api.py
*a central store for all of the implementations of the backend API, all api function should be implemented here.
* using blueprint to match incoming request with the function that should handle it 
* please read the docstring of each function for detailed information on how this function works

### square-backend/squareapi/models.py
* manage and define the properties of the classes being used in the apps
* new classes should be created here

### square-backend/squareapi/websocket.py
* a central store for all of the functions that handles the websocket connections with the frontend.



