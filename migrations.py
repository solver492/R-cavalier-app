import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, OperationalError
from app import db, create_app

def run_migrations():
    """
    Exécute les migrations nécessaires pour mettre à jour la base de données
    avec les nouvelles tables et colonnes
    """
    app = create_app()
    
    with app.app_context():
        print("Démarrage des migrations...")
        
        # Liste des migrations à exécuter
        migrations = [
            # Ajout de la colonne stockage_id à la table prestation
            """
            ALTER TABLE prestation 
            ADD COLUMN stockage_id INTEGER REFERENCES stockage(id)
            """,
            
            # Création de la table stockage si elle n'existe pas
            """
            CREATE TABLE IF NOT EXISTS stockage (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES client(id),
                reference VARCHAR(50) UNIQUE NOT NULL,
                date_debut TIMESTAMP NOT NULL DEFAULT NOW(),
                date_fin TIMESTAMP,
                statut VARCHAR(50) DEFAULT 'Actif',
                montant_mensuel FLOAT NOT NULL,
                caution FLOAT,
                emplacement VARCHAR(100) NOT NULL,
                volume_total FLOAT,
                poids_total FLOAT,
                observations TEXT,
                archive BOOLEAN DEFAULT FALSE,
                date_creation TIMESTAMP DEFAULT NOW()
            )
            """,
            
            # Création de la table article_stockage
            """
            CREATE TABLE IF NOT EXISTS article_stockage (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                description TEXT,
                categorie VARCHAR(50),
                dimensions VARCHAR(100),
                volume FLOAT,
                poids FLOAT,
                valeur_declaree FLOAT,
                code_barre VARCHAR(100),
                photo VARCHAR(255),
                fragile BOOLEAN DEFAULT FALSE,
                date_creation TIMESTAMP DEFAULT NOW()
            )
            """,
            
            # Création de la table d'association stockage_article
            """
            CREATE TABLE IF NOT EXISTS stockage_article (
                stockage_id INTEGER REFERENCES stockage(id),
                article_id INTEGER REFERENCES article_stockage(id),
                quantite INTEGER DEFAULT 1,
                PRIMARY KEY (stockage_id, article_id)
            )
            """,
            
            # Ajout de la colonne stockage_id à la table facture
            """
            ALTER TABLE facture 
            ADD COLUMN stockage_id INTEGER REFERENCES stockage(id)
            """
        ]
        
        # Exécution des migrations
        connection = db.engine.connect()
        for migration in migrations:
            try:
                print(f"Exécution de: {migration.strip().split()[0]} ...")
                connection.execute(text(migration))
                connection.commit()
                print("Migration réussie!")
            except (ProgrammingError, OperationalError) as e:
                # Ignorer les erreurs si la colonne existe déjà
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print(f"Information: {str(e)}")
                    connection.commit()  # Réinitialiser la transaction
                else:
                    print(f"Erreur: {str(e)}")
                    connection.rollback()  # Annuler la transaction en cas d'erreur
        
        connection.close()
        print("Migrations terminées!")

if __name__ == "__main__":
    run_migrations()