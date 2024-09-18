
# file_upload_execute

This repository contains a microservice made using Flask that allows uploading scripts and executing them either via a web browser or curl. This is by no means a completed project, but rather an exercise done to practice executing scripts and streaming stdout via Flask.

# Technologies used

* Flask - I chose Flask as the backend because I am decently familiar with it. Flask handled calling all APIs, giving access to the project's pages, and formatting data.
* Sqlite3 was used for storage, as it is a lightweight sql implementation that stores all data in a .db file.
* HTML/CSS w/ Jinja2 - HTML was used to design the project's pages, and Jinja2 was used to implement data passed by Flask into each page. CSS was used to style the pages.
  * Bootstrap - was used for overall page layout.
  * jquery/javascript - was used to handle tasks such as the data table.  
  *   Jinja2 templates can be found in the flask/templates folder.
* Docker-compose was used on linux to deploy the app.
* A nginx container spawns along with a flask container to run the app and provide access to it using a reverse proxy.
* Shelljob was used instead of subprocess for convenience because it pre-formats the output of executed commands. 
# Usage instructions
* Install docker and docker-compose on a linux server.
* Clone the repository.
* Enter the repository folder.
* Execute ```docker-compose up```.
	* Note that port 80 is used by default.
* Access the app by going to ```http://[server ip]```. 
* If you would like to use the app using curl, execute ```curl -T [filename to be uploaded].sh [url]```. You may then execute ```curl [url]/listfiles``` to view a list of files  and their execute/download/delete links in json format.
	* Note that in some areas, 127.0.0.1 may be returned as part of URLs, as I have not implemented grabbing the IP of the server the service runs on yet.
* If you would like to use the app using a browser, visit ```http://[server ip]``` to upload files and ```http://[server ip]/listfiles``` to list files.
* Execute files by either visiting or sending a curl request to ```http://[server ip]/execute/[fileid]/(args separated by a comma)```. An example of passing args is ```/execute/1/arg1,arg2,arg3```. Alternatively, visit ```http://[server ip]/execute/[fileid]``` to be prompted to enter args.
	* testfile.sh is a simple script that executes the ping command and expects 1 argument, the address to ping.
