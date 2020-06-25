-- PITCHERS MOST OFTEN PLAYED AGAINST	
WITH mytable AS (
SELECT p.nameKey, COUNT(*) AS count_
FROM pitching_gamelogs p
INNER JOIN (
			SELECT gameKey, team
			FROM batting_gamelogs 
			WHERE nameKey = 'suzukic01'
			) ap
ON p.gameKey = ap.gameKey
AND p.team != ap.team
GROUP BY p.nameKey
ORDER BY count_ DESC
LIMIT 50)
SELECT m.name, mt.*
FROM mytable mt
INNER JOIN ( 
			SELECT DISTINCT name, nameKey
			FROM meta
			) m
ON mt.nameKey = m.nameKey
ORDER BY mt.count_ DESC

-- BATTERS MOST OFTEN PLAYED AGAINST	
WITH mytable AS (
SELECT p.nameKey, COUNT(*) AS count_
FROM batting_gamelogs p
INNER JOIN (
			SELECT gameKey, team
			FROM pitching_gamelogs 
			WHERE nameKey = 'sabatc.01'
			) ap
ON p.gameKey = ap.gameKey
AND p.team != ap.team
GROUP BY p.nameKey
ORDER BY count_ DESC
LIMIT 50)
SELECT m.name, mt.*
FROM mytable mt
INNER JOIN ( 
			SELECT DISTINCT name, nameKey
			FROM meta
			) m
ON mt.nameKey = m.nameKey
ORDER BY mt.count_ DESC


SELECT m.name, b.nameKey, COUNT(*) AS count_
FROM pitching_gamelogs b
INNER JOIN (
			SELECT nameKey 
			FROM pitching_gamelogs
			WHERE gcar = 1
			) SQ
ON b.nameKey = SQ.nameKey
INNER JOIN meta m
ON b.nameKey = m.nameKey
AND b.year = m.year
AND b.team = m.team
GROUP BY b.nameKey
ORDER BY count_ DESC

SELECT DISTINCT nameKey
FROM meta
WHERE name = 'Clayton Kershaw'