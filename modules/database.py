from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create database directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Database configuration
DATABASE_URL = "sqlite:///data/outfits.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Outfit(Base):
    """SQLAlchemy model for storing outfit information"""
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    image_path = Column(String(255))
    weather = Column(String(255))
    emotion = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert outfit object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_path": self.image_path,
            "weather": self.weather,
            "emotion": self.emotion,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

def init_db():
    """Initialize the database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_outfit(db, name, description=None, image_path=None, weather=None, emotion=None):
    """Save a new outfit to the database"""
    try:
        outfit = Outfit(
            name=name,
            description=description,
            image_path=image_path,
            weather=weather,
            emotion=emotion
        )
        db.add(outfit)
        db.commit()
        db.refresh(outfit)
        logger.info(f"Saved outfit: {name}")
        return outfit
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving outfit: {str(e)}")
        raise

def get_outfits(db, limit=10, offset=0):
    """Get recent outfits from the database"""
    try:
        outfits = db.query(Outfit).order_by(Outfit.created_at.desc()).offset(offset).limit(limit).all()
        return [outfit.to_dict() for outfit in outfits]
    except Exception as e:
        logger.error(f"Error getting outfits: {str(e)}")
        raise

def get_outfit_by_id(db, outfit_id):
    """Get a specific outfit by ID"""
    try:
        outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
        return outfit.to_dict() if outfit else None
    except Exception as e:
        logger.error(f"Error getting outfit by ID: {str(e)}")
        raise

def delete_outfit(db, outfit_id):
    """Delete an outfit from the database"""
    try:
        outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
        if outfit:
            db.delete(outfit)
            db.commit()
            logger.info(f"Deleted outfit: {outfit.name}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting outfit: {str(e)}")
        raise

# Initialize database when module is imported
init_db() 