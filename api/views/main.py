from flask import Blueprint, request
from flask import Response, render_template
from api.models import db, Email, Link
from api.core import create_response, serialize_list, logger
from sqlalchemy import inspect
import json

main = Blueprint("main", __name__)  # initialize blueprint

def create_link(created_by, parent_link_id):
    new_link = Link()
    if parent_link_id is not None:
        link = Link.query.filter_by(id=parent_link_id).first()
        new_link.parent_link_id = link.id
        if link.root_link_id is None:
            new_link.root_link_id = link.id #this link is the root link
            original_user = link.created_by
        else:
            root_link = Link.query.filter_by(id=link.root_link_id).first()
            new_link.root_link_id = root_link.id
            original_user = root_link.created_by
    else:
        new_link.parent_link = None
        new_link.root_link = None
        original_user = created_by #new link this is root

    url = Link.url_from_username(original_user, created_by)
    new_link.url = url
    new_link.desc = f"af link by {created_by}"
    new_link.created_by = created_by

    db.session.add(new_link)
    db.session.commit()
    new_link = Link.query.filter_by(url=url).first()
    return new_link

# function that is called when you visit /
@main.route("/")
def index():
    # just show a nice page saying what this is
    logger.info("Hello World!")
    return render_template('index.html')

# create new af link - takes either the username of the person or another af link
@main.route("/links", methods=["GET"])
def alllinks():
    body = request.json
    links = Link.query.all()
    return Response(json.dumps(serialize_list(links)), mimetype='application/json', status=200)


# create new af link - takes either the username of the person or another af link
@main.route("/link", methods=["POST"])
def createlink():
    body = request.json
    if 'created_by' not in body:
        return Response(json.dumps({'error': 'need to know who is creating this link' }), mimetype='application/json', status=400)
    original_user = None
    created_by = body['created_by']
    #username is who is generating the link once he submits email
    if 'parent_link_id' in body and len(body['parent_link_id']) > 0:
        link_id = body['parent_link_id']
    else:
        link_id = None

    new_link = create_link(created_by, link_id)
    return Response(json.dumps(new_link.to_dict()), mimetype='application/json', status=200)

# take email and the link for which the email was submitted
@main.route("/email", methods=["POST"])
def email():
    body = request.json
    if 'email' not in body or 'link_id' not in body or 'username' not in body:
        return Response(json.dumps({'error': 'need both email and which link this email was given to' }), mimetype='application/json', status=400)
    email = body['email']
    new_submit = Email(email)
    link_id = body['link_id']
    username = body.get('username')
    link = Link.query.filter_by(id=int(link_id)).first()
    new_submit.parent_link_id = link.id
    new_submit.name = body.get('name','')
    new_submit.username = username
    db.session.add(new_submit)
    db.session.commit()
    submitted_email = Email.query.filter_by(parent_link_id=link.id, email=email).first()
    aflink = create_link(username, link_id)
    return Response(json.dumps({ 'email': submitted_email.to_dict(), 'aflink': aflink.to_dict() }), mimetype='application/json', status=200)


#render the page to submit one's email
@main.route("/l/<linkurl>", methods=["GET"])
def rendersubmit(linkurl):
    link = Link.query.filter_by(url=linkurl).first()
    username = request.args.get('u','')
    if link is None:
        return Response(json.dumps({'error': 'wrong link url' }), mimetype='application/json', status=404)
    return render_template('submit.html', link_id=link.id,username=username)

#get all emails submitted for a particular user
@main.route("/emails", methods=["GET"])
def getemails():
    root_created_by = request.args.get('root_created_by', None)
    if root_created_by is None:
        return Response(json.dumps({'error': 'need subscriber' }), mimetype='application/json', status=400)
    original_links = Link.query.filter_by(created_by=root_created_by).all()
    all_links = []
    parent_links = original_links
    print(original_links)
    while parent_links is not None and len(parent_links) > 0:
        all_links = all_links + parent_links
        parent_links_ids = ( l.id for l in parent_links )
        print('PARENT LINK IDS IS', parent_links_ids)
        next_links = Link.query.filter(Link.parent_link_id.in_(parent_links_ids)).all()
        parent_links = next_links
    #get all the emails for these links
    all_links_ids = ( l.id for l in all_links )
    emails = Email.query.filter(Email.parent_link_id.in_(all_links_ids)).all()
    return Response(json.dumps(serialize_list(emails)), mimetype='application/json', status=200)
