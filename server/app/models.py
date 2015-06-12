from passlib.apps import custom_app_context as pwd_context
from app import db

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(32), index=True)
  password_hash = db.Column(db.String(128))
  created_at = db.Column(db.DateTime, server_default=db.func.now())
  created_at = db.Column(db.DateTime, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

  def hash_password(self, password):
    """Hashes user-given password before storing in database
    """
    # Use the sha256_crypt hashing algorithm from PassLib
    self.password_hash = pwd_context.encrypt(password)

  def verify_password(self, password):
    """Verifies a user-given password against hashed password from database
    """
    return pwd_context.verify(password, self.hash_password)
