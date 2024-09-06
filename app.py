
"""import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from encryption import encrypt_document, decrypt_document, generate_key
from qr_generator import generate_qr_code, add_logo_to_qr

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file to the specified path
            file.save(filepath)

            # Encrypt the document
            key = generate_key()
            with open(filepath, 'rb') as f:
                file_data = f.read()
            encrypted_data = encrypt_document(file_data, key)
            encrypted_file_path = filepath + '.enc'
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)

            # Generate a secure download link
            download_link = url_for('download_file', filename=os.path.basename(encrypted_file_path), key=key.hex(), _external=True)
            qr_data = download_link

            # Generate QR code
            qr_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'qrcode.png')
            generate_qr_code(qr_data, qr_image_path)

            # Optionally, add a logo to the QR code
            logo_path = ''  # Add your logo here
            if os.path.exists(logo_path):
                qr_image_with_logo = os.path.join(app.config['UPLOAD_FOLDER'], 'qrcode_with_logo.png')
                add_logo_to_qr(qr_image_path, logo_path, qr_image_with_logo)
                qr_image_path = qr_image_with_logo

            return render_template('upload.html', qr_code=qr_image_path, download_link=download_link)

    return render_template('upload.html')

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    key = request.args.get('key')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Decrypt the document before sending it to the user
    with open(filepath, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = decrypt_document(encrypted_data, bytes.fromhex(key))

    # Save decrypted file temporarily to send it to the user
    original_filename = filename.replace('.enc', '')
    decrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
    
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)

    return send_file(decrypted_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)"""


"""import os
from flask import Flask, render_template, request, redirect, url_for
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import qrcode

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Google Drive API setup
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

def upload_to_drive(filepath):
    file_metadata = {'name': os.path.basename(filepath)}
    media = MediaFileUpload(filepath, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    return file_id

def get_shareable_link(file_id):
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(fileId=file_id, body=permission).execute()
    file = service.files().get(fileId=file_id, fields='webViewLink').execute()
    return file.get('webViewLink')

def generate_qr_code(data, filepath):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(filepath)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Upload to Google Drive
        file_id = upload_to_drive(filepath)
        shareable_link = get_shareable_link(file_id)

        # Generate QR Code
        qr_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'qrcode.png')
        generate_qr_code(shareable_link, qr_image_path)

        return render_template('upload.html', qr_code=qr_image_path, download_link=shareable_link)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)"""


import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from qr_generator import generate_qr_code

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

def upload_to_drive(file_path):
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')
    
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # Making the file shareable
    file_id = file.get('id')
    permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    service.permissions().create(fileId=file_id, body=permission).execute()
    
    # Generate the shareable link
    file_link = f"https://drive.google.com/uc?id={file_id}&export=download"
    return file_link

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file locally first
            file.save(filepath)

            # Upload the file to Google Drive
            try:
                download_link = upload_to_drive(filepath)

                # Generate QR code for the download link
                qr_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'qrcode.png')
                generate_qr_code(download_link, qr_image_path)

                return render_template('upload.html', qr_code=qr_image_path, download_link=download_link)
            except Exception as e:
                return f"An error occurred: {e}"

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)



