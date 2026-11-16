from datetime import datetime, timezone

from flask import render_template, request, redirect, url_for, flash, session

from app import db
from app.posts import post_bp
from app.posts.models import Post
from app.posts.forms import PostForm, DeletePostForm


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        author = session.get("username") or "Anonymous"

        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            is_active=form.is_active.data,
            posted=form.publish_date.data
            or datetime.now(timezone.utc).replace(tzinfo=None),
            category=form.category.data,
            author=author[:20],
        )

        db.session.add(new_post)
        db.session.commit()

        flash("Post added successfully", "success")

        return redirect(url_for("posts.list_posts"))

    if request.method == "POST":
        flash("Перевірте правильність заповнення форми.", "danger")

    return render_template(
        "posts/add_post.html", title="Створити новий пост", form=form
    )


@post_bp.route("", methods=["GET"])
@post_bp.route("/", methods=["GET"])
def list_posts():
    stmt = db.select(Post).where(Post.is_active.is_(True)).order_by(Post.posted.desc())

    posts = db.session.scalars(stmt).all()

    return render_template("posts/posts.html", title="Список постів", posts=posts)


@post_bp.route("/<int:id>", methods=["GET"])
def post_detail(id):
    post = db.get_or_404(Post, id)

    return render_template("posts/detail_post.html", title=post.title, post=post)


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id):
    post = db.get_or_404(Post, id)

    form = PostForm(obj=post)

    if request.method == "GET":
        form.publish_date.data = post.posted

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.is_active = form.is_active.data
        post.category = form.category.data
        post.posted = form.publish_date.data or post.posted

        db.session.commit()

        flash("Пост успішно оновлено!", "success")

        return redirect(url_for("posts.post_detail", id=post.id))

    if request.method == "POST":
        flash("Перевірте правильність заповнення форми.", "danger")

    return render_template(
        "posts/add_post.html", title="Редагувати пост", form=form, editing=True
    )


@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
def delete_post(id):
    post = db.get_or_404(Post, id)

    form = DeletePostForm()

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()

        flash("Пост успішно видалено!", "success")

        return redirect(url_for("posts.list_posts"))

    return render_template(
        "posts/delete_confirm.html", title="Видалення поста", post=post, form=form
    )
