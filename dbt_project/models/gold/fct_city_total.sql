select
    city,
    sum(total_price) as total_revenue
from {{ ref('fct_sales') }}
group by 1
order by 2 desc