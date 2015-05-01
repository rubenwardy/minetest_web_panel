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

db.session.add(ServerLogEntry(server, "plain", "Server was backed up", None))
db.session.add(ServerLogEntry(server, "error", "Server Crashed!", """
17:04:28: ACTION[ServerThread]: singleplayer joins game. List of players: singleplayer
zerr: invalid or incomplete deflate data
17:04:28: ERROR[EmergeThread0]: Invalid block data in database (4,0,1) (SerializationError): decompressZlib: inflate failed
17:04:28: ERROR[main]: ServerError: Invalid data in MapBlock (6,2,0)
17:04:28: ERROR[main]: ----
17:04:28: ERROR[main]: "Invalid block data in database"
17:04:28: ERROR[main]: See debug.txt.
17:04:28: ERROR[main]: You can ignore this using [ignore_world_load_errors = true].
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,-2,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,-1,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,0,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,1,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,2,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,0,0): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,0,1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,-2,2): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,-1,3): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (2,0,3): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (3,-2,2): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (4,-2,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (4,-1,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (4,0,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (4,1,-1): SQL logic error or missing database
17:04:29: ERROR[main]: WARNING: saveBlock: Block failed to save (4,2,-1): SQL logic error or missing database
"""))

db.session.commit()
