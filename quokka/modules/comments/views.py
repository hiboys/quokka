#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask.views import MethodView
from flask_mongoengine.wtf import model_form
from flask_mongoengine.wtf.models import ModelForm
from flask_security import current_user
from quokka.core.templates import render_template
from quokka.core.fields import CaptchaField
from .models import Comment
from wtforms import HiddenField, StringField, ValidationError

import logging
logger = logging.getLogger()

class CommentModelForm(ModelForm):
    reply_to_comment = HiddenField("reply_to_comment")
    captcha = CaptchaField("captcha")


class CommentView(MethodView):

    form = model_form(
        Comment,
        base_class=CommentModelForm,
        only=['author_name', 'author_email', 'body']
    )

    @staticmethod
    def render_context(path, form, parent_comment=None):
        comments = Comment.objects.exclude("content").filter(path=path, published=True, is_reply=False)

        return render_template('content/comments.html',
                               comments=comments,
                               form=form,
                               path=path,
                               parent_comment=parent_comment)

    def get(self, path):
        reply_to_comment = ""
        parent_comment = None
        if request.args.has_key("replytocom"):
            reply_to_comment = request.args["replytocom"]
            try:
                parent_comment = Comment.objects.get(pk=reply_to_comment)
            except Exception, ex:
                logger.exception(ex)
        return self.render_context(path,
                                   form=self.form(reply_to_comment=reply_to_comment),
                                   parent_comment=parent_comment)

    def post(self, path):
        form = self.form(request.form)

        if form.validate():
            comment = Comment(path=path)
            form.populate_obj(comment)

            if current_user.is_authenticated:
                comment.published = True
                comment.author_name = current_user.name
                comment.author_email = current_user.email
            comment.save()

            #get the reply to comment id from the form
            reply_to_comment = form.reply_to_comment.data
            if reply_to_comment is not None and len(reply_to_comment) != 0:
                try:
                    comment.is_reply = True
                    comment.save()
                    Comment.objects(pk=reply_to_comment).update_one(push__replies=comment)
                except Exception, e:
                    comment.delete()
                    logger.exception(e)

            return self.render_context(path, form=self.form())

        return self.render_context(path, form=form)
