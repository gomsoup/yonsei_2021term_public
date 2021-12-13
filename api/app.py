import os
from flask import Flask, render_template
from flask.helpers import make_response
from flask.json import jsonify
from flask_restx import Api, Resource
from resources.ErrorHandler import error_handle

from controller.communicate import communicator
from model.db import db

app = Flask(__name__)
app.debug = True

api = Api(app)
api.add_namespace(communicator, '/communicate')

@api.route('/online')
class main(Resource):
    def get(self):
        return jsonify({"ret" : "Success"})

if app.debug:
    @api.route('/test_upload')
    class main(Resource):
        def get(self):
            headers = {'Content-Type' : 'text/html'}
            return make_response(render_template('upload.html') , 200, headers)

    @api.route('/test_notify')
    class main(Resource):
        def get(self):
            headers = {'Content-Type' : 'text/html'}
            return make_response(render_template('notify.html'), 200, headers)

    @api.route('/test_app_notify')
    class main(Resource):
        def get(self):
            headers = {'Content-Type' : 'text/html'}
            return make_response(render_template('app_notify.html'), 200, headers)

def init():
    basedir = os.path.abspath(os.path.dirname(__file__)) 
    db_file = os.path.join(basedir + '/resources/db', 'db.sqlite')
    print (db_file)
    upload_file = os.path.join(basedir, 'userdata/image')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SECRET_KEY'] = 'abcdefg'
    app.config['UPLOAD_FOLDER '] = upload_file

    #__tablename__ = 'image'

    db.init_app(app)
    db.app = app
    db.create_all()
    error_handle(app)

if __name__ == "__main__":
    init()
    app.run(host = '0.0.0.0', port = 9949)
