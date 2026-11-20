from datetime import datetime, timezone

from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import select

from app import db
from app.posts import post_bp
from app.posts.models import Post, Tag
from app.posts.forms import PostForm, DeletePostForm
from app.users.models import User


def set_author_choices(form):
    users = db.session.scalars(select(User).order_by(User.username)).all()

    form.user_id.choices = [(user.id, user.username) for user in users]


def set_tag_choices(form):
    tags = db.session.scalars(select(Tag).order_by(Tag.name)).all()

    form.tags.choices = [(tag.id, tag.name) for tag in tags]


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()
    set_author_choices(form)
    set_tag_choices(form)

    if form.validate_on_submit():
        selected_tags = db.session.scalars(
            select(Tag).where(Tag.id.in_(form.tags.data))
        ).all()

        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            is_active=form.is_active.data,
            posted=form.publish_date.data
            or datetime.now(timezone.utc).replace(tzinfo=None),
            category=form.category.data,
            user_id=form.user_id.data,
            tags=selected_tags,
        )

        db.session.add(new_post)
        db.session.commit()

        flash("Пост успішно створено!", "success")

        return redirect(url_for("posts.list_posts"))

    if request.method == "POST":
        flash("Перевірте правильність заповнення форми.", "danger")

    return render_template(
        "posts/add_post.html",
        title="Створити новий пост",
        form=form,
    )


@post_bp.route("", methods=["GET"])
@post_bp.route("/", methods=["GET"])
def list_posts():
    stmt = select(Post).where(Post.is_active.is_(True)).order_by(Post.posted.desc())

    posts = db.session.scalars(stmt).all()

    return render_template(
        "posts/posts.html",
        title="Список постів",
        posts=posts,
    )


@post_bp.route("/<int:id>", methods=["GET"])
def post_detail(id):
    post = db.get_or_404(Post, id)

    return render_template(
        "posts/detail_post.html",
        title=post.title,
        post=post,
    )


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id):
    post = db.get_or_404(Post, id)

    form = PostForm(obj=post)
    set_author_choices(form)
    set_tag_choices(form)

    if request.method == "GET":
        form.publish_date.data = post.posted
        form.tags.data = [tag.id for tag in post.tags]

    if form.validate_on_submit():
        selected_tags = db.session.scalars(
            select(Tag).where(Tag.id.in_(form.tags.data))
        ).all()

        post.title = form.title.data
        post.content = form.content.data
        post.is_active = form.is_active.data
        post.category = form.category.data
        post.posted = form.publish_date.data or post.posted
        post.user_id = form.user_id.data
        post.tags = selected_tags

        db.session.commit()

        flash("Пост успішно оновлено!", "success")

        return redirect(url_for("posts.post_detail", id=post.id))

    if request.method == "POST":
        flash("Перевірте правильність заповнення форми.", "danger")

    return render_template(
        "posts/add_post.html",
        title="Редагувати пост",
        form=form,
        editing=True,
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
        "posts/delete_confirm.html",
        title="Видалення поста",
        post=post,
        form=form,
    )
