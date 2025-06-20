import os

# बेसिक कॉन्फिगरेशन
SECRET_KEY = 'your-secret-key-here'
SQLALCHEMY_DATABASE_URI = 'sqlite:///inventory.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# फाइल अपलोड सेटिंग्स
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# पेजिनेशन
ITEMS_PER_PAGE = 20