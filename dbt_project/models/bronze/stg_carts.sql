with source as (
    select
        id as cart_id,
        user_id,
        date as cart_date,
        products as products_json,
        _loaded_at
    from {{ source('bronze', 'carts') }}
)
select
    source.cart_id,
    source.user_id,
    source.cart_date,
    (product_data ->> 'productId')::int as product_id,
    (product_data ->> 'quantity')::int as quantity,
    source._loaded_at
from source,
lateral jsonb_array_elements(source.products_json) as product_data