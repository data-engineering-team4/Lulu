SELECT champion_name,
       AVG(win) * 100 AS `Win Rate`,
       COUNT(match_id) AS `Total Games`
FROM our_filtered_data
WHERE position = "{my_lane}"
GROUP BY champion_name
ORDER BY `Win Rate` DESC