SELECT cs_id, ROUND(avg(score)) AS Bld_Ensemble_Average_Score
FROM "Building_Model_Score"
GROUP BY cs_id;

SELECT cs_id, avg(score) AS Bld_Ensemble_Average_Score
FROM "Building_Model_Score"
GROUP BY cs_id;

SELECT cs_id
       ,avg(score) AS raw_score
        ,round(avg(score))
        ,now()::date
FROM "Building_Model_Score" as bms
where bms.model_id in (13,15)
GROUP BY cs_id;


insert into "Building_Model_Score" (cs_id, model_id, raw_score, score, date_calculated)
    SELECT cs_id
    ,avg(score)
    ,17
    ,round(avg(score))
    ,now()::date
    FROM "Building_Model_Score" as bms
    where bms.model_id in (13,15)
    GROUP BY cs_id
on conflict on constraint building_model_pk do update
set score = excluded.score,
raw_score = excluded.raw_score,
date_calculated = excluded.date_calculated;