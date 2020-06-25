
-- SUM OF HOMERUNS PER PARK, PER YEAR
SELECT p.venue, p.year, p.homeTeam, SUM(b.hr) AS sumHomeRuns
FROM "gamelogs.schedules" p
INNER JOIN "gamelogs.batting" b
ON p.gameKey = b.gameKey
GROUP BY p.venue, p.year, p.homeTeam
ORDER BY sumHomeRuns DESC


-- AVG OF HR, HITS, SINGLES, DOUBLES, TRIPLES AND BB PER PARK FOR 2014
WITH mytable AS(
SELECT p.venue, p.gameKey, SUM(b.r) AS Runs, SUM(b.hr) AS HomeRuns, SUM(b.h) AS Hits, SUM(b.double) AS Doubles, SUM(b.triple) AS Triples, SUM(b.bb) AS BBs
FROM "gamelogs.schedules" p
INNER JOIN "gamelogs.batting" b
ON p.gameKey = b.gameKey
WHERE p.year = 2014
GROUP BY p.venue, p.gameKey
)
SELECT venue,  AVG(Runs), AVG(HomeRuns), AVG(Hits), AVG(Doubles), AVG(Triples), AVG(BBs)
FROM mytable
GROUP BY venue
ORDER BY AVG(Runs) DESC

--SUM OF RUNS, HOMERUNS, HITS, DOUBLES, TRIPLES AND BB FOR COORS FIELD DURING 2014
SELECT p.venue, p.gameKey, SUM(b.r) AS Runs, SUM(b.hr) AS HomeRuns, SUM(b.h) AS Hits, SUM(b.double) AS Doubles, SUM(b.triple) AS Triples, SUM(b.bb) AS BBs
FROM "gamelogs.schedules" p
INNER JOIN "gamelogs.batting" b
ON p.gameKey = b.gameKey
WHERE p.year = 2014
AND p.venue = 'Coors Field'
GROUP BY p.venue, p.gameKey


--ESPN PARK FACTOR

SELECT home.team, homeRS, homeRA, roadRS, roadRA, home.g AS homeG, road.g AS roadG, ((homeRS + homeRA)/home.g) / ((roadRS + roadRA)/road.g)  AS parkFactor
FROM ( 
SELECT st.team AS team, CAST(SUM(g1.homeTeamScore) AS REAL) AS homeRS, CAST(SUM(g1.awayTeamScore) AS REAL) AS homeRA, CAST(COUNT(*) AS REAL) AS g
FROM (SELECT DISTINCT team, gameKey FROM "gamelogs.batting" WHERE year = 2014) st
INNER JOIN "gamelogs.schedules" g1
ON st.team = g1.homeTeamAbbr
AND st.gameKey = g1.gameKey
GROUP BY st.team
) home
INNER JOIN (
SELECT st.team AS team, CAST(SUM(g2.awayTeamScore) AS REAL) AS roadRS, CAST(SUM(g2.homeTeamScore) AS REAL) AS roadRA, CAST(COUNT(*) AS REAL) AS g
FROM (SELECT DISTINCT team, gameKey FROM "gamelogs.batting" WHERE year = 2014) st
INNER JOIN "gamelogs.schedules" g2
ON st.team = g2.awayTeamAbbr
AND st.gameKey = g2.gameKey
GROUP BY st.team
) road
ON home.team = road.team





