select
bd."CS_ID"
,concat('LN-',bd."CS_ID")
,(select count(1) from "Building" where "CS_ID"=concat('LN-',bd."CS_ID"))
from "Building" as bd
where
bd."CS_ID" not like 'LN%';

update "Building" set
    "CS_ID" = concat('LN-',"CS_ID")
where
"CS_ID" not like 'LN%' and
"CS_ID" not in ('21468327','18771550','21769054','20742136','20956338','21058749','20058903');

select count(1) from "Building" where "CS_ID"= concat('LN-',"CS_ID")."CS_ID") group by "CS_ID";

select
    b."CS_ID"
    ,r.cs_id
    ,b."SquareFeet"
    ,r."SquareFeet"
from "Building" as b
left join result5 as r on r.cs_id=b."CS_ID"
where b."SquareFeet" is null
and r."SquareFeet" is not null;

update "Building"

select * from result5