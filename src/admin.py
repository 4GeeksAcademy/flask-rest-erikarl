import os
from flask_admin import Admin
from models import db, User, Planets, People, Favorite
from flask_admin.contrib.sqla import ModelView

class FavoriteAdmin(ModelView):
    column_list = ("user_id", "content_type", "content_id")
    column_labels = {
        "user_id": "Usuario",
        "content_type": "Tipo de contenido",
        "content_id": "ID del contenido"
    }

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Planets, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(FavoriteAdmin(Favorite, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))