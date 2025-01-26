-- Create the database and tables for the CitizenParticipation project

CREATE DATABASE CitizenParticipation
    DEFAULT CHARACTER SET = 'utf8mb4';
USE CitizenParticipation;

-- Table for storing cities
CREATE TABLE Cities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

-- Table for storing projects
CREATE TABLE Projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    city_id INT,
    proposal_count INT DEFAULT 0,
    project_url TEXT,
    FOREIGN KEY (city_id) REFERENCES Cities(id)
);

-- Table for storing users
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    verified_status ENUM('verified', 'not verified') DEFAULT 'not verified'
);

-- Table for storing proposals
CREATE TABLE Proposals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    project_id INT,
    author_id INT,
    city_id INT,
    supporters INT DEFAULT 0,
    proposal_url TEXT,
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES Users(id) ON DELETE SET NULL
    FOREIGN KEY (city_id) REFERENCES Cities(id) ON DELETE CASCADE
);

-- Table for storing comments on projects and proposals
CREATE TABLE Comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    user_id INT,
    project_id INT NULL,
    proposal_id INT NULL,
    date DATETIME NOT NULL,
    likes INT DEFAULT 0,
    dislikes INT DEFAULT 0,
    total_votes INT GENERATED ALWAYS AS (likes - dislikes) STORED,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (proposal_id) REFERENCES Proposals(id) ON DELETE CASCADE
);
