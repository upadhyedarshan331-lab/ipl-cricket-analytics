-- 02_database_setup.sql
-- PURPOSE: Create IPL analytics database with all 4 tables

-- Create database
CREATE DATABASE IF NOT EXISTS ipl_analytics;
USE ipl_analytics;

-- ── TABLE 1: venues ────────────────────────────────────────────────────────
-- Stores unique stadium names
-- WHY separate table: avoid repeating "Wankhede Stadium" in every match row

CREATE TABLE IF NOT EXISTS venues (
    venue_id   INT AUTO_INCREMENT PRIMARY KEY,
    venue_name VARCHAR(150) NOT NULL UNIQUE
);

-- ── TABLE 2: matches ───────────────────────────────────────────────────────
-- One row per match (1,095 rows will go here)

CREATE TABLE IF NOT EXISTS matches (
    match_id        INT PRIMARY KEY,
    season          INT,
    match_date      DATE,
    city            VARCHAR(100),
    venue_id        INT,
    team1           VARCHAR(100),
    team2           VARCHAR(100),
    toss_winner     VARCHAR(100),
    toss_decision   VARCHAR(10),
    winner          VARCHAR(100),
    result          VARCHAR(50),
    result_margin   FLOAT,
    player_of_match VARCHAR(100),
    method          VARCHAR(50),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);

-- ── TABLE 3: players ───────────────────────────────────────────────────────
-- Every unique player name across all deliveries
-- WHY: Avoids storing full names in every delivery row

CREATE TABLE IF NOT EXISTS players (
    player_id   INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL UNIQUE
);

-- ── TABLE 4: deliveries ────────────────────────────────────────────────────
-- Main fact table - one row per ball bowled (260,920 rows will go here)

CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id         INT AUTO_INCREMENT PRIMARY KEY,
    match_id            INT NOT NULL,
    inning              TINYINT,
    batting_team        VARCHAR(100),
    bowling_team        VARCHAR(100),
    over_num            TINYINT,
    ball_num            TINYINT,
    batter_id           INT,
    bowler_id           INT,
    batsman_runs        TINYINT DEFAULT 0,
    extra_runs          TINYINT DEFAULT 0,
    total_runs          TINYINT DEFAULT 0,
    extras_type         VARCHAR(20),
    is_wicket           TINYINT(1) DEFAULT 0,
    dismissal_kind      VARCHAR(50) DEFAULT 'not_out',
    player_dismissed_id INT,
    phase               VARCHAR(15),
    is_four             TINYINT(1) DEFAULT 0,
    is_six              TINYINT(1) DEFAULT 0,
    is_boundary         TINYINT(1) DEFAULT 0,
    FOREIGN KEY (match_id)  REFERENCES matches(match_id),
    FOREIGN KEY (batter_id) REFERENCES players(player_id),
    FOREIGN KEY (bowler_id) REFERENCES players(player_id)
);

-- ── INDEXES ────────────────────────────────────────────────────────────────
-- WHY: Speeds up queries on large tables dramatically

CREATE INDEX idx_del_match  ON deliveries(match_id);
CREATE INDEX idx_del_batter ON deliveries(batter_id);
CREATE INDEX idx_del_bowler ON deliveries(bowler_id);
CREATE INDEX idx_match_season ON matches(season);

-- Confirm tables created
SHOW TABLES;