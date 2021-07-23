# coding: utf-8
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from assets.database import Base
from datetime import datetime as dt

#Table情報
class Data(Base):
    #TableNameの設定
    __tablename__ = "data"
    #Column情報を設定する
    id = Column(Integer, primary_key=True)
    Vessel = Column(String, unique=False)
    Carrier = Column(String, unique=False)
    Voyage = Column(String, unique=False)
    Service = Column(String, unique=False)
    Pod = Column(String, unique=False)
    ETA = Column(String, unique=False)
    Berthing = Column(String, unique=False)
    timestamp = Column(DateTime, default=dt.now())

    def __init__(self, Vessel=None, Carrier=None, Voyage=None,Service=None, Pod=None, ETA=None, Berthing=None ,timestamp=None):
        self.Vessel = Vessel
        self.Carrier = Carrier
        self.Voyage = Voyage
        self.Service = Service
        self.Pod = Pod
        self.ETA = ETA
        self.Berthing = Berthing
        self.timestamp = timestamp
