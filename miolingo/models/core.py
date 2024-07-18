# from datetime import datetime
#
# from sqlalchemy import SmallInteger, String, DateTime, func
# from sqlalchemy.orm import Mapped, mapped_column
#
# from miolingo.db.base_class import Base, BaseModelMixin
#
#
# class Translation(BaseModelMixin, Base):
#     lang: Mapped[str] = mapped_column(String(length=2))  # @todo enum or validate?
#
#     text: Mapped[str] = mapped_column(String(length=2048))
#     # slug = models.SlugField(max_length=2048, null=True, editable=False)  # @todo
#
#     priority: Mapped[str] = mapped_column(SmallInteger, default=0)
#
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=func.now(),
#     )  # @FIXME store in UTC!
#     modified_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=func.now(),
#         onupdate=func.now(),
#     )  # @FIXME store in UTC!
#
#     # user = models.ForeignKey(
#     #     User,
#     #     on_delete=models.CASCADE,
#     #     related_name="translations",
#     # )
#     #
#     # trans = models.ManyToManyField("self")
#     #
#     # class Meta:
#     #     unique_together = ("lang", "slug", "user")
#     #
#     # def __str__(self):
#     #     return f"{self.text} ({self.lang})"
#     #
#     # def save(self, *args, **kwargs):
#     #     if not self.slug:
#     #         self.slug = slugify(self.text)
#     #     return super().save(*args, **kwargs)
