# coding: utf-8
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from assets.database import Base
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from sqlalchemy.schema import UniqueConstraint

#Table情報
class Data(Base):
    #TableNameの設定
    __tablename__ = "data"
    #Unique制約
    __table_args__ = (UniqueConstraint('Vessel','Carrier','Voyage','Service','Pod','ETA','Berthing'),{})
    #Column情報を設定する
    id = Column(Integer, primary_key=True)
    Vessel = Column(String)
    Carrier = Column(String)
    Voyage = Column(String)
    Service = Column(String)
    Pod = Column(String)
    ETA = Column(String)
    Berthing = Column(String)
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
