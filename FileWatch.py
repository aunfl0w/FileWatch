from flask import Flask, request, redirect, url_for, render_template
from flask_mail import Mail, Message
import os
import logging
import zipfile
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# TODO: Secure copy
# TODO: Stats

app = Flask(__name__)

mail_active = 'y'
# Configurations for Flask-Mail
# Testing locally via mailcatcher
app.config['MAIL_SERVER'] = '127.0.0.1'  # Replace with your mail server
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = None  # Replace with your email
app.config['MAIL_PASSWORD'] = None     # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@example.com'

mail = Mail(app)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileCompressorHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)  # Wait a moment to ensure the file is fully written
            self.compress_file(event.src_path)

    def compress_file(self, file_path):
        file_name = os.path.basename(file_path)
        zip_file_path = os.path.splitext(file_path)[0] + ".zip"
        
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(file_path, arcname=file_name)
        
        logging.info(f"File compressed: {file_name} to {zip_file_path}")

        # Optionally, delete the original file after compression
        os.remove(file_path)
        logging.info(f"Original file deleted: {file_name}")

# watcher
observer = Observer()
event_handler = FileCompressorHandler()
observer.schedule(event_handler, path=UPLOAD_FOLDER, recursive=False)
observer.start()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Log the file upload
            logging.info(f"File uploaded: {file.filename} (saved to {file_path})")
            
            # Send email notification
            if mail_active == 'y': 
              msg = Message("New File Uploaded", 
                          sender="your-email@example.com",
                          recipients=["recipient-email@example.com"])
            msg.body = f"A new file named {file.filename} has been uploaded."
            mail.send(msg)
            print (msg.body)

            return 'File uploaded and notification email sent'
    return '''
    <!doctype html>
    <title>Upload File</title>
    <h1>Upload a file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    try:
        app.run(ssl_context=('/usr/src/app/certs/server.crt', '/usr/src/app/certs/server.key'),host="0.0.0.0", port=5000)
    observer.join()
