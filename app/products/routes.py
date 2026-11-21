from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask import send_from_directory
from tinydb import Query, TinyDB
from werkzeug.utils import secure_filename

from . import products_bp
from .forms import ProductForm


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "products.json"
UPLOAD_PATH = Path(__file__).resolve().parent / "static" / "uploads"


def product_table():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return TinyDB(DB_PATH).table("products")


def get_product(product_id):
    return product_table().get(Query().id == product_id)


@products_bp.route("/product/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_PATH, filename)


def save_image(upload):
    if not upload or not upload.filename:
        return None
    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
    extension = secure_filename(upload.filename).rsplit(".", 1)[-1].lower()
    filename = f"{uuid4().hex}.{extension}"
    upload.save(UPLOAD_PATH / filename)
    return f"uploads/{filename}"


@products_bp.route("/products/")
@products_bp.route("/product")
def index():
    products = sorted(product_table().all(), key=lambda item: item["id"])
    return render_template("products/products.html", products=products)


@products_bp.route("/products/<int:product_id>")
@products_bp.route("/product/<int:product_id>")
def detail(product_id):
    product = get_product(product_id)
    if product is None:
        abort(404)
    return render_template("products/detail_product.html", product=product)


@products_bp.route("/product/add", methods=["GET", "POST"])
def add():
    form = ProductForm()
    if form.validate_on_submit():
        try:
            table = product_table()
            product_id = max((item["id"] for item in table.all()), default=0) + 1
            price = Decimal(form.price.data.replace(",", "."))
            product = {"id": product_id, "name": form.name.data.strip(), "content": form.content.data,
                       "price": f"{price:.2f}", "category": form.category.data,
                       "quantity": form.quantity.data, "image": save_image(form.image.data),
                       "created_at": datetime.now(timezone.utc).isoformat()}
            table.insert(product)
            flash("Товар успішно додано.", "success")
            return redirect(url_for("products.detail", product_id=product_id))
        except OSError:
            current_app.logger.exception("Could not save product")
            flash("Не вдалося зберегти товар.", "error")
    return render_template("products/product_form.html", form=form, title="Додати товар")


@products_bp.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit(product_id):
    product = get_product(product_id)
    if product is None:
        abort(404)
    form = ProductForm()
    if form.validate_on_submit():
        try:
            image = save_image(form.image.data) or product.get("image")
            price = Decimal(form.price.data.replace(",", "."))
            changes = {"name": form.name.data.strip(), "content": form.content.data, "price": f"{price:.2f}",
                       "category": form.category.data, "quantity": form.quantity.data, "image": image}
            product_table().update(changes, Query().id == product_id)
            flash("Зміни товару збережено.", "success")
            return redirect(url_for("products.detail", product_id=product_id))
        except OSError:
            current_app.logger.exception("Could not update product")
            flash("Не вдалося зберегти зміни товару.", "error")
    elif not form.is_submitted():
        form.name.data = product["name"]
        form.content.data = product["content"]
        form.price.data = str(product["price"])
        form.category.data = product["category"]
        form.quantity.data = product["quantity"]
    return render_template("products/product_form.html", form=form, title="Редагувати товар", product=product)


@products_bp.route("/product/<int:product_id>/delete", methods=["POST"])
def delete(product_id):
    product = get_product(product_id)
    if product is None:
        abort(404)
    product_table().remove(Query().id == product_id)
    if product.get("image"):
        (UPLOAD_PATH / Path(product["image"]).name).unlink(missing_ok=True)
    flash("Товар видалено.", "success")
    return redirect(url_for("products.index"))
