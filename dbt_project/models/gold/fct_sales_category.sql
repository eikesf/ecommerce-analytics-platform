select
    product_category,
    sum(quantity) as units_sold,
    sum(total_price) as total_revenue
from {{ ref('fct_sales') }}
group by 1
order by 3 desc