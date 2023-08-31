    WITH match_conditions AS (
      SELECT match_id,
             team_id,
             SUM(CASE WHEN position = 'TOP' AND champion_name = "{top_champ}" THEN 1 ELSE 0 END) AS top_count,
             SUM(CASE WHEN position = 'JUNGLE' AND champion_name = "{jungle_champ}" THEN 1 ELSE 0 END) AS jungle_count,
             SUM(CASE WHEN position = 'MIDDLE' AND champion_name = "{middle_champ}" THEN 1 ELSE 0 END) AS middle_count,
             SUM(CASE WHEN position = 'BOTTOM' AND champion_name = "{bottom_champ}" THEN 1 ELSE 0 END) AS bottom_count,
             SUM(CASE WHEN position = 'UTILITY' AND champion_name = "{utility_champ}" THEN 1 ELSE 0 END) AS utility_count
      FROM games
      GROUP BY match_id, team_id
    )
    SELECT match_id, team_id
    FROM match_conditions
    WHERE top_count {top_operator} 0 AND jungle_count {jungle_operator} 0 AND middle_count {middle_operator} 0 AND bottom_count {bottom_operator} 0 AND utility_count {utility_operator} 0