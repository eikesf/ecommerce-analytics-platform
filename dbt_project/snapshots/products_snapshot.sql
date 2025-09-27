{% snapshot products_snapshot %}

{{
    config(
        target_schema='silver',
        unique_key='id',
        strategy='timestamp',
        updated_at='_loaded_at',
    )
}}

select * from {{ source('bronze', 'products') }}

{% endsnapshot %}