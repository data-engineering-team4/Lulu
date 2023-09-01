    SELECT games.*
    FROM games
    JOIN opponent_lane_matching_games
    ON games.match_id = opponent_lane_matching_games.match_id AND games.team_id != opponent_lane_matching_games.opponent_team_id