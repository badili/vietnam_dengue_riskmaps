from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float
from dengue_map import app

db = SQLAlchemy(app)


class Counties(db.Model):
    id = Column(Integer, primary_key=True)
    code = Column(String(10), index=True, unique=True)
    county_name = Column(String(70), index=True, unique=True)
    center_lat = Column(Float(11, 2))
    center_lon = Column(Float(12, 3))
    geometry = Column(db.Text)

    class Meta:
        db_table = 'counties'

    def publish(self):
        self.save()


class Posts(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(45), index=True, unique=True)
    representation_area = Column(String(45))

    class Meta:
        db_table = 'posts'

    def publish(self):
        self.save()


class CountyVoterCount(db.Model):
    id = Column(Integer, primary_key=True)
    county_id = Column(Integer, ForeignKey('counties.id'), nullable=False)
    year = Column(Integer)
    total_voters = Column(Integer)

    class Meta:
        db_table = 'county_voter_count'

    def publish(self):
        self.save()

class Constituencies(db.Model):
    id = Column(Integer, primary_key=True)
    code = Column(String(10), index=True, unique=True)
    county_id = Column(Integer, ForeignKey('counties.id'), nullable=False)
    constituency_name = Column(String(70), index=True, unique=True)
    center_lat = Column(Float(11, 2))
    center_lon = Column(Float(12, 3))
    geometry = Column(db.Text)

    class Meta:
        db_table = 'constituencies'

    def publish(self):
        self.save()


class ConstituencyVoterCount(db.Model):
    id = Column(Integer, primary_key=True)
    constituency_id = Column(Integer, ForeignKey('constituencies.id'), nullable=False)
    year = Column(Integer)
    total_voters = Column(Integer)

    class Meta:
        db_table = 'constituencies_voter_count'

    def publish(self):
        self.save()


class Wards(db.Model):
    id = Column(Integer, primary_key=True)
    code = Column(String(70), index=True, unique=True)
    constituency_id = Column(Integer, ForeignKey('constituencies.id'), nullable=False)
    county_id = Column(Integer, ForeignKey('counties.id'), nullable=False)
    ward_name = Column(String(70), index=True, unique=True)
    center_lat = Column(Float(11, 2))
    center_lon = Column(Float(12, 3))
    geometry = Column(db.Text)

    class Meta:
        db_table = 'wards'

    def publish(self):
        self.save()


class WardVoterCount(db.Model):
    id = Column(Integer, primary_key=True)
    ward_id = Column(Integer, ForeignKey('wards.id'), nullable=False)
    year = Column(Integer)
    total_voters = Column(Integer)

    class Meta:
        db_table = 'ward_voter_count'

    def publish(self):
        self.save()


class ConstList(db.Model):
    id = Column(Integer, primary_key=True)
    county = Column(String(100))
    county_code = Column(String(100))
    const_code = Column(String(100))
    constituency = Column(String(100))

    class Meta:
        db_table = 'const_list'

    def publish(self):
        self.save()


class PollingStations(db.Model):
    id = Column(Integer, primary_key=True)
    county_code = Column(Integer)
    county_name = Column(String(15))
    constituency_code = Column(Integer)
    constituency_name = Column(String(19))
    caw_code = Column(Integer)
    caw_name = Column(String(26))
    reg_centre_code = Column(Integer)
    reg_centre_name = Column(String(54))
    voters_per_reg_centre = Column(String(10))
    polling_station_code = Column(String(20))
    polling_station_name = Column(String(54))
    voters_per_polling_station = Column(Integer)

    class Meta:
        db_table = 'polling_stations'

    def publish(self):
        self.save()


class ProvResults(db.Model):
    id = Column(Integer, primary_key=True)
    poll_station_id = Column(Integer, ForeignKey('polling_stations.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    iebc_timestamp = Column(String(100))
    saving_timestamp = Column(String(100))
    total_stations = Column(String(100))
    reporting_stations = Column(String(100))
    t_votes = Column(Integer)
    _abstention = Column(Integer)
    _census = Column(Integer)
    _blank = Column(Integer)
    _null = Column(Integer)

    class Meta:
        db_table = 'prov_results'

    def publish(self):
        self.save()


class CountyProvResults(db.Model):
    id = Column(Integer, primary_key=True)
    county_id = Column(Integer, ForeignKey('counties.id'), nullable=False)
    prov_results_id = Column(Integer, ForeignKey('prov_results.id'), nullable=False)
    aspirant_name = Column(String(70))
    party = Column(String(10))
    color = Column(String(15))
    presential = Column(Integer)
    international = Column(Integer)
    perc = Column(Float(8, 4))
    absentee = Column(Integer)
    special = Column(Integer)
    iebc_id = Column(Integer)
    ranking = Column(Integer)

    class Meta:
        db_table = 'county_prov_results'

    def publish(self):
        self.save()


class PollingStationsProvResults(db.Model):
    id = Column(Integer, primary_key=True)
    prov_results_id = Column(Integer, ForeignKey('prov_results.id'), nullable=False)
    aspirant_name = Column(String(70))
    party = Column(String(10))
    color = Column(String(15))
    presential = Column(Integer)
    international = Column(Integer)
    perc = Column(Float(8, 4))
    absentee = Column(Integer)
    special = Column(Integer)
    iebc_id = Column(Integer)
    ranking = Column(Integer)

    class Meta:
        db_table = 'county_prov_results'

    def publish(self):
        self.save()


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
