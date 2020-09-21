class DBSession:
    tasks = {}
    def __init__(self):
        self.tasks = DBSession.tasks
        
def get_db():
    return DBSession()