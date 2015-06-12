from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from app import app, db

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
    return pwd_context.verify(password, self.password_hash)

  def generate_auth_token(self, expiration=600):
    """Creates an authorization token
    """
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({'id': self.id})

  @staticmethod
  def verify_auth_token(token):
    """Verify the token and return the user object if verifies
    """
    s = Serializer(app.config['SECRET_KEY'])
    try:
      data = s.loads(token)
    except SignatureExpired:
      return None # valid token but expired
    except BadSignature:
      return None # invalid token
    user = User.query.get(data['id'])
    return user
