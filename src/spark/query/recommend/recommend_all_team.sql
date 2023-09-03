SELECT champion_name,
        COUNT(match_id) AS `pick_rate`
 FROM combined_filtered_data
 WHERE position = "{my_lane}"
 GROUP BY champion_name
 ORDER BY `pick_rate` DESC
 LIMIT 3
