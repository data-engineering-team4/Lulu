    SELECT games.*
    FROM games
    JOIN our_matching_games
    ON games.match_id = our_matching_games.match_id AND games.team_id = our_matching_games.team_id