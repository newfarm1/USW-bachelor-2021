from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import text
from datetime import datetime
from time import sleep
import queue

sq = queue.Queue()
#"mysql://root:cake@localhost/food_storage"
db_uri = "sqlite:///data.db?check_same_thread=False"
engine = create_engine(db_uri)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()
Base = declarative_base()

class Decrypted(Base):

    __tablename__ = "decrypted"
    hash_code = Column(String, primary_key=True)
    hash_type = Column(Integer)
    password_plain = Column(String)


    def __init__(self, hash_code, hash_type, password_plain):
        self.hash_code = hash_code
        self.hash_type = hash_type
        self.password_plain = password_plain

    def ingest(hash_code, hash_type, password_plain):
        ingest = Decrypted(hash_code, hash_type, password_plain)
        session.add(ingest)
        session.commit()
        Session.remove()

    def everything():
        everything = session.query(Decrypted).all()
        Session.remove()
        return everything

class Ongoing_job(Base):

    __tablename__ = "ongoing_job"
    task_nr = Column(Integer, primary_key=True, autoincrement=True)
    attack_type = Column(String)
    hash_code = Column(String)
    job = Column(String)
    algo = Column(Integer)
    ongoing = Column(Boolean)
    worker = Column(String)


    def __init__(self, attack_type, hash_code, job, algo, ongoing, worker):
        self.attack_type = attack_type
        self.hash_code = hash_code
        self.job = job
        self.algo = algo
        self.ongoing = ongoing
        self.worker = worker


    def ingest(attack_type, hash_code, job, algo):
        ingest = Ongoing_job(attack_type, hash_code, job, algo, 0, "")
        session.add(ingest)
        session.commit()
        Session.remove()

    def get_next():
        next_queue = session.query(Ongoing_job).filter(Ongoing_job.ongoing == 0).first()
        Session.remove()
        return next_queue

    def working(task_nr, worker):
        session.query(Ongoing_job).filter(Ongoing_job.task_nr == task_nr).update({'ongoing': 1, 'worker':str(worker)})
        session.commit()
        Session.remove()

    def task_done(work_id):
        session.query(Ongoing_job).filter(Ongoing_job.task_nr == work_id).delete()
        session.commit()
        Session.remove()


    def revert(ip):
        session.query(Ongoing_job).filter(Ongoing_job.worker == str(ip)).update({'ongoing': 0, 'worker':'DC'})
        session.commit()
        Session.remove()
        

    def cleanup():
        cleaning = True
        while cleaning:
            clean = Ongoing_job.get_next()
            
            if clean:
                print(f' Cleaning task {clean.task_nr}')
                Ongoing_job.task_done(clean.task_nr)
            else:
                cleaning = False

    def full_queue():
        full_queue = session.query(Ongoing_job).all()
        Session.remove()
        return full_queue

class Decrypt_queue(Base):

    __tablename__ = "decrypt_queue"
    task_nr = Column(Integer, primary_key=True, autoincrement=True)
    algo = Column(Integer)
    hash_code = Column(String)
    decrypt_type = Column(String)
    ongoing = Column(Boolean)
    setting1 = Column(String)
    setting2 = Column(String)



    def __init__(self, algo, hash_code, decrypt_type, ongoing, setting1, setting2):
        self.algo = algo
        self.hash_code = hash_code
        self.decrypt_type = decrypt_type
        self.ongoing = ongoing
        self.setting1 = setting1
        self.setting2 = setting2

    def ingest(algo, hash_code, decrypt_type, ongoing, setting1, setting2):
        ingest = Decrypt_queue(algo, hash_code, decrypt_type, ongoing, setting1, setting2)
        session.add(ingest)
        session.commit()
        Session.remove()

    def queue():
        queue = session.query(Decrypt_queue).first()
        Session.remove()
        return queue

    def ongoing_task(task):
        session.query(Decrypt_queue).filter(Decrypt_queue.task_nr == task).update({'ongoing': 1})
        session.commit()
        Session.remove()

    def full_queue():
        full_queue = session.query(Decrypt_queue).all()
        Session.remove()
        return full_queue

    def done():
        session.query(Decrypt_queue).filter(Decrypt_queue.ongoing == 1).delete()
        session.commit()
        Session.remove()



class Machines(Base):

    __tablename__ = "machines"
    ip = Column(String, primary_key=True)
    gpu = Column(String)
    task = Column(Integer)
    last_task = Column(String)




    def __init__(self, ip, gpu, task, last_task):
        self.ip = ip
        self.gpu = gpu
        self.task = task
        self.last_task = last_task

    def ingest(ip, gpu):
        ingest = Machines(str(ip), gpu, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        session.add(ingest)
        session.commit()
        Session.remove()

    def get():
        machines = session.query(Machines).all()
        Session.remove()
        return machines

    def update(ip, task):
        session.query(Machines).filter(Machines.ip == str(ip)).update({'task': task, 'last_task': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        session.commit()
        Session.remove()    

    def dc(ip):
        session.query(Machines).filter(Machines.ip == str(ip)).delete()
        session.commit()
        Session.remove()

class Hashes(Base):

    __tablename__ = "hashes"
    mode = Column(Integer, primary_key=True)
    hash_name = Column(String)


    def __init__(self, mode, hash_name):
        self.mode = mode
        self.hash_name = hash_name


    def hashes_get():
        hashes = session.query(Hashes).all()
        Session.remove()
        return hashes

    def ingest(hash_mode, hash_name):
        ingest = Hashes(hash_mode, hash_name)
        session.add(ingest)
        session.commit()
        Session.remove()

    def hashes_spesific(mode):
        hashes = session.query(Hashes).filter(Hashes.mode == int(mode)).first()
        Session.remove()
        return hashes



def table_check():
    metadata = MetaData(engine)
    if not(engine.dialect.has_table(engine, 'decrypted')):
        Table('decrypted', metadata,
        Column('hash_code', String(80), primary_key=True),
        Column('hash_type', Integer),
        Column('password_plain', String(30)))
        metadata.create_all()

    if not(engine.dialect.has_table(engine, 'ongoing_job')):
        Table('ongoing_job', metadata,
        Column('task_nr', Integer, primary_key=True, autoincrement=True),
        Column('attack_type', String(80)),
        Column('hash_code', String(80)),
        Column('job', String(80)),
        Column('algo', Integer),
        Column('ongoing', Boolean),
        Column('worker', String(20)))
        metadata.create_all()





    if not(engine.dialect.has_table(engine, 'decrypt_queue')):
        Table('decrypt_queue', metadata,
        Column('task_nr', Integer, primary_key=True, autoincrement=True),
        Column('algo', Integer),
        Column('hash_code', String(80)),
        Column('decrypt_type', String(80)),
        Column('ongoing', Boolean),
        Column('setting1', String(80)),
        Column('setting2', String(80)))
        metadata.create_all()


    if not(engine.dialect.has_table(engine, 'machines')):
        Table('machines', metadata,
        Column('ip', String(80), primary_key=True),
        Column('gpu', String(80)),
        Column('task', Integer),
        Column('last_task', String(80)))
        metadata.create_all()

    if not(engine.dialect.has_table(engine, 'hashes')):
        Table('hashes', metadata,
        Column('mode', Integer, primary_key=True),
        Column('hash_name', String(80)))
        metadata.create_all()
    
