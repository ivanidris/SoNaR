from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from wtforms import validators

import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters


# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sonar.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
    + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# Create models
class BingSearch(db.Model):
    __tablename__ = 'bing_searches'

    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Text)
    url = db.Column(db.Text)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    query = db.Column(db.Text)
    search_date = db.Column(db.DateTime)
    flag = db.Column(db.Text)

    # Required for administrative interface.
    # For python 3 please use __str__ instead.
    def __unicode__(self):
        return self.title


class CseSearch(db.Model):
    __tablename__ = 'cse_searches'

    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text)
    html_snippet = db.Column(db.Text)
    search_date = db.Column(db.DateTime)

    def __unicode__(self):
        return self.link


class TwitterSearch(db.Model):
    __tablename__ = 'twitter_searches'
    __table_args__ = (
        db.Index('ix_twitter_searches_54c871099f02ec17', 'query', 'html'),
    )

    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text)
    html = db.Column(db.Text)
    search_date = db.Column(db.DateTime)

    def __unicode__(self):
        return self.html


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


# Create admin
admin = admin.Admin(app, name='SoNaR', template_mode='bootstrap3')

# Add views
admin.add_view(sqla.ModelView(BingSearch, db.session))
admin.add_view(sqla.ModelView(CseSearch, db.session))
admin.add_view(sqla.ModelView(TwitterSearch, db.session))


if __name__ == '__main__':
    app.run(debug=True)
