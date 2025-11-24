-- This script populates the 'teams' and 'games' tables with the initial matchups for a tournament.
-- You MUST first populate the team names below table before running this script.

INSERT INTO teams (name, seed, region)
VALUES
('', 1, 'East'),
('', 2, 'East'),
('', 3, 'East'),
('', 4, 'East'),
('', 5, 'East'),
('', 6, 'East'),
('', 7, 'East'),
('', 8, 'East'),
('', 9, 'East'),
('', 10, 'East'),
('', 11, 'East'),
('', 12, 'East'),
('', 13, 'East'),
('', 14, 'East'),
('', 15, 'East'),
('', 16, 'East'),
('', 1, 'Midwest'),
('', 2, 'Midwest'),
('', 3, 'Midwest'),
('', 4, 'Midwest'),
('', 5, 'Midwest'),
('', 6, 'Midwest'),
('', 7, 'Midwest'),
('', 8, 'Midwest'),
('', 9, 'Midwest'),
('', 10, 'Midwest'),
('', 11, 'Midwest'),
('', 12, 'Midwest'),
('', 13, 'Midwest'),
('', 14, 'Midwest'),
('', 15, 'Midwest'),
('', 16, 'Midwest'),
('', 1, 'South'),
('', 2, 'South'),
('', 3, 'South'),
('', 4, 'South'),
('', 5, 'South'),
('', 6, 'South'),
('', 7, 'South'),
('', 8, 'South'),
('', 9, 'South'),
('', 10, 'South'),
('', 11, 'South'),
('', 12, 'South'),
('', 13, 'South'),
('', 14, 'South'),
('', 15, 'South'),
('', 16, 'South'),
('', 1, 'West'),
('', 2, 'West'),
('', 3, 'West'),
('', 4, 'West'),
('', 5, 'West'),
('', 6, 'West'),
('', 7, 'West'),
('', 8, 'West'),
('', 9, 'West'),
('', 10, 'West'),
('', 11, 'West'),
('', 12, 'West'),
('', 13, 'West'),
('', 14, 'West'),
('', 15, 'West'),
('', 16, 'West');

-- =========================
-- Round 1 (real matchups)
-- =========================
INSERT INTO games (round, round_order, source_game_1, source_game_2, team_1_id, team_2_id, winner_id, region, game_time)
SELECT
    1 AS round,
	CASE t1.seed
		WHEN 1 THEN 1
		WHEN 8 THEN 2
		WHEN 5 THEN 3
		WHEN 4 THEN 4
		WHEN 6 THEN 5
		WHEN 3 THEN 6
		WHEN 7 THEN 7
		WHEN 2 THEN 8
	END AS round_order,
    NULL AS source_game_1,
    NULL AS source_game_2,
    LEAST(t1.team_id, t2.team_id) AS team_1_id,
    GREATEST(t1.team_id, t2.team_id) AS team_2_id,
    NULL AS winner_id,
    t1.region AS region,
    '2025-01-01 12:00:00' AS game_time
FROM teams t1
JOIN teams t2
    ON t1.region = t2.region
   AND t1.seed + t2.seed = 17
   AND t1.seed < t2.seed
ORDER BY 
	t1.region, 
    round_order
       
-- Round 2 (16 games)
INSERT INTO games (round, round_order, source_game_1, source_game_2, team_1_id, team_2_id, winner_id, region, game_time)
SELECT
    2 AS round,
    ((g1.round_order + 1) DIV 2) AS round_order,   -- 1..4
    g1.game_id AS source_game_1,
    g2.game_id AS source_game_2,
    NULL AS team_1_id,
    NULL AS team_2_id,
    NULL AS winner_id,
    g1.region,
    '2025-01-01 12:00:00' AS game_time
FROM games g1
JOIN games g2
  ON g2.region = g1.region
 AND g2.round = 1
 AND g1.round = 1
 AND g2.round_order = g1.round_order + 1
WHERE (g1.round_order % 2) = 1   -- take only the odd round_order rows: 1,3,5,7
ORDER BY g1.region, round_order;

-- Round 3 (8 games)
INSERT INTO games (round, round_order, source_game_1, source_game_2, team_1_id, team_2_id, winner_id, region, game_time)
SELECT
    3 AS round,
    ((g1.round_order + 1) DIV 2) AS round_order,   -- 1..4
    g1.game_id AS source_game_1,
    g2.game_id AS source_game_2,
    NULL AS team_1_id,
    NULL AS team_2_id,
    NULL AS winner_id,
    g1.region,
    '2025-01-01 12:00:00' AS game_time
FROM games g1
JOIN games g2
  ON g2.region = g1.region
 AND g2.round = 2
 AND g1.round = 2
 AND g2.round_order = g1.round_order + 1
WHERE (g1.round_order % 2) = 1   -- take only the odd round_order rows: 1,3,5,7
ORDER BY g1.region, round_order;

-- Round 4 (4 games)
INSERT INTO games (round, round_order, source_game_1, source_game_2, team_1_id, team_2_id, winner_id, region, game_time)
SELECT
    4 AS round,
    ((g1.round_order + 1) DIV 2) AS round_order,   -- 1..4
    g1.game_id AS source_game_1,
    g2.game_id AS source_game_2,
    NULL AS team_1_id,
    NULL AS team_2_id,
    NULL AS winner_id,
    g1.region,
    '2025-01-01 12:00:00' AS game_time
FROM games g1
JOIN games g2
  ON g2.region = g1.region
 AND g2.round = 3
 AND g1.round = 3
 AND g2.round_order = g1.round_order + 1
WHERE (g1.round_order % 2) = 1   -- take only the odd round_order rows: 1,3,5,7
ORDER BY g1.region, round_order;

-- Round 5 (2 games)
INSERT INTO games (round, round_order, source_game_1, source_game_2, team_1_id, team_2_id, winner_id, region, game_time)
WITH pairs AS (
    SELECT
        g1.game_id AS source_game_1,
        g2.game_id AS source_game_2
    FROM games g1
    JOIN games g2
      ON g1.round = g2.round
	WHERE g1.region = 'South' AND g2.region = 'West'
    AND g1.round = 4
)
SELECT
    5 AS round,
    1 AS round_order,
    source_game_1,
    source_game_2,
    NULL AS team_1_id,
    NULL AS team_2_id,
    NULL AS winner_id,
     'Final Four Left',
    '2025-01-01 12:00:00' AS game_time
FROM pairs;

INSERT INTO games (round, round_order, source_game_1, source_game_2, team_1_id, team_2_id, winner_id, region, game_time)
WITH pairs AS (
    SELECT
        g1.game_id AS source_game_1,
        g2.game_id AS source_game_2
    FROM games g1
    JOIN games g2
      ON g1.round = g2.round
	WHERE g1.region = 'East' AND g2.region = 'Midwest'
    AND g1.round = 4
)
SELECT
    5 AS round,
    1 AS round_order,
    source_game_1,
    source_game_2,
    NULL AS team_1_id,
    NULL AS team_2_id,
    NULL AS winner_id,
     'Final Four Right',
    '2025-01-01 12:00:00' AS game_time
FROM pairs;

-- Round 6 (1 game, championship)
INSERT INTO games (round, round_order, source_game_1, source_game_2, team_1_id, team_2_id, winner_id, region, game_time)
WITH pairs AS (
    SELECT
        g1.game_id AS source_game_1,
        g2.game_id AS source_game_2
    FROM games g1
    JOIN games g2
      ON g1.round = g2.round
	WHERE g1.region = 'Final Four Left' AND g2.region = 'Final Four Right'
)
SELECT
    5 AS round,
    1 AS round_order,
    source_game_1,
    source_game_2,
    NULL AS team_1_id,
    NULL AS team_2_id,
    NULL AS winner_id,
     'Championship',
    '2025-01-01 12:00:00' AS game_time
FROM pairs;