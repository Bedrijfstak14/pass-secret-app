from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, LargeBinary, String

db = SQLAlchemy()

class Secret(db.Model):
    id = Column(String(32), primary_key=True)
    data = Column(LargeBinary, nullable=False)
    nonce = Column(LargeBinary(12), nullable=False)
    views_left = Column(Integer, default=1)
