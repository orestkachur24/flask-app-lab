"""Insert seed data into products table

Revision ID: 09616d15fab4
Revises: b6fe30c28abc
Create Date: 2026-11-21 19:35:42.447197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09616d15fab4'
down_revision = 'b6fe30c28abc'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    categories = sa.table("categories", sa.column("id", sa.Integer), sa.column("name", sa.String))
    products = sa.table(
        "products", sa.column("id", sa.Integer), sa.column("name", sa.String),
        sa.column("price", sa.Float), sa.column("active", sa.Boolean),
        sa.column("category_id", sa.Integer),
    )
    seeded_categories = ("Electronics", "Books", "Clothing")
    category_ids = {}
    for name in seeded_categories:
        category_id = bind.execute(sa.select(categories.c.id).where(categories.c.name == name)).scalar_one_or_none()
        if category_id is None:
            bind.execute(categories.insert().values(name=name))
            category_id = bind.execute(sa.select(categories.c.id).where(categories.c.name == name)).scalar_one()
        category_ids[name] = category_id

    seed_products = [
        ("Laptop", 1200.0, True, "Electronics"),
        ("Smartphone LG", 800.0, True, "Electronics"),
        ("Novel", 20.0, True, "Books"),
        ("T-Shirt", 25.0, False, "Clothing"),
    ]
    for name, price, active, category in seed_products:
        exists = bind.execute(sa.select(products.c.id).where(products.c.name == name)).first()
        if exists is None:
            bind.execute(products.insert().values(
                name=name, price=price, active=active, category_id=category_ids[category]
            ))


def downgrade():
    bind = op.get_bind()
    categories = sa.table("categories", sa.column("id", sa.Integer), sa.column("name", sa.String))
    products = sa.table("products", sa.column("id", sa.Integer), sa.column("name", sa.String),
                        sa.column("category_id", sa.Integer))
    seed_products = ("Laptop", "Smartphone LG", "Novel", "T-Shirt")
    seed_categories = ("Electronics", "Books", "Clothing")
    bind.execute(products.delete().where(products.c.name.in_(seed_products)))
    for name in seed_categories:
        still_used = sa.exists(sa.select(products.c.id).where(products.c.category_id == categories.c.id))
        bind.execute(categories.delete().where(categories.c.name == name, ~still_used))
