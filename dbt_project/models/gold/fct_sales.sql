{{
    config(
        materialized='view',
        unique_key='sales_id'
    )
}}

select
    (sc.cart_id || '-' || sc.product_id) as sales_id,
    sc.cart_id,
    sc.user_id,
    sc.product_id,
    du.username,
    du.city,
    dp.product_title,
    dp.product_category,
    sc.quantity,
    dp.product_price,
    (sc.quantity * dp.product_price) as total_price,
    sc.cart_timestamp,
    sc._loaded_at
from
    {{ref('int_carts')}} sc
left join {{ref('dim_users')}} du on sc.user_id = du.user_id
left join {{ref('dim_products')}} dp on sc.product_id = dp.product_id

{% if is_incremental() %}

    where sc._loaded_at > (select max(_loaded_at) from {{this}})

{% endif %}