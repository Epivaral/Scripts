
-- get service tier info for all user databases

select db.name as DB, edition, service_objective, elastic_pool_name
from sys.database_service_objectives SO 
INNER JOIN sys.databases DB
ON SO.database_id = DB.database_id
order by DB