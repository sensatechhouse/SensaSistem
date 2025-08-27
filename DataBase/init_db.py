import sqlite3
from datetime import datetime

class DatabaseInitializer:
    def __init__(self, db_name='cs_tournaments.db'):
        self.db_name = fr'DataBase/bases/{db_name}'
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
                    'players', 'teams', 'player_team', 
                    'tournaments', 'tournament_teams', 'matches'
                )
            """)
            tables = cursor.fetchall()
            
            # Se não encontrar todas as tabelas, considera vazio
            return len(tables) < 6
            
        except sqlite3.Error as e:
            print(f"Erro ao verificar se o banco está vazio: {e}")
            return True
    
    def create_tables(self):
        """Cria todas as tabelas necessárias (sem administradores)"""
        try:
            cursor = self.conn.cursor()
            
            # Tabela de Jogadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nickname VARCHAR(50) UNIQUE NOT NULL,
                    steam_id VARCHAR(20) UNIQUE,
                    email VARCHAR(100),
                    country VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
    
    def show_table_counts(self):
        """Mostra a quantidade de registros em cada tabela"""
        try:
            cursor = self.conn.cursor()
            tables = [
                'players', 'teams', 'player_team',
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
            if self.create_tables():
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
        print("✅ Todas as tabelas foram criadas com sucesso!")
        print("✅ Banco de dados vazio, aguardando inserção de dados.")
    else:
        print("\n❌ Falha na inicialização do sistema!")

if __name__ == "__main__":
    main()