SELECT champion_name,
        AVG(win) * 100 AS `win_rate`,
        COUNT(match_id) AS `pick_rate`
 FROM opponent_lane_filtered_data
 WHERE position = "{my_lane}"
 GROUP BY champion_name
 ORDER BY `pick_rate` DESC
 LIMIT 3