-- Crée la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS BDD;

-- Utilise la base de données
USE BDD;

-- Crée la table utilisateurs si elle n'existe pas déjà
CREATE TABLE IF NOT EXISTS utilisateurs (
    utilisateur_id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    clé_publique_rsa TEXT NOT NULL,
    clé_privée_rsa_chiffrée TEXT NOT NULL,
    sel_mot_de_passe TEXT NOT NULL,  -- Utilisé pour renforcer le chiffrement de la clé privée
    mot_de_passe_hash TEXT NOT NULL
);

-- Crée la table discussions si elle n'existe pas déjà
CREATE TABLE IF NOT EXISTS discussions (
    discussion_id SERIAL PRIMARY KEY,
    titre VARCHAR(255),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crée la table participants si elle n'existe pas déjà
CREATE TABLE IF NOT EXISTS participants (
    discussion_id INT,
    utilisateur_id INT,
    PRIMARY KEY (discussion_id, utilisateur_id),
    FOREIGN KEY (discussion_id) REFERENCES discussions(discussion_id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(utilisateur_id)
);

-- Crée la table messages si elle n'existe pas déjà
CREATE TABLE IF NOT EXISTS messages (
    message_id SERIAL PRIMARY KEY,
    discussion_id INT,
    utilisateur_id INT,
    contenu_chiffré BYTEA NOT NULL,
    clé_session_chiffrée BYTEA NOT NULL,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discussion_id) REFERENCES discussions(discussion_id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(utilisateur_id)
);
