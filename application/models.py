from .database import db


class Admin(db.Model):
    __tablename__="admin"
    admin_email=db.Column(db.String,primary_key=True)
    admin_password=db.Column(db.String , nullable=False)
    admin_name=db.Column(db.String , nullable=False)


class Venue(db.Model):
    __tablename__="venue"
    venue_id=db.Column(	db.Integer, primary_key=True, autoincrement=True)
    venue_name=db.Column(db.String,  nullable=False)
    venue_location=db.Column(db.String,  nullable=False)
    venue_max_no_of_shows=db.Column(db.Integer,  nullable=False)
    venue_max_seats_per_show=db.Column(db.Integer,  nullable=False)
    venue_num_shows_added=db.Column(db.Integer, default=0)
    ven_shows=db.relationship("Show",secondary="show_in_venue",backref='show_vens')


class Tag(db.Model):
    __tablename__="tag"
    tag_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name=db.Column(db.String, unique=True)
    tag_shows=db.relationship("Show", secondary="tag_of_shows",backref="show_tags")



class Tag_of_shows(db.Model):
    __tablename__="tag_of_shows"
    tag_id=db.Column(db.Integer,db.ForeignKey("tag.tag_id"),primary_key=True)
    show_id=db.Column(db.Integer,db.ForeignKey("show.show_id"),primary_key=True)

class Show_in_venue(db.Model):
    __tablename__="show_in_venue"
    venue_id=db.Column(	db.Integer,db.ForeignKey("venue.venue_id"),primary_key=True)
    show_id=db.Column(db.Integer,db.ForeignKey("show.show_id"),primary_key=True)
    no_of_tickets_booked=db.Column(db.Integer, default=0)
    show_housefull_flag=db.Column(db.Integer, default=0)




class Show(db.Model):
    __tablename__="show"
    show_id=db.Column(db.Integer, primary_key=True,  autoincrement=True)
    show_name=db.Column(db.String, nullable=False)
    show_rating=db.Column(db.Numeric(1,1))
    show_price_per_ticket=db.Column(db.Integer)
    show_num_ratings=db.Column(db.Integer, default=0)
    show_total_rating=db.Column(db.Integer, default=0)




class Ticket(db.Model):
    __tablename__="ticket"
    ticket_id=db.Column(db.Integer, primary_key=True,  autoincrement=True)
    user_email=db.Column(db.String, db.ForeignKey("user.user_email"), nullable=False)
    ticket_total_price=db.Column(db.Integer)
    ticket_num_tickets=db.Column(db.Integer)
    show_id=db.Column(db.Integer)
    venue_id=db.Column(db.Integer)


    

class User(db.Model):
    __tablename__="user"
    user_email=db.Column(db.String,primary_key=True)
    user_password=db.Column(db.String , nullable=False)
    user_name=db.Column(db.String , nullable=False)
    user_tickets=db.relationship("Ticket")