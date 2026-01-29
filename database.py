from sqlalchemy import Column, Integer, Float, DateTime, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os, sys

# SQLite database file path



def get_db_path():
    # Define a name for your app's data folder
    app_name = "DustMonitorUM"
    
    if getattr(sys, 'frozen', False):
        # On Windows, this points to C:\Users\Username\AppData\Local
        base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    else:
        # During development, keep it in the script directory
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a dedicated subfolder if it doesn't exist
    data_dir = os.path.join(base_dir, app_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    db_path = os.path.join(data_dir, "dustmonitor.db")
    print("db_path:", db_path)
    return db_path

# DATABASE_URL = os.environ.get("DATABASE_URL")

# if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
#     # SQLAlchemy requires 'postgresql://' not 'postgres://' (Supabase sometimes provides the latter)
#     DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# else:
#     # DATABASE_URL = "sqlite:///./local_dev.db"
#     db_path = get_db_path()

#     normalized_path = db_path.replace(os.sep, '/')
#     DATABASE_URL = f"sqlite:///{normalized_path}"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

################

# 1. Pull the raw URL from the environment
raw_url = os.environ.get("DATABASE_URL")

# 2. Logic to determine final URL
if raw_url:
    # Handle the Supabase/Heroku 'postgres://' quirk
    if raw_url.startswith("postgres://"):
        DATABASE_URL = raw_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = raw_url
else:
    # Local fallback
    db_path = get_db_path() # Your existing function
    normalized_path = db_path.replace(os.sep, '/')
    DATABASE_URL = f"sqlite:///{normalized_path}"

# 3. Create the engine
# Note: check_same_thread is ONLY for SQLite
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

# For your debug print:
print(f"CONNECTED TO HOST: {engine.url.host}") 
print(f"FULL URL USED: {DATABASE_URL}")
################

current_db_host = engine.url.host
print(current_db_host)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. Table for periodic readings
class DeviceReading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    # timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    timestamp = Column(DateTime(timezone=True), server_default=datetime.now(timezone.utc).isoformat())
    network_address = Column(Integer)
    dust_concentration = Column(Float)
    pcb_temp = Column(Float)
    current_loop = Column(Float)
    laser_diode_signal = Column(Integer)
    photo_diode_signal = Column(Integer)

def get_db():
    db = SessionLocal()
    print("current_db_host", current_db_host)
    print("DATABASE_URL: ", DATABASE_URL)
    print("DEBUG: All Env Keys:", os.environ.keys())
    try:
        yield db
    finally:
        db.close()


# 2. Table for device configuration & calibration, Not required for now.
# class DeviceConfig(Base):
#     __tablename__ = "device_configs"
#     network_address = Column(Integer, primary_key=True)
#     max_range = Column(Integer)
#     alarm_threshold = Column(Integer)
#     calibration_a = Column(Float)
#     calibration_b = Column(Float)
#     last_updated = Column(DateTime, default=datetime.utcnow)

# Create the tables
Base.metadata.create_all(bind=engine)