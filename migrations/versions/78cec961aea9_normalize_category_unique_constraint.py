"""Normalize category unique constraint

Revision ID: 78cec961aea9
Revises: 09616d15fab4
Create Date: 2026-11-21 19:43:25.728497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78cec961aea9'
down_revision = '09616d15fab4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "_categories_new",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_categories"),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_table(
        "_products_new",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["_categories_new.id"], name="fk_products_category_id_categories"),
        sa.PrimaryKeyConstraint("id", name="pk_products"),
    )
    op.execute("INSERT INTO _categories_new (id, name) SELECT id, name FROM categories")
    op.execute("INSERT INTO _products_new (id, name, price, category_id, active, created_at) SELECT id, name, price, category_id, active, created_at FROM products")
    op.drop_table("products")
    op.drop_table("categories")
    op.rename_table("_categories_new", "categories")
    op.rename_table("_products_new", "products")


def downgrade():
    op.create_table(
        "_categories_old",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_table(
        "_products_old",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["_categories_old.id"], name="category_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("INSERT INTO _categories_old (id, name) SELECT id, name FROM categories")
    op.execute("INSERT INTO _products_old (id, name, price, category_id, active, created_at) SELECT id, name, price, category_id, active, created_at FROM products")
    op.drop_table("products")
    op.drop_table("categories")
    op.rename_table("_categories_old", "categories")
    op.rename_table("_products_old", "products")
