from flask import Flask, request, redirect, url_for, render_template
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Configurations for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your-email-password'     # Replace with your email password

mail = Mail(app)

# Folder to store uploaded files
UPLOAD_FOLDER = '/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            
            # Send email notification
            msg = Message("New File Uploaded", 
                          sender="your-email@example.com",
                          recipients=["recipient-email@example.com"])
            msg.body = f"A new file named {file.filename} has been uploaded."
            #mail.send(msg)
            print msg.body

            return 'File uploaded and email sent!'
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
    app.run(host="0.0.0.0", port=8080)
