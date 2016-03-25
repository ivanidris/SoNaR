from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_admin as admin
from flask_admin.contrib import sqla
from jinja2 import Markup
from flask_admin.contrib.sqla import ModelView


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

    def __str__(self):
        return self.title


class CseSearch(db.Model):
    __tablename__ = 'cse_searches'

    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text)
    html_snippet = db.Column(db.Text)
    search_date = db.Column(db.DateTime)

    def __str__(self):
        return self.link


class CodeKeyword(db.Model):
    __tablename__ = 'code_keywords'

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.Text)
    tfidf = db.Column(db.Text)
    Flag = db.Column(db.Text)


class ExcludeUrl(db.Model):
    __tablename__ = 'exclude_urls'

    id = db.Column(db.Integer, primary_key=True)
    Added = db.Column(db.Text)
    URL = db.Column(db.Text)


class Feed(db.Model):
    __tablename__ = 'feeds'

    id = db.Column(db.Integer, primary_key=True)
    URL = db.Column(db.Text)
    Added = db.Column(db.Text)
    Flag = db.Column(db.Text)


class Keyword(db.Model):
    __tablename__ = 'keywords'

    id = db.Column(db.Integer, primary_key=True)
    Term = db.Column(db.Text)
    Added = db.Column(db.Text)
    Flag = db.Column(db.Text)


class TwitterSearch(db.Model):
    __tablename__ = 'twitter_searches'
    __table_args__ = (
        db.Index('ix_twitter_searches_54c871099f02ec17', 'query', 'html'),
    )

    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text)
    html = db.Column(db.Text)
    search_date = db.Column(db.DateTime)

    def __str__(self):
        return self.html


class TwitterUser(db.Model):
    __tablename__ = 'twitter_users'

    id = db.Column(db.Integer, primary_key=True)
    URL = db.Column(db.Text)
    Date = db.Column(db.Text)
    Flag = db.Column(db.Text)


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


# Create admin
admin = admin.Admin(app, name='SoNaR', template_mode='bootstrap3')


# Add views
class BingSearchAdmin(sqla.ModelView):
    def _url_formatter(view, context, model, name):
        return Markup('<a href={0}>{0}</a>'.format(model.url))

    column_formatters = {'url': _url_formatter}
    column_default_sort = ('search_date', True)

admin.add_view(BingSearchAdmin(BingSearch, db.session))
admin.add_view(ModelView(CodeKeyword, db.session))


class CseSearchAdmin(sqla.ModelView):
    def _html_formatter(view, context, model, name):
        return Markup('<a href={0}>{0}</a>'.format(model.link))

    def _snippet_formatter(view, context, model, name):
        return Markup(model.html_snippet)

    column_formatters = {'link': _html_formatter,
                         'html_snippet': _snippet_formatter}
    column_default_sort = ('search_date', True)

admin.add_view(CseSearchAdmin(CseSearch, db.session))
admin.add_view(ModelView(ExcludeUrl, db.session))
admin.add_view(ModelView(Feed, db.session))


class KeywordAdmin(sqla.ModelView):
    column_default_sort = ('Added', True)

admin.add_view(KeywordAdmin(Keyword, db.session))


class TwitterSearchAdmin(sqla.ModelView):
    def _html_formatter(view, context, model, name):
        return Markup(model.html)

    column_formatters = {'html': _html_formatter}
    column_default_sort = ('search_date', True)

admin.add_view(TwitterSearchAdmin(TwitterSearch, db.session))


class TwitterUserAdmin(sqla.ModelView):
    def _html_formatter(view, context, model, name):
        return Markup('<a href={0}>{0}</a>'.format(model.URL))

    column_formatters = {'URL': _html_formatter}
    column_default_sort = ('Date', True)

admin.add_view(TwitterUserAdmin(TwitterUser, db.session))

if __name__ == '__main__':
    app.run(debug=True)
