SELECT f.*
FROM our_filtered_data f
JOIN opponent_filtered_data o
ON f.match_id = o.match_id AND f.team_id = o.team_id;
