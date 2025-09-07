from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Date, Time, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

Base = declarative_base()

# Definição dos modelos
class Photoperiod(Base):
    __tablename__ = 'photoperiod'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(500))

class Gender(Base):
    __tablename__ = 'gender'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(500))

class Intensity(Base):
    __tablename__ = 'intensity'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(500))

class TrainingType(Base):
    __tablename__ = 'training_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(500))

class DamageType(Base):
    __tablename__ = 'damage_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(500))

class SensorType(Base):
    __tablename__ = 'sensor_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(500))

class EffectorType(Base):
    __tablename__ = 'effector_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(500))

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(300), unique=True)
    password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    
    grows = relationship("Grow", back_populates="user", cascade="all, delete-orphan")

class Grow(Base):
    __tablename__ = 'grow'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(50), nullable=False)
    lenght = Column(Float)
    width = Column(Float)
    height = Column(Float)
    
    user = relationship("User", back_populates="grows")
    plants = relationship("Plant", back_populates="grow", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="grow", cascade="all, delete-orphan")
    effectors = relationship("Effector", back_populates="grow", cascade="all, delete-orphan")

class Sensor(Base):
    __tablename__ = 'sensor'
    
    id = Column(Integer, primary_key=True)
    grow_id = Column(Integer, ForeignKey('grow.id'))
    ip = Column(String(45), nullable=True)
    name = Column(String(100), nullable=False)
    sensor_type_id = Column(Integer, ForeignKey('sensor_type.id'))
    last_sensor_value = Column(Float, default=0.0)
    data_retention_days = Column(Integer, default=1)
    
    # Relationships
    grow = relationship("Grow", back_populates="sensors")
    sensor_type = relationship("SensorType")
    sensor_data = relationship("SensorData", back_populates="sensor", cascade="all, delete-orphan")
    bounded_effectors = relationship("Effector", back_populates="bounded_sensor", foreign_keys="Effector.bounded_sensor_id")  # Relação reversa
    
    def __repr__(self):
        return f"<Sensor(id={self.id}, name='{self.name}')>"

class Effector(Base):
    __tablename__ = 'effector'
    
    id = Column(Integer, primary_key=True)
    grow_id = Column(Integer, ForeignKey('grow.id'))
    effector_type_id = Column(Integer, ForeignKey('effector_type.id'))
    name = Column(String(100), nullable=False)
    ip = Column(String(45), nullable=True)
    normal_on = Column(Boolean, default=True)
    power_on = Column(Boolean, default=False)
    scheduled = Column(Boolean, default=False)
    on_time = Column(Time, nullable=True)
    off_time = Column(Time, nullable=True)
    bounded = Column(Boolean, default=False)
    bounded_sensor_id = Column(Integer, ForeignKey('sensor.id'), nullable=True)
    threshold = Column(Float, default=0.0)
    last_request = Column(DateTime, default=datetime.now)
    
    # Relationships
    grow = relationship("Grow", back_populates="effectors")
    effector_type = relationship("EffectorType")
    bounded_sensor = relationship("Sensor", foreign_keys=[bounded_sensor_id], back_populates="bounded_effectors")
    
    def __repr__(self):
        return f"<Effector(id={self.id}, name='{self.name}')>"

class SensorData(Base):
    __tablename__ = 'sensor_data'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'), nullable=False)
    value = Column(Float, nullable=False)
    datetime = Column(DateTime, default=datetime.now)
    
    sensor = relationship("Sensor", back_populates="sensor_data")

class Plant(Base):
    __tablename__ = 'plant'
    id = Column(Integer, primary_key=True)
    grow_id = Column(Integer, ForeignKey('grow.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    photoperiod_id = Column(Integer, ForeignKey('photoperiod.id'), nullable=False)
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    harvested = Column(Boolean, default=False)
    yield_ = Column('yield', Float, default=0)
    
    grow = relationship("Grow", back_populates="plants")
    photoperiod = relationship("Photoperiod")
    gender = relationship("Gender")
    trainings = relationship("Training", back_populates="plant", cascade="all, delete-orphan")
    waterings = relationship("Watering", back_populates="plant", cascade="all, delete-orphan")
    feedings = relationship("Feeding", back_populates="plant", cascade="all, delete-orphan")
    transplantings = relationship("Transplanting", back_populates="plant", cascade="all, delete-orphan")
    damages = relationship("Damage", back_populates="plant", cascade="all, delete-orphan")

class Training(Base):
    __tablename__ = 'training'
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id'), nullable=False)
    date = Column(Date, nullable=False)
    training_type_id = Column(Integer, ForeignKey('training_type.id'), nullable=False)
    
    plant = relationship("Plant", back_populates="trainings")
    training_type = relationship("TrainingType")

class Watering(Base):
    __tablename__ = 'watering'
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id'), nullable=False)
    date = Column(Date, nullable=False)
    mililiter = Column(Integer, nullable=False)
    
    plant = relationship("Plant", back_populates="waterings")

class Feeding(Base):
    __tablename__ = 'feeding'
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id'), nullable=False)
    date = Column(Date, nullable=False)
    dosage = Column(Integer, nullable=False)
    nitrogen = Column(Integer, nullable=False)
    phosphorus = Column(Integer, nullable=False)
    potassium = Column(Integer, nullable=False)
    concentration = Column(Integer, nullable=False)
    
    plant = relationship("Plant", back_populates="feedings")

class Transplanting(Base):
    __tablename__ = 'transplanting'
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id'), nullable=False)
    date = Column(Date, nullable=False)
    lenght = Column(Float, default=0)
    width = Column(Float, default=0)
    height = Column(Float, default=0)
    radius = Column(Float, default=0)
    
    plant = relationship("Plant", back_populates="transplantings")

class Damage(Base):
    __tablename__ = 'damage'
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id'), nullable=False)
    date = Column(Date, nullable=False)
    damage_type_id = Column(Integer, ForeignKey('damage_type.id'), nullable=False)
    intensity_id = Column(Integer, ForeignKey('intensity.id'), nullable=False)
    
    plant = relationship("Plant", back_populates="damages")
    damage_type = relationship("DamageType")
    intensity = relationship("Intensity")