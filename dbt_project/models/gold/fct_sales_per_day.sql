select
    cart_timestamp::date as sale_date,
    count(distinct cart_id) as number_of_carts,
    count(distinct user_id) as number_of_customers,
    sum(total_price) as total_revenue
from {{ ref('fct_sales') }}
group by 1
order by 1 desc