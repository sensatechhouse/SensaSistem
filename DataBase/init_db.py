import sqlite3
import bcrypt
from datetime import datetime, date

class DatabaseInitializer:
    def __init__(self, db_name='cs_tournaments.db'):
        self.db_name = db_name
        self.conn = None
        
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.execute("PRAGMA foreign_keys = ON")  # Ativar chaves estrangeiras
            print(f"Conexão com {self.db_name} estabelecida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao conectar com o banco de dados: {e}")
            return False
    
    def is_database_empty(self):
        """Verifica se o banco de dados está vazio"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar se as tabelas existem
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    'administrators', 'players', 'teams', 'player_team', 
                    'tournaments', 'tournament_teams', 'matches'
                )
            """)
            tables = cursor.fetchall()
            
            # Se não encontrar todas as tabelas, considera vazio
            if len(tables) < 7:
                return True
                
            # Verificar se há dados nas tabelas principais
            cursor.execute("SELECT COUNT(*) FROM administrators")
            admin_count = cursor.fetchone()[0]
            
            return admin_count == 0
            
        except sqlite3.Error as e:
            print(f"Erro ao verificar se o banco está vazio: {e}")
            return True
    
    def create_tables(self):
        """Cria todas as tabelas necessárias"""
        try:
            cursor = self.conn.cursor()
            
            # Tabela de Administradores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS administrators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabela de Jogadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nickname VARCHAR(50) UNIQUE NOT NULL,
                    steam_id VARCHAR(20) UNIQUE,
                    email VARCHAR(100),
                    country VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER REFERENCES administrators(id)
                )
            ''')
            
            # Tabela de Equipes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    tag VARCHAR(10) UNIQUE NOT NULL,
                    country VARCHAR(50),
                    founded_date DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER REFERENCES administrators(id)
                )
            ''')
            
            # Tabela de Relação Jogadores-Equipes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_team (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
                    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
                    join_date DATE DEFAULT CURRENT_DATE,
                    leave_date DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(player_id, team_id)
                )
            ''')
            
            # Tabela de Campeonatos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tournaments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    start_date DATE,
                    end_date DATE,
                    prize_pool DECIMAL(15,2),
                    location VARCHAR(100),
                    game_version VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'PLANNED',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER REFERENCES administrators(id)
                )
            ''')
            
            # Tabela de Times no Campeonato
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tournament_teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tournament_id INTEGER REFERENCES tournaments(id) ON DELETE CASCADE,
                    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
                    seed INTEGER,
                    group_name VARCHAR(50),
                    UNIQUE(tournament_id, team_id)
                )
            ''')
            
            # Tabela de Partidas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tournament_id INTEGER REFERENCES tournaments(id),
                    team1_id INTEGER REFERENCES teams(id),
                    team2_id INTEGER REFERENCES teams(id),
                    match_date DATETIME,
                    map VARCHAR(50),
                    score_team1 INTEGER DEFAULT 0,
                    score_team2 INTEGER DEFAULT 0,
                    winner_id INTEGER REFERENCES teams(id),
                    status VARCHAR(20) DEFAULT 'SCHEDULED',
                    round VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Criar índices para melhor performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_team_player ON player_team(player_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_team_team ON player_team(team_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tournament_teams_tournament ON tournament_teams(tournament_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tournament_teams_team ON tournament_teams(team_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_tournament ON matches(tournament_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_team1 ON matches(team1_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_team2 ON matches(team2_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_winner ON matches(winner_id)')
            
            self.conn.commit()
            print("Tabelas criadas com sucesso!")
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False
    
    def hash_password(self, password):
        """Gera hash da senha usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def insert_sample_data(self):
        """Insere dados de exemplo no banco"""
        try:
            cursor = self.conn.cursor()
            
            # Inserir administradores
            admin_passwords = {
                'admin': self.hash_password('admin123'),
                'manager': self.hash_password('manager123')
            }
            
            cursor.executemany('''
                INSERT INTO administrators (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', [
                ('admin', 'admin@cs-tournaments.com', admin_passwords['admin']),
                ('manager', 'manager@cs-tournaments.com', admin_passwords['manager'])
            ])
            
            # Inserir jogadores
            cursor.executemany('''
                INSERT INTO players (nickname, steam_id, email, country, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', [
                ('coldzera', 'STEAM_1:1:123456', 'coldzera@email.com', 'Brazil', 1),
                ('s1mple', 'STEAM_1:1:654321', 's1mple@email.com', 'Ukraine', 1),
                ('device', 'STEAM_1:1:789012', 'device@email.com', 'Denmark', 1),
                ('ZywOo', 'STEAM_1:1:345678', 'zywoo@email.com', 'France', 1),
                ('NiKo', 'STEAM_1:1:901234', 'niko@email.com', 'Bosnia', 2)
            ])
            
            # Inserir equipes
            cursor.executemany('''
                INSERT INTO teams (name, tag, country, founded_date, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', [
                ('Natus Vincere', 'NaVi', 'Ukraine', '2009-12-17', 1),
                ('FaZe Clan', 'FaZe', 'International', '2010-05-30', 1),
                ('Team Vitality', 'VIT', 'France', '2013-08-27', 2),
                ('Astralis', 'AST', 'Denmark', '2016-01-18', 2)
            ])
            
            # Inserir relações jogador-equipe
            cursor.executemany('''
                INSERT INTO player_team (player_id, team_id, join_date)
                VALUES (?, ?, ?)
            ''', [
                (2, 1, '2020-01-01'),  # s1mple in NaVi
                (3, 4, '2021-01-01'),  # device in Astralis
                (4, 3, '2020-06-01'),  # ZywOo in Vitality
                (5, 2, '2022-01-01')   # NiKo in FaZe
            ])
            
            # Inserir campeonatos
            cursor.executemany('''
                INSERT INTO tournaments (name, description, start_date, end_date, 
                                       prize_pool, location, game_version, status, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                ('ESL Pro League Season 16', 'Major CS:GO tournament in Malta', 
                 '2023-08-30', '2023-10-02', 1000000.00, 'Malta', 'CS:GO', 'COMPLETED', 1),
                ('IEM Katowice 2023', 'One of the most prestigious CS:GO tournaments', 
                 '2023-02-01', '2023-02-12', 1000000.00, 'Katowice, Poland', 'CS:GO', 'COMPLETED', 1),
                ('BLAST Premier World Final 2023', 'World Final championship', 
                 '2023-12-13', '2023-12-17', 1000000.00, 'Abu Dhabi', 'CS:GO', 'PLANNED', 2)
            ])
            
            # Inserir times nos campeonatos
            cursor.executemany('''
                INSERT INTO tournament_teams (tournament_id, team_id, seed, group_name)
                VALUES (?, ?, ?, ?)
            ''', [
                (1, 1, 1, 'A'), (1, 2, 2, 'A'), (1, 3, 1, 'B'), (1, 4, 2, 'B'),
                (2, 1, 1, 'A'), (2, 2, 2, 'B'), (3, 1, 1, 'A'), (3, 3, 2, 'A')
            ])
            
            # Inserir partidas
            cursor.executemany('''
                INSERT INTO matches (tournament_id, team1_id, team2_id, match_date, 
                                   map, score_team1, score_team2, winner_id, status, round)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                (1, 1, 2, '2023-09-01 15:00:00', 'Mirage', 16, 12, 1, 'COMPLETED', 'Group Stage'),
                (1, 3, 4, '2023-09-01 18:00:00', 'Inferno', 10, 16, 4, 'COMPLETED', 'Group Stage'),
                (1, 1, 4, '2023-09-02 15:00:00', 'Nuke', 16, 14, 1, 'COMPLETED', 'Semi-final'),
                (2, 1, 2, '2023-02-05 16:00:00', 'Ancient', 19, 17, 1, 'COMPLETED', 'Grand Final')
            ])
            
            self.conn.commit()
            print("Dados de exemplo inseridos com sucesso!")
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao inserir dados de exemplo: {e}")
            self.conn.rollback()
            return False
    
    def show_table_counts(self):
        """Mostra a quantidade de registros em cada tabela"""
        try:
            cursor = self.conn.cursor()
            tables = [
                'administrators', 'players', 'teams', 'player_team',
                'tournaments', 'tournament_teams', 'matches'
            ]
            
            print("\n=== CONTAGEM DE REGISTROS POR TABELA ===")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} registros")
                
        except sqlite3.Error as e:
            print(f"Erro ao contar registros: {e}")
    
    def initialize_database(self):
        """Método principal para inicializar o banco de dados"""
        if not self.connect():
            return False
        
        if self.is_database_empty():
            print("Banco de dados vazio. Iniciando inicialização...")
            if self.create_tables() and self.insert_sample_data():
                print("Banco de dados inicializado com sucesso!")
                self.show_table_counts()
                return True
            else:
                print("Falha na inicialização do banco de dados!")
                return False
        else:
            print("Banco de dados já contém dados. Nenhuma ação necessária.")
            self.show_table_counts()
            return True
    
    def close_connection(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada.")

# Função principal
def main():
    # Instanciar o inicializador
    db_initializer = DatabaseInitializer()
    
    # Inicializar o banco de dados
    success = db_initializer.initialize_database()
    
    # Fechar conexão
    db_initializer.close_connection()
    
    if success:
        print("\n✅ Sistema pronto para uso!")
        print("Credenciais de acesso:")
        print("Usuário: admin | Senha: admin123")
        print("Usuário: manager | Senha: manager123")
    else:
        print("\n❌ Falha na inicialização do sistema!")

if __name__ == "__main__":
    main()