from web_panel.models import db, User, Server, ServerLogEntry
import os

if os.path.isfile("web_panel/data.sqlite"):
	os.remove("web_panel/data.sqlite")

db.create_all()

user = User("admin", "pass")
user.is_admin = True
db.session.add(user)

server = Server("Server 1", "servertest")
db.session.add(server)
db.session.commit()

print("Database created.")
