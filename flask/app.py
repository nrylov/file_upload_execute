from flask import Flask, request, Response, render_template, redirect, send_file, jsonify, url_for, stream_with_context
from werkzeug.utils import secure_filename
import tempfile
from helpers import *
from shelljob import proc
import os

# Config
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# Handles rendering the index page
@app.route('/', methods=['GET'])
def indexpage():
    return render_template('index.html', title='Index')


# Handles uploads from the html form
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        # Grabs the file from the form
        file = request.files['scriptupload']
        # Grabs the filename
        filename = secure_filename(file.filename)
        # Reads the file
        file = file.read()
        # Calls filehandler, which stores the file and returns a url to access the file.
        uploaded = filehandler(filename, file)
        return redirect('/listfiles')


# Handles uploads from CURL
@app.route('/<filename>', methods=['PUT', 'GET'])
def filepage(filename):
    # Handles if PUT request (curl -T [filename] [url])
    if request.method == 'PUT':
        # Saves sent file to variable
        file = request.data
        # If a file was sent, calls filehandler and returns the result.
        if file is not None:
            return filehandler(filename, file)
        # If no file was sent, returns "Empty file."
        else:
            return '\nEmpty file.\n'


# Handles file download
@app.route('/retrieve/<id>')
def retrievefile(id):
    # Calls grabfile which retrieves the file and saves it to a variable.
    file = grabfile(id)
    # Creates a temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w+b')
    # Writes the file to the temporary file
    temp_file.write(file['file'])
    # Returns to the start byte of the file prior to returning it
    temp_file.seek(0)
    # Returns the file
    return send_file(temp_file, attachment_filename=file['filename'])


# Handles passing arguments to running a script if using
@app.route('/execute/<id>', methods=['POST', 'GET'])
def getargs(id):
    # if GET request, renders launch page.
    if request.method == 'GET':
        file = grabfile(id)
        return render_template('passargs.html', file=file, title="Launch script")
    # If POST request, redirects to execute page.
    else:
        args = request.form.to_dict()['args']
        url = f"/execute/{id}/{args}"
        # return url
        return redirect(url)


# Handles executing script
@app.route('/execute/<id>/<args>')
def execute(id, args):
    # Grabs file
    file = grabfile(id)
    try:
        # Creates a temp file
        temp_file = tempfile.NamedTemporaryFile(mode='a+b', suffix='.sh', delete=False)
        # Writes the file to the temporary file
        temp_file.write(file['file'])
        # Closes the temp file so it can be executed
        temp_file.close()
        # Chmods the file so it can be executed
        make_executable(temp_file.name)

        # Initiates shelljob package, for formatted subprocess handling
        g = proc.Group()
        # Converts passed args into a list
        args = args.split(',')

        # Defines the command to be executed (temp file path + list of args)
        command = [f'{temp_file.name}'] + args
        # Runs the command
        p = g.run(command)

        # Handles tracking the process
        def read_process():
            while g.is_pending():
                # Reads lines of the process's output
                lines = g.readlines()
                for proc, line in lines:
                    # Converts each line from bytes to a string and yields it
                    line = line.decode()
                    if line != '':
                        yield line

        # Handles streaming process output if the request came from curl
        if 'curl' in request.headers.get('User-Agent'):
            return Response(read_process(), mimetype='text/plain')
        # Handles streaming the process output if the request came from a web browser
        else:
            return Response(stream_with_context(stream_template('execute.html', rows=read_process())))
    finally:
        # Deletes the temp file when completed.
        os.remove(temp_file.name)


# Handles file list
@app.route('/listfiles')
def listfiles():
    # Connects to db
    db = sqlite3.connect('files.db')
    # Sets sqlite row factory as Row, which formats results as dicts
    db.row_factory = sqlite3.Row
    # Initiates db cursor
    cursor = db.cursor()
    # Defines query for selecting all files from db
    fetch_files_query = "SELECT id, filename, datetime(date, 'unixepoch') FROM files"
    # Executes query and saves results to a variable
    results = cursor.execute(fetch_files_query).fetchall()
    # Saves the server url to a variable
    url = url_for('indexpage', _external=True)
    # Defines a list of dictionaries that contain useful info such as the query results
    # and execute/download/delete links.
    results_dict = [dict(result, execute_url=f'{url}execute/{result["id"]}',
                    retrieve_url=f'{url}retrieve/{result["id"]}', delete_url=f'{url}delete/{result["id"]}')
                    for result in results]
    # If the list page was loaded using curl, returns results in json format
    if 'curl' in request.headers.get('User-Agent'):
        return jsonify(results_dict)
    # If the list page was loaded using a web browser, renders the listing page
    else:
        # Renders the list page, passing query results
        return render_template('list.html', results=results_dict, title='Script list')


# Handles deleting files
@app.route('/delete/<id>')
def delete(id):
    # Connects to db
    db = sqlite3.connect('files.db')
    # Establishes a db cursor
    cursor = db.cursor()
    # Defines query for deleting the file
    delete_query = "DELETE FROM files WHERE id = ?"
    # Executes the query
    cursor.execute(delete_query, (id,))
    # Commits changes to db
    db.commit()
    # Closes db connection
    db.close()
    # If the delete page was loaded using curl, returns response in json format
    if 'curl' in request.headers.get('User-Agent'):
        return jsonify({'response': 'File deleted successfully.'})
    # If the delete page was loaded using a web browser, redirects back to the list page.
    else:
        return redirect('/listfiles')


# Handles streaming to flask
def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
