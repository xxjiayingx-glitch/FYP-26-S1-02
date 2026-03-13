from flask import Blueprint, request, redirect, session
from control.CommentController import add_comment

comment_bp = Blueprint('comment', __name__)

@comment_bp.route("/add_comment", methods=["POST"])
def add_comment_route():

    articleID = request.form["articleID"]
    commentText = request.form["commentText"]
    userID = session["userID"]

    add_comment(articleID, userID, commentText)

    return redirect("/dashboard")

