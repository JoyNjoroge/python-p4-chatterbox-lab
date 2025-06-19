from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods = ['GET', 'POST'])
def messages():
    if request.method == "GET":
        msgs = Message.query.order_by(Message.created_at.asc()).all()
        return make_response([m.to_dict() for m in msgs], 200)


    data = request.get_json(silent=True) or request.form

    body     = data.get("body")
    username = data.get("username")

    if not body or not username:
        return make_response(
            {"error": "body and username required"}, 400
        )

    new_msg = Message(body=body, username=username)
    db.session.add(new_msg)
    db.session.commit()

    return make_response(new_msg.to_dict(), 201)

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    msg = Message.query.get(id)
    if not msg:
        return make_response({"error": "Message not found"}, 404)


    if request.method == "GET":
        return make_response(msg.to_dict(), 200)

    if request.method == "PATCH":
        data = request.get_json(silent=True) or request.form
        if "body" in data:
            msg.body = data["body"]
            db.session.add(msg)
            db.session.commit()
        return make_response(msg.to_dict(), 200)


    if request.method == "DELETE":
        db.session.delete(msg)
        db.session.commit()
        return make_response({}, 204)

if __name__ == '__main__':
    app.run(port=5555)
