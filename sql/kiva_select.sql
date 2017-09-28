SELECT status, count(1)
FROM loan
GROUP BY status


SELECT date_trunc('month', posted_date) AS max_posted_date, status, count(*)
FROM loan
WHERE status IN ('expired', 'funded')
GROUP BY max_posted_date, status
ORDER BY max_posted_date;

SELECT sector, count(1) AS count
FROM loan
GROUP BY sector
ORDER BY count DESC;


-- Look at funding rate by country
SELECT location_country, expired, funded,
       expired::FLOAT / ((expired::FLOAT) + (funded::FLOAT)) AS expiration_rate,
       funded::FLOAT / ((expired::FLOAT) + (funded::FLOAT)) AS funding_rate
FROM (
   SELECT * FROM crosstab (
       'SELECT location_country, status, count(1) AS count
        FROM loan
        GROUP BY location_country, status'

      ,$$VALUES ('expired'::text), ('funded'::text)$$)
   AS ct ("location_country" text, "expired" int, "funded" text)
) c
WHERE
  expired IS NOT NULL
  AND funded IS NOT NULL
  AND expired >= 100
ORDER BY expiration_rate DESC

-- Look at funding rate by sector
SELECT sector, expired, funded,
       expired::FLOAT / ((expired::FLOAT) + (funded::FLOAT)) AS expiration_rate,
       funded::FLOAT / ((expired::FLOAT) + (funded::FLOAT)) AS funding_rate
FROM (
   SELECT * FROM crosstab (
       'SELECT sector, status, count(1) AS count
        FROM loan
        GROUP BY sector, status'

      ,$$VALUES ('expired'::text), ('funded'::text)$$)
   AS ct ("sector" text, "expired" int, "funded" text)
) c
WHERE
  expired IS NOT NULL
  AND funded IS NOT NULL
ORDER BY expiration_rate DESC

SELECT activity, count(1) AS count
FROM loan
GROUP BY activity
ORDER BY count DESC;

SELECT p.id, count(*)
FROM loan l
LEFT OUTER JOIN partner p ON l.partner_id = p.id
GROUP BY p.id
HAVING count(*) = 1

SELECT file_index, max(date_trunc('month', posted_date)) AS max_posted_date, min(date_trunc('month', posted_date)) AS min_posted_date, count(*)
FROM loan
GROUP BY file_index
ORDER BY max_posted_date;
