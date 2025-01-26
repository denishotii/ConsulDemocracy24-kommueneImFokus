-- This SQL query will give you an overview of all projects, 
-- their proposals, and comments in a specific city. 
SELECT 
    p.id AS project_id,
    p.title AS project_title,
    p.description AS project_description,
    p.proposal_count,
    p.project_url,
    
    pr.id AS proposal_id,
    pr.title AS proposal_title,
    pr.description AS proposal_description,
    pr.supporters,
    pr.proposal_url,
    
    c.id AS comment_id,
    c.text AS comment_text,
    c.user_id AS comment_author,
    c.date AS comment_date,
    c.likes,
    c.dislikes,
    c.total_votes
    
FROM Projects p
LEFT JOIN Proposals pr ON p.id = pr.project_id
LEFT JOIN Comments c ON p.id = c.project_id OR pr.id = c.proposal_id
WHERE p.city_id = (SELECT id FROM Cities WHERE name = 'Pforzheim')
ORDER BY p.id, pr.id, c.date;


-- Find the top 5 projects with the highest number of proposals.
SELECT p.id, p.title, p.proposal_count, c.name AS city_name
FROM Projects p
JOIN Cities c ON p.city_id = c.id
ORDER BY p.proposal_count DESC
LIMIT 5;


-- Find the top 10 proposals with the highest number of supporters.
SELECT pr.id, pr.title, pr.supporters, p.title AS project_title, c.name AS city_name
FROM Proposals pr
JOIN Projects p ON pr.project_id = p.id
JOIN Cities c ON pr.city_id = c.id
ORDER BY pr.supporters DESC
LIMIT 10;

