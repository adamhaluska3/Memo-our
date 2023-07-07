import os

from flask import Flask, redirect


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='ambatukam',
        DATABASE=os.path.join(app.instance_path, 'memo-our.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/')
    def index():
        return redirect('auth/login')

    return app
