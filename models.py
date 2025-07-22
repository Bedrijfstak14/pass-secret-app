from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, LargeBinary, String
from datetime import datetime

db = SQLAlchemy()

class Secret(db.Model):
    id = Column(String(32), primary_key=True)
    data = Column(LargeBinary, nullable=False)
    nonce = Column(LargeBinary(12), nullable=False)
    views_left = Column(Integer, default=1)
    expire_at = db.Column(db.DateTime, nullable=True)
    def is_expired(self):
        return self.expire_at and datetime.now(timezone.utc) > self.expire_at
