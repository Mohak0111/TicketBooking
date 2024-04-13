from flask_restful import Resource, fields, marshal_with, reqparse
from application.database import db
from application.models import *
from application.validation import  NotFoundError

admins=Admin.query.all()
admin_emails_from_db=[admin.admin_email for admin in admins]

create_venue_parser=reqparse.RequestParser()
create_venue_parser.add_argument('venue_name')
create_venue_parser.add_argument('venue_location')
create_venue_parser.add_argument('venue_max_no_of_shows')
create_venue_parser.add_argument('venue_max_seats_per_show')


get_show_parser=reqparse.RequestParser()
get_show_parser.add_argument('show_name')

get_venue_parser=reqparse.RequestParser()
get_venue_parser.add_argument('venue_name')


show_get_fields={
    "show_name":fields.String,
    "show_rating":fields.Float,
    "show_price_per_ticket":fields.Integer
}

venue_get_fields={
    "venue_name":fields.String,
    "venue_location": fields.String,
    "venue_max_no_of_shows": fields.Integer,
    "venue_max_seats_per_show": fields.Integer,
    "venue_num_shows_added": fields.Integer,
}

class ShowAPI(Resource):
    @marshal_with(show_get_fields)
    def get(self,admin_email):
        if not (admin_email in admin_emails_from_db):
            raise NotFoundError(status_code=404)
        args=get_show_parser.parse_args()
        show_name=args.get('show_name',None)
        show=Show.query.filter(Show.show_name.ilike(f'%{show_name}%')).first()
        if show:
            return show
        else:
            raise NotFoundError(status_code=404)


class VenueAPI(Resource):
    @marshal_with(venue_get_fields)
    def get(self,admin_email):
        if not (admin_email in admin_emails_from_db):
            raise NotFoundError(status_code=404)
        args=get_venue_parser.parse_args()
        venue_name=args.get('venue_name',None)
        venue=Venue.query.filter(Venue.venue_name.ilike(f'%{venue_name}%')).first()
        if venue:
            return venue
        else:
            raise NotFoundError(status_code=404)


    @marshal_with(venue_get_fields)
    def post(self,admin_email):
        if not (admin_email in admin_emails_from_db):
            raise NotFoundError(status_code=404)
        args=create_venue_parser.parse_args()


        venue_name=args.get('venue_name',None)
        venue_location=args.get('venue_location',None)
        venue_max_no_of_shows=args.get('venue_max_no_of_shows',None)
        venue_max_seats_per_show=args.get('venue_max_seats_per_show',None)

        try:
            venue=Venue(venue_name=venue_name,venue_location=venue_location,venue_max_no_of_shows=venue_max_no_of_shows,venue_max_seats_per_show=venue_max_seats_per_show)
            db.session.add(venue)
            db.session.commit()
        except:
            raise NotFoundError(status_code=404)



        if venue:
            return venue
        else:
            raise NotFoundError(status_code=404)