SELECT 
    house_divisions.debate_id,
    main_mp.house_division_id,
    COALESCE(num_utterances.num_utterances, 0) AS 'num_utterances',
    CASE WHEN main_mp.is_vote_aye = 1 THEN 'aye' ELSE 'no' END AS 'The MP voted:',
    SUM(CASE WHEN other_mps.is_vote_aye = 1 THEN 1 ELSE 0 END) AS '# fellow MPs voting aye:',
    SUM(CASE WHEN other_mps.is_vote_aye = 0 THEN 1 ELSE 0 END) AS '# fellow MPs voting no:',
    CASE WHEN SUM(main_mp.is_vote_aye != other_mps.is_vote_aye) > SUM(main_mp.is_vote_aye = other_mps.is_vote_aye) THEN 'AGAINST' ELSE 'WITH ' END AS 'Were they in the majority:'
FROM
    (SELECT 
        mp.mp_id,
        mp.party,
        votes.house_division_id,
        votes.is_vote_aye
     FROM
        votes
     LEFT JOIN
         mp
     USING(mp_id)
     WHERE votes.mp_id = "?" AND mp.term_start == 2017) main_mp
LEFT OUTER JOIN
    (SELECT
        votes.house_division_id,
        votes.is_vote_aye,
        mp.party
     FROM
        votes
     LEFT JOIN
        mp
     ON
        votes.mp_id = mp.mp_id
     WHERE votes.mp_id != "?" AND mp.term_start == 2017) other_mps
     ON
        main_mp.house_division_id = other_mps.house_division_id AND
        main_mp.party = other_mps.party
LEFT JOIN
      house_divisions
USING (house_division_id)
LEFT JOIN
   (SELECT
      speeches.speaker_id AS mp_id,
      debate_id,
      COUNT(*) AS 'num_utterances'
    FROM
      speeches
    GROUP BY
      speeches.speaker_id,
      speeches.debate_id  
      ) num_utterances
ON house_divisions.debate_id = num_utterances.debate_id AND main_mp.mp_id = num_utterances.mp_id
GROUP BY
   main_mp.is_vote_aye,
   house_divisions.debate_id,
   main_mp.house_division_id
ORDER BY
   house_divisions.debate_id ASC