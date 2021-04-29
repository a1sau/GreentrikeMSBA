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


create table "ETL_Building"
(
	"Address_Line" varchar,
	"City" varchar,
	"State" varchar,
	"Postal_Code" varchar,
	"Property_Type" varchar,
	bg_geo_id varchar,
	"CS_ID" varchar not null,
	url varchar,
	"Price" double precision,
	"SquareFeet" double precision,
	"Building_Class" varchar,
	"Year_Built" varchar,
	"Sale_Type" varchar,
	"Picture_url" varchar,
	"Upload_Date" date,
	"Currently_listed" boolean,
	"Sale_Lease" varchar,
	"old_CS_ID" varchar,
	"Price_monthly" double precision,
	"Price_yearly" double precision,
	"Expansion_sqft" double precision,
	"Space" varchar,
	"Condition" varchar,
	"Available" varchar,
	"Term" varchar
);

alter table "Building" owner to postgres;

grant insert, select, update, delete, truncate, references, trigger on "Building" to public;

grant insert, select, update, delete, truncate, references, trigger on "Building" to aneims;

grant insert, select, update, delete, truncate, references, trigger on "Building" to bpope;

grant insert, select, update, delete, truncate, references, trigger on "Building" to dbliler;

grant insert, select, update, delete, truncate, references, trigger on "Building" to eotanez;

grant insert, select, update, delete, truncate, references, trigger on "Building" to mmelgare;
