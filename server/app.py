import flask
from flask_sqlalchemy import SQLAlchemy
import os
import hmac
from dotenv import load_dotenv
from flask import Response
from datetime import datetime

load_dotenv()
app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
APP_EMAIL = os.getenv("APP_EMAIL")
EMAIL_HOST = os.getenv("EMAIL_HOST")
APP_EMAIL_PASSWORD = os.getenv("APP_EMAIL_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
EMAIL_PORT= os.getenv("EMAIL_PORT")
KEY = os.getenv("KEY")
LOGS_DIR = os.path.join(os.path.dirname(__file__),"/logs")

class Transaction(db.Model):
    transaction = db.Column(db.String, primary_key=True)
    
if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)

with app.app_context():
    db.create_all()
 
@app.route('/transaction', methods=['POST'])
def transaction():
    transaction = flask.request.json['originAccount'] +"    "+ flask.request.json['destinationAccount'] +"    "+ flask.request.json['amount'] +"    "+ flask.request.json['nonce']
    new_nonce = Transaction(transaction=transaction)
    if (db.session.query(Transaction).filter_by(transaction=transaction).first()):
        with open('logs/log_'+str(datetime.now().date())+'.txt', 'a') as file:
            file.write('This transaction is duplicated\n')
            file.write('Transaction:    ' + transaction + '\n\n')
        return Response("This transaction is duplicated", status = 400)
    
    if (flask.request.json['hash'] != hmac.new(KEY.encode(), bytes(transaction.encode('utf-8')), "sha256").hexdigest()):
        with open('logs/log_'+str(datetime.now().date())+'.txt', 'a') as file:
            file.write('Invalid transaction hash\n')
            file.write('Transaction:    ' + transaction + '\n\n')
        return Response("Invalid hash", status=400)

    db.session.add(new_nonce)
    db.session.commit()
    return Response("Transaction made successfully", status=200)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
