from flask import request,redirect,url_for
from flask import render_template
from flask import current_app as app
from application.models import *

logged_user_id=None
logged_admin_id=None

@app.route('/')
def home():
    return render_template('index.html')




@app.route('/admin',methods=['POST','GET'])
def admin():
    global logged_admin_id
    if not logged_admin_id:
        error=None
        if request.method=="POST":
            email=request.form.get('admin_username')
            passw=request.form.get('admin_password')
            admin_from_db=Admin.query.filter(Admin.admin_email==email).first()
            if admin_from_db:
                if passw==admin_from_db.admin_password:
                    logged_admin_id=admin_from_db.admin_email
                    venues=Venue.query.all()
                    return(render_template('admin_dashboard.html',adminname=admin_from_db.admin_name, venues=venues))
                    # return redirect(url_for('admin_dashboard',adminname=admin_from_db.admin_name))
                else:
                    error="wrong password"
            else:
                error="wrong email"
        return render_template('admin_login.html',error=error)
    else:
            venues=Venue.query.all()
            admin_from_db=Admin.query.get(logged_admin_id)
            return(render_template('admin_dashboard.html',adminname=admin_from_db.admin_name, venues=venues))
        
@app.route("/admin_summary")
def admin_summary():
    global logged_admin_id
    if not logged_admin_id:
        return redirect(url_for("admin"))
    shows=Show.query.all()
    show_in_venues=Show_in_venue.query.all()
    return render_template('admin_summary.html',shows=shows,show_in_venues=show_in_venues)


@app.route("/venue_create",methods=["GET","POST"])
def venue_create():
    global logged_admin_id
    if not logged_admin_id:
        return redirect(url_for('admin'))
    if request.method=="POST":
        name=request.form.get('venue_name')
        location=request.form.get("venue_location")
        max_no_of_shows=request.form.get("venue_max_no_of_shows")
        max_seats_per_show=request.form.get("venue_max_seats_per_show")
        newven=Venue(venue_name=name,venue_location=location,venue_max_no_of_shows=max_no_of_shows,venue_max_seats_per_show=max_seats_per_show)
        db.session.add(newven)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('venue_create.html')

@app.route("/venue_edit", methods=["GET","POST"])
def venue_edit():
    global logged_admin_id
    if not logged_admin_id:
        return redirect(url_for('admin'))
    if request.method=="POST":
        ven_id=request.form.get('ven_id')
        edit_venue=Venue.query.get(ven_id)
        name=request.form.get('venue_name')
        location=request.form.get("venue_location")
        max_no_of_shows=request.form.get("venue_max_no_of_shows")
        max_seats_per_show=request.form.get("venue_max_seats_per_show")
        edit_venue.venue_name, edit_venue.venue_location, edit_venue.venue_max_no_of_shows, edit_venue.venue_max_seats_per_show=name, location, max_no_of_shows, max_seats_per_show
        db.session.commit()
        return redirect(url_for('admin'))
    venues=Venue.query.all()
    return render_template('venue_edit.html',venues=venues)    

@app.route("/venue_delete", methods=["GET","POST"])
def venue_delete():
    global logged_admin_id
    if not logged_admin_id:
        return redirect(url_for('admin'))
    if request.method=="POST":
        ven_id=request.form.get('ven_id')
        tickets=Ticket.query.filter(Ticket.venue_id==ven_id).all()
        for bye_ticket in tickets:
            db.session.delete(bye_ticket)
            db.session.commit()
        bye_venue=Venue.query.get(ven_id)
        db.session.delete(bye_venue)
        db.session.commit()
    venues=Venue.query.all()
    return render_template('venue_delete.html',venues=venues)








@app.route("/show_create",methods=["GET","POST"])
def show_create():
    global logged_admin_id
    if not logged_admin_id:
        return redirect(url_for('admin'))
    if request.method=="POST":
        name=request.form.get('show_name')
        rating=request.form.get('show_rating')
        price=request.form.get('price')
        new_show=Show(show_name=name,show_rating=rating,show_price_per_ticket=price)
        vens=request.form.getlist("option")
        for i in vens:
            ven=Venue.query.get(int(i))
            ven.venue_num_shows_added+=1
            new_show.show_vens.append(ven)            
        tags=request.form.get('tags')
        tags=[x.strip() for x in tags.split(",")]
        for i in tags:
            # get/create tag and append it in show_tags
            tag=Tag.query.filter(Tag.tag_name==i).first()
            if not tag:
                tag=Tag(tag_name=i)
            new_show.show_tags.append(tag)
        db.session.add(new_show)
        db.session.commit()
        return redirect(url_for('admin'))
    venues=Venue.query.filter(Venue.venue_num_shows_added<Venue.venue_max_no_of_shows).all()
    return render_template('show_create.html',venues=venues)

@app.route("/show_edit", methods=["GET","POST"])
def show_edit():
    global logged_admin_id
    if not logged_admin_id:
        return redirect(url_for('admin'))
    if request.method=="POST":
        show_id=request.form.get('show_id')
        edit_show=Show.query.get(show_id)

        name=request.form.get('show_name')
        rating=request.form.get("show_rating")
        price=request.form.get('price')
        vens=request.form.getlist("option")
        vens=[Venue.query.get(int(i)) for i in vens]


        # remove unchecked venues which were previously checked and update the numshows:
        for i in edit_show.show_vens:
            if i not in vens:
                edit_show.show_vens.remove(i)
                i.venue_num_shows_added-=1
                tickets=Ticket.query.filter(Ticket.show_id==show_id, Ticket.venue_id==i.venue_id).all()
                for bye_ticket in tickets:
                    db.session.delete(bye_ticket)
        
        # add checked venues which were previously unchecked and update the numshows:
        for i in vens:
            if i not in edit_show.show_vens:
                edit_show.show_vens.append(i)
                i.venue_num_shows_added+=1
        
        
        tags=request.form.get('tags')
        tags=[x.strip() for x in tags.split(",")]

        taglis=[]
        for i in tags:
            x=Tag.query.filter(Tag.tag_name==i).first()
            if not x:
                x=Tag(tag_name=i)
            taglis.append(x)
        
        edit_show.show_tags=[]
        edit_show.show_tags=taglis



        print(edit_show.show_vens, edit_show.show_tags)
        edit_show.show_name=name
        edit_show.show_rating=rating
        edit_show.show_price_per_ticket=price
        db.session.commit()
        
        return redirect(url_for("admin"))
    shows=Show.query.all()
    venues=Venue.query.filter(Venue.venue_num_shows_added<Venue.venue_max_no_of_shows).all()
    return render_template("show_edit.html", shows=shows, venues=venues)

@app.route("/show_delete", methods=["GET","POST"])
def show_delete():
    global logged_admin_id
    if not logged_admin_id:
        return redirect(url_for('admin'))
    if request.method=="POST":
        show_id=request.form.get('show_id')
        bye_show=Show.query.get(int(show_id))
        tickets=Ticket.query.filter(Ticket.show_id==int(show_id))
        for bye_ticket in tickets:
            db.session.delete(bye_ticket)
            db.session.commit()
        for i in bye_show.show_vens:
            i.venue_num_shows_added-=1
        db.session.delete(bye_show)
        db.session.commit()
    shows=Show.query.all()
    return render_template('show_delete.html',shows=shows)

@app.route("/search",methods=["GET","POST"])
def search():
    result=[]
    global logged_user_id
    if not logged_user_id:
        return redirect(url_for('user_login'))
    if request.method=="POST":
        search_field=request.form.get("field")
        if search_field=="venue_name":
            venue_name=request.form.get("venue_name_input")
            result=Venue.query.filter(Venue.venue_name.ilike(f'%{venue_name}%')).all()
        if search_field=="show_name":
            show_name=request.form.get("show_name_input")
            shows=Show.query.filter(Show.show_name.ilike(f'%{show_name}%')).all()
            for show in shows:
                for venue in show.show_vens:
                    result.append(venue)
            result=list(set(result))
        if search_field=="location":
            venue_location=request.form.get("location_input")
            result=Venue.query.filter(Venue.venue_location.ilike(f'%{venue_location}%')).all()
        if search_field=="tag":
            tag_name=request.form.get("tag_input")
            tags=Tag.query.filter(Tag.tag_name.ilike(f'%{tag_name}%')).all()
            for tag in tags:
                for show in tag.tag_shows:
                    for venue in show.show_vens:
                        result.append(venue)
            result=list(set(result))

    return render_template('search.html',venues=result)



@app.route('/user_register',methods=["GET","POST"])
def user_register():
    global logged_user_id
    if not logged_user_id:
        error=None
        if request.method=="POST":
            email=request.form.get('user_username')
            user_from_db=User.query.filter(User.user_email==email).first()
            name=request.form.get('name')
            passw=request.form.get('user_password')
            if not user_from_db:
                confirm_passw=request.form.get('user_password_confirm')
                if passw==confirm_passw:
                    new_user=User(user_email=email,user_password=passw,user_name=name)
                    db.session.add(new_user)
                    db.session.commit()
                    return redirect(url_for('user_login'))
                else:
                    error="passwords do not match"
            else:
                error="user already exists"
        return render_template('user_register.html',error=error)
    return redirect(url_for("user_dashboard"))


@app.route('/user_login',methods=["GET","POST"])
def user_login():
    global logged_user_id
    if not logged_user_id:
        error=None
        if request.method=="POST":
            email=request.form.get('user_username')
            passw=request.form.get('user_password')
            user_from_db=User.query.filter(User.user_email==email).first()
            if user_from_db:
                if passw==user_from_db.user_password:
                    logged_user_id=user_from_db.user_email
                    return redirect(url_for("user_dashboard"))
                else:
                    error="wrong password"
            else:
                error="wrong email"
        return render_template('user_login.html',error=error)
    return redirect(url_for('user_dashboard'))


@app.route('/user_dashboard')
def user_dashboard():
    global logged_user_id
    if not logged_user_id:
        return redirect(url_for('user_login'))
    venues=Venue.query.all()
    show_in_venue=Show_in_venue.query.all()
    user_from_db=User.query.get(logged_user_id)
    return render_template('user_dashboard.html',venues=venues,user_name=user_from_db.user_name,show_in_venue=show_in_venue)


# put housefull flag in Show_in_venue
@app.route('/user_book',methods=["GET","POST"])
def user_book():
    global logged_user_id
    housefull=False
    if not logged_user_id:
        return redirect(url_for('user_login'))
    
    venue_id=request.args.get('venue_id',None)
    show_id=request.args.get('show_id',None)
    if not (venue_id or show_id):
        return(redirect(url_for('user_login')))
    venue=Venue.query.get(int(venue_id))
    show=Show.query.get(int(show_id))
    if request.method=="GET":
        no_of_tickets_booked=Show_in_venue.query.get((int(venue_id),int(show_id))).no_of_tickets_booked
        no_of_tickets_available=venue.venue_max_seats_per_show-no_of_tickets_booked

        return render_template("user_book.html",show=show,venue=venue,no_of_tickets_available=no_of_tickets_available)
    elif request.method=="POST":
        no_of_tickets_to_purchase=int(request.form.get("no_of_tickets_to_purchase"))
        total_price=no_of_tickets_to_purchase*int(show.show_price_per_ticket)
        # show_id venue_id logged_user_id
        ticket=Ticket.query.filter(Ticket.user_email==logged_user_id,Ticket.show_id==show_id, Ticket.venue_id==venue_id).first()
        if not ticket:
            ticket=Ticket(user_email=logged_user_id,show_id=show_id, venue_id=venue_id,ticket_total_price=total_price,ticket_num_tickets=no_of_tickets_to_purchase)
            db.session.add(ticket)
            db.session.commit()
        else:
            ticket.ticket_total_price+=total_price
            ticket.ticket_num_tickets+=no_of_tickets_to_purchase
            db.session.commit()
        # update no_of_tickets_booked and housefull_flag
        show_in_venue=Show_in_venue.query.get((venue_id,show_id))
        show_in_venue.no_of_tickets_booked+=no_of_tickets_to_purchase
        if show_in_venue.no_of_tickets_booked==venue.venue_max_seats_per_show:
            show_in_venue.show_housefull_flag=1
        db.session.commit()
        return(redirect(url_for('user_dashboard')))

@app.route('/user_bookings')
def user_bookings():
    global logged_user_id
    if not logged_user_id:
        return redirect(url_for("user_login"))
    user=User.query.get(logged_user_id)
    venues,shows=[],[]
    for i in user.user_tickets:
        venue,show=Venue.query.get(i.venue_id),Show.query.get(i.show_id)
        venues.append(venue)
        shows.append(show)
    venues,shows=set(venues),set(shows)
    print(venues,shows)
    return render_template("user_bookings.html",user=user, venues=venues, shows=shows)

@app.route('/user_rating',methods=["GET","POST"])
def user_rating():
    global logged_user_id
    if not logged_user_id:
        return redirect(url_for('user_login'))
    show_id=request.args.get('show_id')
    show=Show.query.get(show_id)
    if request.method=="POST":
        rating=request.form.get("rating")
        show.show_num_ratings+=1
        show.show_total_rating+=int(rating)
        show_rating=round(show.show_total_rating/show.show_num_ratings,1)
        show.show_rating=show_rating
        db.session.commit()
        return redirect(url_for("user_dashboard"))
    return render_template("user_rating.html",show=show)


@app.route('/log_out')
def log_out():
    global logged_admin_id
    global logged_user_id
    logged_admin_id=None
    logged_user_id=None
    return redirect(url_for('home'))