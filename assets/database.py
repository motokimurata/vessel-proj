# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import datetime
import os
import pandas as pd

databese_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.db')
engine = create_engine(os.environ.get('DATABASE_URL') or'sqlite:///' + databese_file, convert_unicode=True , echo=True)
db_session = scoped_session(
                sessionmaker(
                    autocommit = False,
                    autoflush = False,
                    bind = engine
                )
             )
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():    
    Base.metadata.create_all(bind=engine)
    db_session.close()

def read_data():
    from assets import models   

    df = pd.read_csv('assets/vessel_schedule.csv')
    for index,_df in df.iterrows():
        row = models.Data(Vessel= _df['vessel'], Carrier=_df['carrier'], Voyage = _df['voyage No.'],  Service = _df['service'], Pod = _df['POD'], ETA = _df['ETA'], Berthing = _df['Berthing'],)
        db_session.add(row)
    db_session.commit()
    db_session.close()