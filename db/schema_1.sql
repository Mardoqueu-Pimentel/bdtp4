create table product
(
    id         integer not null
        constraint product_primary_key_id
            primary key,
    asin       varchar
        constraint product_key_asin
            unique,
    title      varchar,
    "group"    varchar,
    sales_rank varchar
);

alter table product
    owner to mard;

create table product_similar
(
    first_prod_id  integer not null
        constraint first_product_fkey
            references product,
    second_prod_id integer not null
        constraint second_product_fkey
            references product,
    constraint product_similar_key
        primary key (first_prod_id, second_prod_id)
);

alter table product_similar
    owner to mard;

create table category
(
    id   integer not null
        constraint category_primary_key
            primary key,
    name varchar
);

alter table category
    owner to mard;

create table product_category
(
    prod_id integer not null
        constraint product_category_fkey1
            references product,
    cat_id  integer not null
        constraint product_category_fkey2
            references category,
    constraint product_category_primary_key
        primary key (prod_id, cat_id)
);

alter table product_category
    owner to mard;

create table review
(
    prod_id     integer
        constraint review_fk
            references product,
    customer_id integer,
    rating      integer,
    votes       integer,
    helpful     integer
);

alter table review
    owner to mard;


