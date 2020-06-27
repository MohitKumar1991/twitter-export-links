from flask import Blueprint, request
from flask import Response, render_template
from api.models import db, Person, Email
from api.core import create_response, serialize_list, logger
from sqlalchemy import inspect

main = Blueprint("main", __name__)  # initialize blueprint

# function that is called when you visit /
@main.route("/")
def index():
    # just show a nice page saying what this is
    logger.info("Hello World!")
    return render_template('index.html')

# create new af link - takes either the username of the person or another af link
@main.route("/link", methods=["POST"])
def createlink():
    body = request.json
    if 'created_by' not in body:
        return Response(json.dumps({'error': 'need to know who is creating this link' }), mimetype='application/json', status=400)
    original_user = None
    created_by = body['created_by']
    #username is who is generating the link once he submits email
    new_link = Link()
    if 'link_id' in body:
        link = Link.query.first(id=body['link_id'])
        new_link.parent_link = link
        new_link.root_link = link.root_link
        original_user = link.root_link.created_by
    else:
        new_link.parent_link = None
        new_link.root_link = None
        original_user = created_by #new link this is root

    new_link.url = Link.url_from_username(original_user, created_by)
    new_link.desc = f"af link by {created_by}"

    db.session.add_all([new_link])
    db.session.commit()
    return Response(json.dumps(new_link.to_dict()), mimetype='application/json', status=200)

# take email and the link for which the email was submitted
@main.route("/email", methods=["POST"])
def email():
    body = request.json
    if 'email' not in body or 'link_id' not in body:
        return Response(json.dumps({'error': 'need both email and which link this email was given to' }), mimetype='application/json', status=400)
    new_submit = body['email']
    link_id = body['link_id']
    link = Link.query.first(id=link_id)
    new_submit.parent_link = link
    new_submit.email = email
    new_submit.name = body.get('name','')
    db.session.add_all([new_submit])
    db.session.commit()
    return Response(json.dumps(new_submit.to_dict()), mimetype='application/json', status=200)


#render the page to submit one's email
@main.route("/submit_email", methods=["GET"])
def rendersubmit():
    return render_template('submit.html')

#get all emails submitted for a particular user
@main.route("/emails", methods=["POST"])
def getemails():
    root_created_by = request.args.get('root_created_by')
    original_links = Link.query.filter_by(created_by=root_created_by).all()
    all_links = []
    parent_links = original_links
    while parent_links is not None and len(parent_links) > 0:
        all_links = all_links + parent_links
        next_links = Link.query.filter(Link.parent_link.in_(parent_links)).all()
        parent_links = next_links
    #get all the emails for these links
    emails = Email.query.filter(Email.parent_link.in_(all_links)).all()
    return Response(json.dumps(serialize_list(emails)), mimetype='application/json', status=200)
