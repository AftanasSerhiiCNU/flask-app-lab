from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Enum,
    Boolean,
    ForeignKey,
    Column,
    Integer,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db

post_tags = db.Table(
    "post_tags",
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(150), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    posted: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        Enum("news", "publication", "tech", "other", name="post_category"),
        default="other",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("1"),
        nullable=False,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="posts",
    )

    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts",
    )

    def __repr__(self):
        return f"<Post(title={self.title})>"


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags",
    )

    def __repr__(self):
        return f"<Tag(name={self.name})>"
