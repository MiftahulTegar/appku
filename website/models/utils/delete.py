from website.models.user import Doctor
from ... import db
from flask_login import current_user
import os, shutil

class DeleteData:
    def __init__(self, DB, item_id):
        self.DB = DB
        self.item_id = item_id
        self.is_deleted = False
    