from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Date, Time, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from models import *

class Database():
    def __init__(self, host, db_name, db_user, db_password):
        self.host = host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        
        # Criar engine e sessão
        connection_string = f"mysql+mysqlconnector://{db_user}:{db_password}@{host}/{db_name}"
        self.engine = create_engine(connection_string, pool_recycle=3600)
        self.Session = scoped_session(sessionmaker(bind=self.engine, autocommit=False, autoflush=False))
        
        # Criar tabelas
        Base.metadata.create_all(self.engine)
        
        # Inserir dados iniciais
        self._insert_initial_data()

    def _get_session(self):
        return self.Session()

    def _insert_initial_data(self):
        session = self._get_session()
        try:
            # Mapeamento correto entre nome da tabela e classe do modelo
            model_mapping = {
                'gender': Gender,
                'photoperiod': Photoperiod,
                'training_type': TrainingType,
                'damage_type': DamageType,
                'intensity': Intensity,
                'sensor_type': SensorType,
                'effector_type': EffectorType
            }
            
            # Dados iniciais para as tabelas de referência
            initial_data = {
                'gender': [
                    {'name': 'Male', 'description': ''},
                    {'name': 'Female', 'description': ''},
                    {'name': 'Hermaphrodite', 'description': ''},
                    {'name': 'Unknown', 'description': ''}
                ],
                'photoperiod': [
                    {'name': 'Germination', 'description': ''},
                    {'name': 'Seedling', 'description': ''},
                    {'name': 'Vegetative', 'description': ''},
                    {'name': 'Flowering', 'description': ''},
                    {'name': 'Autoflower', 'description': ''}
                ],
                'training_type': [
                    {'name': 'Low Stress Training', 'description': ''},
                    {'name': 'High Stress Training', 'description': ''},
                    {'name': 'Apical Pruning', 'description': ''},
                    {'name': 'Lollipop Pruning', 'description': ''},
                    {'name': 'FIM Pruning', 'description': ''}
                ],
                'damage_type': [
                    {'name': 'Physical Damage', 'description': ''},
                    {'name': 'Light Burning', 'description': ''},
                    {'name': 'Wind Burning', 'description': ''},
                    {'name': 'Overwatering', 'description': ''},
                    {'name': 'Overfeeding', 'description': ''},
                    {'name': 'Low watering', 'description': ''},
                    {'name': 'Low Light', 'description': ''},
                    {'name': 'Mold', 'description': ''},
                    {'name': 'Parasites', 'description': ''}
                ],
                'intensity': [
                    {'name': 'Very Low', 'description': ''},
                    {'name': 'Low', 'description': ''},
                    {'name': 'Medium', 'description': ''},
                    {'name': 'High', 'description': ''},
                    {'name': 'Very High', 'description': ''}
                ],
                'sensor_type': [
                    {'name': 'Air Temperature', 'description': ''},
                    {'name': 'Air Humidity', 'description': ''},
                    {'name': 'Soil Temperature', 'description': ''},
                    {'name': 'Soil Humidity', 'description': ''},
                    {'name': 'Soil HP', 'description': ''},
                    {'name': 'Water HP', 'description': ''},
                    {'name': 'PPFD', 'description': ''}
                ],
                'effector_type': [
                    {'name': 'Fan', 'description': ''},
                    {'name': 'Lights', 'description': ''},
                    {'name': 'Water Supplier', 'description': ''},
                    {'name': 'Exhauster', 'description': ''},
                    {'name': 'Blower', 'description': ''},
                    {'name': 'Humidifier', 'description': ''},
                    {'name': 'Dehumidifier', 'description': ''}
                ]
            }
            
            for table_name, data in initial_data.items():
                model_class = model_mapping[table_name]
                for item in data:
                    # Verificar se já existe
                    exists = session.query(model_class).filter_by(name=item['name']).first()
                    if not exists:
                        session.add(model_class(**item))
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"Erro ao inserir dados iniciais: {e}")
            import traceback
            traceback.print_exc()  # Mostra o traceback completo
        finally:
            session.close()

    def execute_query(self, query, params=None):
        """Método de compatibilidade para manter a interface antiga"""
        session = self._get_session()
        try:
            if params:
                result = session.execute(text(query), params)
            else:
                result = session.execute(text(query))
            
            if result.returns_rows:
                return result.fetchall()
            else:
                return result.rowcount
                
        except Exception as e:
            print(f'Erro na query: {e}')
            session.rollback()
            raise
        finally:
            session.close()
    
    def verify_password(self, email: str, password: str) -> bool:
        """Verifica se a senha está correta usando hash"""
        session = self._get_session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                return True
            return False
        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False
        finally:
            session.close()
    
    def get_user_id(self, email: str):
        """Obtém ID do usuário sem expor senha"""
        session = self._get_session()
        try:
            user = session.query(User).filter_by(email=email).first()
            return user.id if user else None
        finally:
            session.close()
        
    def get_admin(self, user_id):
        session = self._get_session()
        try:
            user = session.query(User).get(user_id)
            return user.is_admin if user else False
        finally:
            session.close()
    
    def create_user(self, email: str, password: str, is_admin: bool = False) -> bool:
        """Cria usuário com senha hasheada"""
        session = self._get_session()
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(email=email, password=hashed_password, is_admin=is_admin)
            session.add(new_user)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erro ao criar usuário: {e}")
            return False
        finally:
            session.close()
    
    def get_user_email(self, user_id: int) -> str:
        session = self._get_session()
        try:
            user = session.query(User).get(user_id)
            return user.email if user else ""
        finally:
            session.close()
        
    def get_users(self):
        session = self._get_session()
        try:
            users = session.query(User).all()
            return [(user.id, user.email, user.is_admin) for user in users]
        finally:
            session.close()
    
    def alter_password(self, user_id, password):
        session = self._get_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                user.password = generate_password_hash(password)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
    
    def alter_email(self, user_id, email):
        session = self._get_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                user.email = email
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
    
    def delete_user(self, id):
        session = self._get_session()
        try:
            user = session.query(User).get(id)
            if user:
                session.delete(user)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
    
    def update_user(self, user_id, email, password, is_admin):
        session = self._get_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                user.email = email
                user.password = generate_password_hash(password)
                user.is_admin = is_admin
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_plants(self):
        session = self._get_session()
        try:
            plants = session.query(Plant).all()
            return [(p.id, p.grow_id, p.name, p.start_date, p.end_date, 
                    p.photoperiod_id, p.gender_id, p.harvested, p.yield_) for p in plants]
        finally:
            session.close()
    
    def insert_plant(self, grow_id, name, date, photoperiod_id, gender_id):
        session = self._get_session()
        try:
            new_plant = Plant(
                grow_id=grow_id, 
                name=name, 
                start_date=date, 
                photoperiod_id=photoperiod_id, 
                gender_id=gender_id
            )
            session.add(new_plant)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
    
    def update_plant(self, id, name, date, photoperiod_id, gender_id, harvested=0):
        session = self._get_session()
        try:
            plant = session.query(Plant).get(id)
            if plant:
                plant.name = name
                plant.start_date = date
                plant.photoperiod_id = photoperiod_id
                plant.gender_id = gender_id
                plant.harvested = bool(harvested)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_plant(self, plant_id):
        session = self._get_session()
        try:
            plant = session.query(Plant).get(plant_id)
            if plant:
                return [(plant.id, plant.grow_id, plant.name, plant.start_date, 
                        plant.end_date, plant.photoperiod_id, plant.gender_id, 
                        plant.harvested, plant.yield_)]
            return []
        finally:
            session.close()
    
    def delete_plant(self, plant_id):
        session = self._get_session()
        try:
            plant = session.query(Plant).get(plant_id)
            if plant:
                session.delete(plant)
                session.commit()
                return 1
            return 0
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
    
    # Os métodos restantes seguem o mesmo padrão...
    # Implementei apenas os principais para demonstração
    
    def get_user_grows(self, user_id):
        session = self._get_session()
        try:
            grows = session.query(Grow).filter_by(user_id=user_id).all()
            return [(g.id, g.user_id, g.name, g.lenght, g.width, g.height) for g in grows]
        finally:
            session.close()
    
    def insert_grow(self, user_id, name, lenght, width, height):
        session = self._get_session()
        try:
            new_grow = Grow(
                user_id=user_id,
                name=name,
                lenght=lenght,
                width=width,
                height=height
            )
            session.add(new_grow)
            session.commit()
            return True
        except SQLAlchemyError:
            session.rollback()
            return False
        finally:
            session.close()
    
    # Métodos para manter compatibilidade (podem ser implementados conforme necessário)
    def get_trainings(self):
        return self.execute_query("SELECT id, plant_id, training_type_id, date FROM training")
    
    def get_plant_trainings(self, plant_id):
        return self.execute_query(
            "SELECT id, plant_id, training_type_id, date FROM training WHERE plant_id = %s",
            (plant_id,)
        )
    
    def insert_training(self, plant_id, training_type_id, date):
        return self.execute_query(
            "INSERT INTO training (plant_id, training_type_id, date) VALUES (%s, %s, DATE(%s))",
            (plant_id, training_type_id, date)
        )
    
    # ... outros métodos podem seguir o mesmo padrão

    # Métodos para tipos de referência
    def get_training_types(self):
        session = self._get_session()
        try:
            types = session.query(TrainingType).all()
            return [(t.id, t.name, t.description) for t in types]
        finally:
            session.close()
    
    def get_photoperiods(self):
        session = self._get_session()
        try:
            photoperiods = session.query(Photoperiod).all()
            return [(p.id, p.name, p.description) for p in photoperiods]
        finally:
            session.close()
    
    def get_genders(self):
        session = self._get_session()
        try:
            genders = session.query(Gender).all()
            return [(g.id, g.name, g.description) for g in genders]
        finally:
            session.close()
    
    def get_damage_types(self):
        session = self._get_session()
        try:
            types = session.query(DamageType).all()
            return [(t.id, t.name, t.description) for t in types]
        finally:
            session.close()
    
    def get_intensities(self):
        session = self._get_session()
        try:
            intensities = session.query(Intensity).all()
            return [(i.id, i.name, i.description) for i in intensities]
        finally:
            session.close()
    
    def get_sensor_types(self):
        session = self._get_session()
        try:
            types = session.query(SensorType).all()
            return [(t.id, t.name, t.description) for t in types]
        finally:
            session.close()
    
    def get_effector_types(self):
        session = self._get_session()
        try:
            types = session.query(EffectorType).all()
            return [(t.id, t.name, t.description) for t in types]
        finally:
            session.close()

    # Adicione estes métodos à classe Database no database.py

    def get_grow_plants(self, grow_id):
        session = self._get_session()
        try:
            plants = session.query(Plant).filter_by(grow_id=grow_id).all()
            return [(p.id, p.grow_id, p.name, p.start_date, p.end_date, 
                    p.photoperiod_id, p.gender_id, p.harvested, p.yield_) for p in plants]
        finally:
            session.close()

    def get_grow_sensors(self, grow_id):
        session = self._get_session()
        try:
            sensors = session.query(Sensor).filter_by(grow_id=grow_id).all()
            return [(s.id, s.grow_id, s.ip, s.name, s.sensor_type_id, s.data_retention_days) for s in sensors]
        finally:
            session.close()

    def get_grow_effectors(self, grow_id):
        session = self._get_session()
        try:
            effectors = session.query(Effector).filter_by(grow_id=grow_id).all()
            return [(e.id, e.grow_id, e.effector_type_id, e.name, e.ip, e.normal_on, 
                    e.power_on, e.scheduled, e.on_time, e.off_time, e.bounded, 
                    e.bounded_sensor_id, e.threshold, 
                    e.last_request.strftime('%Y-%m-%d %H:%M:%S') if e.last_request else 'Never') for e in effectors]
        except Exception as e:
            print(f"Erro ao buscar effectors: {e}")
            return []
        finally:
            session.close()

    def get_plant_waterings(self, plant_id):
        return self.execute_query(
            "SELECT id, date, mililiter FROM watering WHERE plant_id = %s",
            (plant_id,)
        )

    def get_plant_damages(self, plant_id):
        return self.execute_query(
            "SELECT id, plant_id, damage_type_id, date, intensity_id FROM damage WHERE plant_id = %s",
            (plant_id,)
        )

    def get_plant_transplantings(self, plant_id):
        return self.execute_query(
            "SELECT id, plant_id, date, lenght, width, height, radius FROM transplanting WHERE plant_id = %s",
            (plant_id,)
        )

    def get_plant_feedings(self, plant_id):
        return self.execute_query(
            "SELECT id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium FROM feeding WHERE plant_id = %s",
            (plant_id,)
        )

    def insert_watering(self, plant_id, date, mililiter):
        return self.execute_query(
            "INSERT INTO watering (plant_id, date, mililiter) VALUES (%s, DATE(%s), %s)",
            (plant_id, date, mililiter)
        )

    def delete_watering(self, watering_id):
        return self.execute_query("DELETE FROM watering WHERE id = %s", (watering_id,))

    def insert_feeding(self, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium):
        return self.execute_query(
            "INSERT INTO feeding (plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium) VALUES (%s, DATE(%s), %s, %s, %s, %s, %s)",
            (plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium)
        )

    def update_grow(self, grow_id, name, lenght, width, height):
        session = self._get_session()
        try:
            grow = session.query(Grow).get(grow_id)
            if grow:
                grow.name = name
                grow.lenght = lenght
                grow.width = width
                grow.height = height
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_grow(self, grow_id):
        session = self._get_session()
        try:
            grow = session.query(Grow).get(grow_id)
            if grow:
                session.delete(grow)
                session.commit()
                return 1
            return 0
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def insert_sensor(self, grow_id, name, sensor_type_id, data_retention_days=1):
        session = self._get_session()
        try:
            new_sensor = Sensor(
                grow_id=grow_id,
                name=name,
                sensor_type_id=sensor_type_id,
                data_retention_days=data_retention_days  # Novo campo
            )
            session.add(new_sensor)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def update_sensor(self, sensor_id, name, sensor_type_id, ip, data_retention_days=1):
        session = self._get_session()
        try:
            sensor = session.query(Sensor).get(sensor_id)
            if sensor:
                sensor.name = name
                sensor.sensor_type_id = sensor_type_id
                sensor.ip = ip
                sensor.data_retention_days = data_retention_days
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_sensor(self, sensor_id):
        session = self._get_session()
        try:
            sensor = session.query(Sensor).get(sensor_id)
            if sensor:
                session.delete(sensor)
                session.commit()
                return 1
            return 0
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def insert_effector(self, grow_id, effector_type_id, name):
        session = self._get_session()
        try:
            new_effector = Effector(
                grow_id=grow_id,
                effector_type_id=effector_type_id,
                name=name
            )
            session.add(new_effector)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_effector(self, effector_id):
        session = self._get_session()
        try:
            effector = session.query(Effector).get(effector_id)
            if effector:
                session.delete(effector)
                session.commit()
                return 1
            return 0
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def get_effector(self, effector_id):
        session = self._get_session()
        try:
            effector = session.query(Effector).get(effector_id)
            if effector:
                return [(effector.id, effector.grow_id, effector.effector_type_id, 
                        effector.name, effector.ip, effector.normal_on, effector.power_on, 
                        effector.scheduled, effector.on_time, effector.off_time, 
                        effector.bounded, effector.bounded_sensor_id, effector.threshold,
                        effector.last_request.strftime('%Y-%m-%d %H:%M:%S') if effector.last_request else 'Never')]
            return []
        except Exception as e:
            print(f"Erro ao buscar effector: {e}")
            return []
        finally:
            session.close()

    def get_last_sensor_data_value(self, sensor_id):
        session = self._get_session()
        try:
            # Buscar o último registro da tabela sensor_data para este sensor
            last_data = session.query(SensorData)\
                .filter_by(sensor_id=sensor_id)\
                .order_by(SensorData.datetime.desc())\
                .first()
            
            if last_data:
                return [(last_data.value,)]
            else:
                # Se não houver dados, retorna 0
                return [(0,)]
        except SQLAlchemyError as e:
            print(f"Erro ao buscar último valor do sensor: {e}")
            return [(0,)]
        finally:
            session.close()

    def get_last_sensor_data_value_and_date(self, sensor_id):
        session = self._get_session()
        try:
            # Buscar o último registro da tabela sensor_data para este sensor
            last_data = session.query(SensorData)\
                .filter_by(sensor_id=sensor_id)\
                .order_by(SensorData.datetime.desc())\
                .first()
            
            if last_data:
                # Retorna tanto o valor quanto a datetime
                return [(last_data.value, last_data.datetime)]
            else:
                # Se não houver dados, retorna 0 e None
                return [(0, None)]
        except SQLAlchemyError as e:
            print(f"Erro ao buscar último valor e data do sensor: {e}")
            return [(0, None)]
        finally:
            session.close()

    def insert_sensor_data(self, sensor_id, value):
        session = self._get_session()
        try:
            # Buscar o sensor para obter os dias de retenção
            sensor = session.query(Sensor).get(sensor_id)
            retention_days = sensor.data_retention_days if sensor else 1
            
            # Inserir novo dado do sensor
            new_data = SensorData(sensor_id=sensor_id, value=value)
            session.add(new_data)
            
            # Atualizar último valor do sensor
            if sensor:
                sensor.last_sensor_value = value
            
            # Limpar dados antigos baseado no campo data_retention_days
            session.execute(
                text("DELETE FROM sensor_data WHERE sensor_id = :sensor_id AND datetime < NOW() - INTERVAL :days DAY"),
                {'sensor_id': sensor_id, 'days': retention_days}
            )
            
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def set_effector_power_on(self, effector_id, power_on):
        session = self._get_session()
        try:
            effector = session.query(Effector).get(effector_id)
            if effector:
                effector.power_on = power_on
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def update_effector(self, effector_id, name, effector_type_id, ip, normal_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold):
        session = self._get_session()
        try:
            effector = session.query(Effector).get(effector_id)
            if effector:
                effector.name = name
                effector.effector_type_id = effector_type_id
                effector.ip = ip
                effector.normal_on = normal_on
                effector.scheduled = scheduled
                effector.on_time = on_time
                effector.off_time = off_time
                effector.bounded = bounded
                # Converter para None se for 0 ou vazio
                effector.bounded_sensor_id = int(bounded_sensor_id) if bounded_sensor_id and int(bounded_sensor_id) > 0 else None
                effector.threshold = threshold
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def update_effector_request_time(self, effector_id):
        session = self._get_session()
        try:
            effector = session.query(Effector).get(effector_id)
            if effector:
                effector.last_request = datetime.now()
                session.commit()
                return True
            return False
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def get_sensor_data(self, sensor_id, limit=100000):
        session = self._get_session()
        try:
            # Buscar dados do sensor ordenados por data mais recente
            sensor_data = session.query(SensorData)\
                .filter_by(sensor_id=sensor_id)\
                .order_by(SensorData.datetime.desc())\
                .limit(limit)\
                .all()
            
            # Formatar para gráficos: [value, datetime] para cada ponto
            formatted_data = []
            for data in sensor_data:
                formatted_data.append([
                    float(data.value),  # valor como float
                    data.datetime.strftime('%Y-%m-%d %H:%M:%S')  # datetime como string
                ])
            
            return formatted_data
            
        except SQLAlchemyError as e:
            print(f"Erro ao buscar dados do sensor {sensor_id}: {e}")
            return []
        finally:
            session.close()