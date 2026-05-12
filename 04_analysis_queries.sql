-- 04_analysis_queries.sql
-- PURPOSE: Extract cricket insights using SQL
-- Run each query one at a time in MySQL Workbench

USE ipl_analytics;

-- ═══════════════════════════════════════════════════════
-- QUERY 1: TOP 10 RUN SCORERS OF ALL TIME
-- WHY: Most basic but important batting stat
-- INSIGHT: Who has scored the most runs across all IPL seasons
-- ═══════════════════════════════════════════════════════

SELECT
    p.player_name,
    COUNT(DISTINCT d.match_id)                        AS matches,
    SUM(d.batsman_runs)                               AS total_runs,
    SUM(d.is_four)                                    AS fours,
    SUM(d.is_six)                                     AS sixes,
    SUM(d.is_boundary)                                AS boundaries,
    ROUND(SUM(d.batsman_runs) * 100.0 /
          COUNT(d.delivery_id), 2)                    AS strike_rate
FROM deliveries d
JOIN players p ON d.batter_id = p.player_id
GROUP BY p.player_id, p.player_name
ORDER BY total_runs DESC
LIMIT 10;


-- ═══════════════════════════════════════════════════════
-- QUERY 2: TOP 10 WICKET TAKERS OF ALL TIME
-- WHY: Key bowling stat
-- NOTE: We exclude run outs because bowler gets no credit
-- ═══════════════════════════════════════════════════════

SELECT
    p.player_name,
    COUNT(DISTINCT d.match_id)                        AS matches,
    ROUND(COUNT(d.delivery_id) / 6.0, 1)             AS overs_bowled,
    SUM(d.total_runs)                                 AS runs_given,
    SUM(d.is_wicket)                                  AS wickets,
    ROUND(SUM(d.total_runs) * 6.0 /
          COUNT(d.delivery_id), 2)                    AS economy_rate,
    ROUND(SUM(d.total_runs) * 1.0 /
          NULLIF(SUM(d.is_wicket), 0), 2)             AS bowling_average
FROM deliveries d
JOIN players p ON d.bowler_id = p.player_id
WHERE d.dismissal_kind NOT IN ('run out', 'not_out')
   OR d.dismissal_kind = 'not_out'
GROUP BY p.player_id, p.player_name
HAVING wickets >= 50
ORDER BY wickets DESC
LIMIT 10;


-- ═══════════════════════════════════════════════════════
-- QUERY 3: PHASE-WISE RUN RATE ANALYSIS
-- WHY: Shows how scoring patterns change across the innings
-- INSIGHT: Death overs have highest run rate but also most wickets
-- ═══════════════════════════════════════════════════════

SELECT
    phase,
    COUNT(delivery_id)                                AS total_balls,
    ROUND(COUNT(delivery_id) / 6.0, 0)               AS total_overs,
    SUM(total_runs)                                   AS total_runs,
    SUM(is_wicket)                                    AS total_wickets,
    SUM(is_six)                                       AS total_sixes,
    SUM(is_four)                                      AS total_fours,
    ROUND(SUM(total_runs) * 6.0 /
          COUNT(delivery_id), 2)                      AS run_rate,
    ROUND(SUM(is_wicket) * 6.0 /
          COUNT(delivery_id), 3)                      AS wickets_per_over
FROM deliveries
GROUP BY phase
ORDER BY FIELD(phase, 'Powerplay', 'Middle', 'Death');


-- ═══════════════════════════════════════════════════════
-- QUERY 4: TOSS IMPACT - DOES WINNING TOSS HELP?
-- WHY: Classic cricket debate - answered with data
-- INSIGHT: Does batting or fielding first win more matches?
-- ═══════════════════════════════════════════════════════

SELECT
    toss_decision,
    COUNT(*)                                          AS total_matches,
    SUM(CASE WHEN toss_winner = winner
             THEN 1 ELSE 0 END)                       AS toss_winner_won,
    ROUND(SUM(CASE WHEN toss_winner = winner
                   THEN 1 ELSE 0 END) * 100.0
          / COUNT(*), 1)                              AS win_percentage
FROM matches
WHERE winner != 'No Result'
GROUP BY toss_decision;


-- ═══════════════════════════════════════════════════════
-- QUERY 5: DEATH OVER SPECIALISTS (BATTERS)
-- WHY: Finishers are the most valuable T20 players
-- INSIGHT: Who performs best in overs 16-20 under pressure
-- ═══════════════════════════════════════════════════════

SELECT
    p.player_name,
    SUM(d.batsman_runs)                               AS death_runs,
    COUNT(d.delivery_id)                              AS death_balls,
    SUM(d.is_six)                                     AS sixes,
    ROUND(SUM(d.batsman_runs) * 100.0 /
          COUNT(d.delivery_id), 2)                    AS death_strike_rate
FROM deliveries d
JOIN players p ON d.batter_id = p.player_id
WHERE d.phase = 'Death'
GROUP BY p.player_id, p.player_name
HAVING death_balls >= 100
ORDER BY death_strike_rate DESC
LIMIT 10;


-- ═══════════════════════════════════════════════════════
-- QUERY 6: BEST POWERPLAY BOWLERS
-- WHY: Powerplay wickets change the game completely
-- INSIGHT: Who is most dangerous in the first 6 overs
-- ═══════════════════════════════════════════════════════

SELECT
    p.player_name,
    COUNT(d.delivery_id)                              AS pp_balls,
    SUM(d.total_runs)                                 AS pp_runs,
    SUM(d.is_wicket)                                  AS pp_wickets,
    ROUND(SUM(d.total_runs) * 6.0 /
          COUNT(d.delivery_id), 2)                    AS pp_economy
FROM deliveries d
JOIN players p ON d.bowler_id = p.player_id
WHERE d.phase = 'Powerplay'
GROUP BY p.player_id, p.player_name
HAVING pp_balls >= 120
ORDER BY pp_wickets DESC
LIMIT 10;


-- ═══════════════════════════════════════════════════════
-- QUERY 7: SEASON-WISE BATTING TRENDS
-- WHY: Shows how T20 cricket has evolved over the years
-- INSIGHT: Has run scoring increased every season?
-- ═══════════════════════════════════════════════════════

SELECT
    m.season,
    COUNT(DISTINCT m.match_id)                        AS matches,
    SUM(d.batsman_runs)                               AS total_runs,
    SUM(d.is_six)                                     AS total_sixes,
    SUM(d.is_four)                                    AS total_fours,
    ROUND(SUM(d.total_runs) * 6.0 /
          COUNT(d.delivery_id), 2)                    AS avg_run_rate
FROM deliveries d
JOIN matches m ON d.match_id = m.match_id
GROUP BY m.season
ORDER BY m.season;


-- ═══════════════════════════════════════════════════════
-- QUERY 8: TOP VENUES BY AVERAGE FIRST INNINGS SCORE
-- WHY: Venue heavily influences match strategy
-- INSIGHT: Which stadiums favour batters vs bowlers
-- ═══════════════════════════════════════════════════════

SELECT
    v.venue_name,
    COUNT(DISTINCT d.match_id)                        AS matches_hosted,
    ROUND(AVG(innings_total), 0)                      AS avg_first_innings_score,
    MAX(innings_total)                                AS highest_score,
    MIN(innings_total)                                AS lowest_score
FROM (
    SELECT match_id, SUM(total_runs) AS innings_total
    FROM deliveries
    WHERE inning = 1
    GROUP BY match_id
) AS first_innings
JOIN deliveries d  ON d.match_id    = first_innings.match_id
JOIN matches m     ON m.match_id    = d.match_id
JOIN venues v      ON v.venue_id    = m.venue_id
GROUP BY v.venue_id, v.venue_name
HAVING matches_hosted >= 5
ORDER BY avg_first_innings_score DESC
LIMIT 10;


-- ═══════════════════════════════════════════════════════
-- QUERY 9: MOST DANGEROUS BATTING PAIRS (PARTNERSHIPS)
-- WHY: Partnership analysis is advanced and impressive
-- INSIGHT: Which two batters score fastest together
-- ═══════════════════════════════════════════════════════

SELECT
    p1.player_name                                    AS batter,
    p2.player_name                                    AS non_striker,
    COUNT(DISTINCT d.match_id)                        AS matches_together,
    SUM(d.batsman_runs)                               AS runs_together,
    COUNT(d.delivery_id)                              AS balls_together,
    ROUND(SUM(d.batsman_runs) * 100.0 /
          COUNT(d.delivery_id), 2)                    AS partnership_sr
FROM deliveries d
JOIN players p1 ON d.batter_id    = p1.player_id
JOIN players p2 ON d.bowler_id    = p2.player_id
GROUP BY p1.player_id, p1.player_name,
         p2.player_id, p2.player_name
HAVING matches_together >= 10
ORDER BY runs_together DESC
LIMIT 10;


-- ═══════════════════════════════════════════════════════
-- QUERY 10: DISMISSAL TYPE BREAKDOWN
-- WHY: Shows what gets batsmen out most in T20
-- INSIGHT: Is caught the most common? What about run outs?
-- ═══════════════════════════════════════════════════════

SELECT
    dismissal_kind,
    COUNT(*)                                          AS total_dismissals,
    ROUND(COUNT(*) * 100.0 /
          SUM(COUNT(*)) OVER(), 1)                    AS percentage
FROM deliveries
WHERE dismissal_kind != 'not_out'
GROUP BY dismissal_kind
ORDER BY total_dismissals DESC;