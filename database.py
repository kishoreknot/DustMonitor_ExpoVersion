from sqlalchemy import Column, Integer, Float, DateTime, Boolean,  create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os, sys , re
from urllib.parse import quote_plus

# SQLite database file path



def get_db_path():
    # Define a name for your app's data folder
    app_name = "DustMonitorUM"
    
    if getattr(sys, 'frozen', False):
        # On Windows, this points to C:\Users\Username\AppData\Local
        base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        print("database.frozen.false", base_dir)
    else:
        # During development, keep it in the script directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print("database.frozen.true", base_dir)

    # Create a dedicated subfolder if it doesn't exist
    data_dir = os.path.join(base_dir, app_name)
    print("database.datadir", data_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("database.path.notexist", data_dir)
    db_path = os.path.join(data_dir, "dustmonitor.db")
    print("database.db_path", db_path)
    return db_path

def get_encoded_url():
    # url = os.getenv("DATABASE_URL")
    url = "postgresql://postgres.rujlxnjigobdlodykgmr:Kis#dwansys31@aws-1-ap-south-1.pooler.supabase.com:5432/postgres" #KIDEL
    if not url:
        db_path = get_db_path()
        normalized_path = db_path.replace(os.sep, '/')
        SQLITE_URL = f"sqlite:///{normalized_path}"
        return SQLITE_URL

    # 1. Fix the postgres prefix for SQLAlchemy 1.4+
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # 2. Use Regex to find the password and encode it
    # This regex looks for: protocol://user:PASSWORD@host
    pattern = r"^(postgresql://.*?):(.*?)@(.*?)$"
    match = re.match(pattern, url)
    
    if match:
        prefix, password, suffix = match.groups()
        # Only encode if it's not already encoded (doesn't contain %)
        if "%" not in password:
            encoded_password = quote_plus(password)
            url = f"{prefix}:{encoded_password}@{suffix}"
            
    return url

DATABASE_URL = get_encoded_url() #os.environ.get("DATABASE_URL")
# DATABASE_URL = 'Something'

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
#     # SQLAlchemy requires 'postgresql://' not 'postgres://' (Supabase sometimes provides the latter)
#     DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# else:
#     # DATABASE_URL = "sqlite:///./local_dev.db"
#     db_path = get_db_path()
#     normalized_path = db_path.replace(os.sep, '/')
#     DATABASE_URL = f"sqlite:///{normalized_path}"

engine = create_engine(DATABASE_URL, connect_args=connect_args)



# current_db_host = engine.url.host
# print(current_db_host)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 1. Table for periodic readings
class DeviceReading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    # timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    # timestamp = Column(DateTime(timezone=True), server_default=datetime.now(timezone.utc).isoformat())
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    network_address = Column(Integer)
    dust_concentration = Column(Float)
    pcb_temp = Column(Float)
    current_loop = Column(Float)
    laser_diode_signal = Column(Integer)
    photo_diode_signal = Column(Integer)
    alarm_threshold = Column(Integer)
    alarm_raised = Column(Boolean, default=False)

def get_db():
    db = SessionLocal()
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