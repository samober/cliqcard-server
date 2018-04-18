import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from cliqcard_server.app import create_app
from cliqcard_server.models import db

app = create_app(config_name=os.getenv('CLIQCARD_SERVER_MODE', 'development'))
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()