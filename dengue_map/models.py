from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float
from dengue_map import app

db = SQLAlchemy(app)


class Provinces(db.Model):
    # define the dictionary structure
    id = Column(Integer, primary_key=True)
    name1 = Column(String(100))
    name2 = Column(String(100))
    varname = Column(String(100))
    engtype = Column(String(100))
    prov_id = Column(Integer, unique=True)
    provtype = Column(String(50))
    isocode = Column(String(20))
    geometry = Column(db.Text)

    class Meta:
        db_table = 'provinces'

    def publish(self):
        self.save()

    def get_id(self):
        return self.id
