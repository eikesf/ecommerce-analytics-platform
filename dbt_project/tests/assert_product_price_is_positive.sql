select
    *
from {{ref('dim_products')}}
where product_price < 0