    WITH match_conditions AS (
      SELECT match_id,
             team_id,
             SUM(CASE WHEN position = "{my_lane}" AND champion_name = "{champ}" THEN 1 ELSE 0 END) AS my_lane_count
      FROM games
      GROUP BY match_id, team_id
    )
      SELECT match_id, team_id AS opponent_team_id
      FROM match_conditions
      WHERE my_lane_count > 0