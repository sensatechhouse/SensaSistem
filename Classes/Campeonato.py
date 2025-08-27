from DataBase.init_db import DatabaseInitializer

class Gerenciador:
    def __init__(self, game, name):
        name_db = f'{game}-{name}.db'
        db_initializer = DatabaseInitializer(name_db)
        db_initializer.initialize_database()
        db_initializer.close_connection()

class Tournaments:
    def __init__(self):
        pass
