#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form

from forms import *
import psycopg2



#---------import psycopg2-------------------------------------------------------------------#
# App Config.
from config import SQLALCHEMY_DATABASE_URI, DEBUG
#----------------------------------------------------------------------------#
import os
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
db.create_all()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#----------------------------------------------------------------------------#

#Models
from models import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.all()

    data=[]
    cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

    for city in cities:
        venues_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == city[0]).filter(Venue.state == city[1])
        data.append({
          "city": city[0],
          "state": city[1],
          "venues": venues_city
        })

    
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
      
      search_term = request.form.get('search_term', '').strip()
      venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
      
      lists=[]
      for venue in venues:
            shows = Show.query.filter_by(venue_id=venue.id).all()
            num_upcoming = 0
            for show in shows:
                  if show.start_time>datetime.now():
                    num_upcoming+=1
            lists.append({"id":venue.id,"name":venue.name,"num_upcoming_shows":num_upcoming})
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
      response={
        "count": len(venues),
        "data": lists
      }
      return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id  
  detail_venue=Venue.query.get_or_404(venue_id)
  lists = db.session.query(Show).filter(Show.venue_id == venue_id)
  past_shows = []
  upcoming_shows = []
  for show in lists:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    show_add = {
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime('%m/%d/%Y')
        }

    if (show.start_time < datetime.now()):
        past_shows.append(show_add)
    else:
        upcoming_shows.append(show_add)
  print(detail_venue.facebook_link)
  print(detail_venue.website_link)
  data = vars(detail_venue)
  data['past_shows']=past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count']=len(past_shows)
  data['upcoming_shows_count']=len(upcoming_shows)
  print(data['genres'],"ranglar")
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form=VenueForm()
  if form.validate_on_submit():
        name=request.form['name']
        city=request.form['city']
        state=request.form['state']
        address=request.form['address']
        phone=request.form['phone']
        genres=request.form.getlist('genres')
        website_link=request.form['website_link']
        facebook_link=request.form['facebook_link']
        seeking_talent=form.seeking_talent.data
        seeking_description=request.form['seeking_description']
        image_link=request.form['image_link']
        
        venue=Venue(
                    name=name,
                    city=city,
                    state=state,
                    address=address,
                    phone=phone,
                    genres=genres,
                    website_link=website_link,
                    facebook_link=facebook_link,
                    seeking_talent=seeking_talent,
                    seeking_description=seeking_description,
                    image_link=image_link
                    )
        
        print(form.image_link.data,'shu keldimi')
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        db.session.close()
  else:
        for error in form.errors:
              flash(error)
        db.session.rollback()
        db.session.close()
  # try:
    
  #   db.session.add(venue)
  #   db.session.commit()
  #   flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # # TODO: insert form data as a new Venue record in the db, instead
  # # TODO: modify data to be the data object returned from db insertion
  
  
  # except:
  #     flash('An error occured. Venue ' + request.form['name'] + ' Could not be listed!')
  #     db.session.rollback()
  # finally:
  #     db.session.close()
      
  # on successful db insert, flash success
          
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/del', methods=['GET','DELETE'])
def delete_venue(venue_id):
      # venue = Venue.query.get_or_404(venue_id)
      try:
        db.session.query(Venue).filter(Venue.id == venue_id).delete()
        db.session.query(Show).filter(Show.venue_id==venue_id).delete()
        db.session.commit()
        flash(f'Venue was successfully deleted!', 'success')
      except:
        flash(f"Venue can't be deleted.", 'danger')
      finally:
        db.session.close()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
      return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
      data=[]
      artists=Artist.query.order_by(Artist.name).all()
      for artist in artists:
            data.append({
              'id':artist.id,
              'name':artist.name
            })
  # TODO: replace with real data returned from querying the database
  
      return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
      search_query = request.form.get("search_term", '')
      results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_query}%')).all()
      data = []

      for result in results:
        data.append({
          "id": result.id,
          "name": result.name,
          "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
        })
      
      response={
        "count": len(results),
        "data": data
      }
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
      return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
      past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()  
      past_shows = []
      for show in past_shows_query:  
          past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
          })
          
      upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()   
      upcoming_shows = []
      for show in upcoming_shows_query:
          upcoming_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
      
      artist=Artist.query.get_or_404(artist_id)
      # past_shows = []
      # past_shows_count = 0
      # upcoming_shows = []
      # upcoming_shows_count = 0
      # for show in artist.shows:
            
      #       if show.start_time > datetime.now():
      #           upcoming_shows_count += 1
      #           upcoming_shows.append({
      #               "venue_id": show.venue_id,
      #               "venue_name": show.venue.name,
      #               "venue_image_link": show.venue.image_link,
      #               "start_time": format_datetime(str(show.start_time))
      #           })
      #       if show.start_time < datetime.now():
      #           past_shows_count += 1
      #           past_shows.append({
      #               "venue_id": show.venue_id,
      #               "venue_name": show.venue.name,
      #               "venue_image_link": show.venue.image_link,
      #               "start_time": format_datetime(str(show.start_time))
      #           })
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
      data = {
            "id": artist_id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            # Put the dashes back into phone number
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows)
        }
  
      return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get_or_404(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
      artist = Artist.query.get_or_404(artist_id)
      form=ArtistForm(request.form)
      try:
        new_artist={
          "name":form.name.data,
          "city":form.city.data,
          "state":form.state.data,
          "phone":form.phone.data,
          "genres":form.genres.data,
          "website_link":form.website_link.data,
          "facebook_link":form.facebook_link.data,
          "seeking_venue":form.seeking_venue.data,
          "seeking_description":form.seeking_description.data,
          "image_link":form.image_link.data,
        }
        
        db.session.query(Artist).filter(Artist.id == artist_id).update(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated !')
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      
      
      except:
          flash('An error occured. Artist ' + request.form['name'] + ' Could not be updated!')
          db.session.rollback()
      finally:
        db.session.close()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<int:artist_id>/del', methods=['GET','DELETE'])
def delete_artist(artist_id):
      artist=Artist.query.get_or_404(artist_id)
      show=Artist.query.get_or_404(artist_id)
      try:
        db.session.query(Show).filter(Show.artist_id == artist_id).delete()
        db.session.query(Artist).filter(Artist.id == artist_id).delete()
        db.session.commit()
        flash(f'Successfully removed artist {artist.name}')
      except:
            db.session.rollback()
            flash(f'An error occurred deleting artist {artist.name}.')
      finally:
        db.session.close()
      return redirect(url_for('artists'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get_or_404(venue_id)
  if venue: 
      form.name.data = venue.name
      form.city.data = venue.city
      form.state.data = venue.state
      form.phone.data = venue.phone
      form.address.data = venue.address
      form.genres.data = venue.genres
      form.facebook_link.data = venue.facebook_link
      form.image_link.data = venue.image_link
      form.website_link.data = venue.website_link
      form.seeking_talent.data = venue.seeking_talent
      form.seeking_description.data = venue.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
      
      venue = Venue.query.get(venue_id)
      form=VenueForm(request.form)
      new_venue={
        "name":form.name.data,
        "city":form.city.data,
        "state":form.state.data,
        "address":form.address.data,
        "phone":form.phone.data,
        "genres":form.genres.data,
        "website_link":form.website_link.data,
        "facebook_link":form.facebook_link.data,
        "seeking_talent":form.seeking_talent.data,
        "seeking_description":form.seeking_description.data,
        "image_link":form.image_link.data,
      }
      
      try:
        
        db.session.query(Venue).filter(Venue.id == venue_id).update(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated !')
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      
      
      except:
          flash('An error occured. Venue ' + request.form['name'] + ' Could not be updated!')
          db.session.rollback()
      finally:
          db.session.close()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
      return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
    artist = Artist(
        name = form.name.data,
        genres = form.genres.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        website_link = form.website_link.data,
        facebook_link = form.facebook_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data,
        image_link = form.image_link.data,
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()
  
  for show in shows:
      # Can reference show.artist, show.venue
      data.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = request.form['start_time']
    # try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed')
    # except:
    #   db.session.rollback()
    #   flash('An error occurred. Show could not be listed.')
    # finally: 
    db.session.close()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)

