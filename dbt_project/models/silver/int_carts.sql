with stg_carts as (
    select * from {{ ref('stg_carts') }}
)
select
    cart_id,
    user_id,
    product_id,
    quantity,
    cart_date::timestamp as cart_timestamp,
    _loaded_at
from stg_carts