from flask import Flask, request, redirect, url_for, render_template
from flask_mail import Mail, Message
import os
import logging
import zipfile
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# TODO: Flesh out secure copy
# TODO: Stats
# TODO: Better error handling

app = Flask(__name__)


# Config block
# Testing locally via mailcatcher
# I would pull all variables out to an external parm store, whether it was an env file, parm store, secrets manager, property file,etc
# Intentionally lazy here and hardcoding 
app.config['MAIL_SERVER'] = '127.0.0.1'  # Replace with your mail server
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = None  # Replace with your email
app.config['MAIL_PASSWORD'] = None     # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'glennkiser@awesomeware.com'

#This is just a test flag to disable mail sending if a smpt server isnt available..
mail_active = 'y'

# End config

mail = Mail(app)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)  # Wait a moment to ensure the file is fully written
            self.compress_file(event.src_path)
            #self.secure_copy_file(file)

    def compress_file(self, file_path):
        file_name = os.path.basename(file_path)
        zip_file_path = os.path.splitext(file_path)[0] + ".zip"
        
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(file_path, arcname=file_name)
        
        logging.info(f"File compressed: {file_name} to {zip_file_path}")
     
        # Optionally, delete the original file after compression
        os.remove(file_path)
        logging.info(f"Original file deleted: {file_name}")

    #def secure_copy_file(self, file)
        #secure copy step.

# watcher
observer = Observer()
event_handler = FileHandler()
observer.schedule(event_handler, path=UPLOAD_FOLDER, recursive=False)
observer.start()

def is_valid_email(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return email_regex.match(email)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        email = request.form['email'].strip()
 
        if file and email and is_valid_email(email): 
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Log the file upload
            logging.info(f"File uploaded: {file.filename} (saved to {file_path})")
            logging.info(f"Uploaded by: {email}")
            
            # Send email notification
            if mail_active == 'y': 
              msg = Message("New File Uploaded", 
                          sender=[email],
                          recipients=["glennkiser@awesomeware.com"])
              msg.body = f"A new file named {file.filename} has been uploaded."
              mail.send(msg)
              logging.info(f"Email sent to {recipients} from {sender}")

            return 'File uploaded and notification email sent
        else:
            return 'Invalid email address or no file uploaded.', 400

    return '''

    <!doctype html>
    <title>Upload File</title>
    <h1>Upload a file</h1>
    <form method=post enctype=multipart/form-data>
      <label for="email">Email address:</label>
      <input type="email" name="email" id="email" required><br><br>
      <input type=file name=file required>
      <input type=submit value=Upload>
    </form>    
    '''

#Main
if __name__ == "__main__":
    try:
        app.run(ssl_context=('/usr/src/app/certs/server.crt', '/usr/src/app/certs/server.key'),host="0.0.0.0", port=5000)
    except:
        print('An error occurred launching the app')

    observer.join()

