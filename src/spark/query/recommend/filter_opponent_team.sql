    SELECT games.*
    FROM games
    JOIN opponent_matching_games
    ON games.match_id = opponent_matching_games.match_id AND games.team_id != opponent_matching_games.opponent_team_id