from flask import Flask, request, jsonify, json, Response
from pyfcm import FCMNotification
from pymongo import MongoClient
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from bson.objectid import ObjectId
from random import random

server = Flask(__name__)
client = MongoClient("ds253918.mlab.com",53918)

db = client["lendr"]
db.authenticate("admin","lendr")

push_service = FCMNotification(api_key="AAAAShAnsbk:APA91bGm7bK9Jlc7pFu38oQ-9w1_q0qQEfiJwrIgg0NS1sV-F47Il8kn6cJWPwUHo4RlSJAGN0nWkCQDMUNOs2xGAGu53dP1x7Ha5YZachCfqB2osU0SK7NVpBI34A1GAVAv8wO9WFFL")

cred = credentials.Certificate("cert.json")
firebase_admin.initialize_app(cred)

@server.route('/api/v1/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        user_register = request.form.to_dict()
        print(user_register)
        auth_token = str(user_register["auth_token"])
        try:
            decoded_token = auth.verify_id_token(auth_token)
        except ValueError:
            return "Fail"
        uid = decoded_token['uid']
        # hash_f = hashlib.md5((str(user_register["firebase_id"]) + str(user_register["username"])  + "pollr").encode("utf-8"))

        db.users.insert_one({
            "username": str(auth.get_user(uid).display_name),
            "session_id": auth_token,
            "loan_requests":[],
            "loan_payments":[],
            "credit_score": 0,
            "credit_card": 0,
            "ccv":123
        })


    return "Success!"
@server.route('/api/v1/login', methods=['POST'])
def login():
    if request.method == 'POST':
        user_login = request.form.to_dict()
        print(user_login)
        auth_token = str(user_login["auth_token"])
        try:
            decoded_token = auth.verify_id_token(auth_token)
        except ValueError:
            return "Fail"
        uid = decoded_token['uid']
        # username = auth
        user_match = db.users.find_one({
            "username" : str(auth.get_user(uid).display_name)
        })

        if(user_match == None):
            return "Fail"
        # print(user_match["password"],user_login["password"])
        # if(user_match["auth_token"] == user_login["password"]):
        #     registration_id = user_match["firebase_id"]
        #     return user_match["hash_f"]
        return "Success"
@server.route('/api/v1/loans_get', methods=['GET'])
def loans_get():
    if request.method == 'GET':
        ses_id = request.args.get("auth_token")


        auth_token = str(ses_id)
        decoded_token = auth.verify_id_token(auth_token)
        uid = -1
        if "uid" in decoded_token.keys():
            uid = decoded_token['uid']
        else:
            return "Fail"

        username = str(auth.get_user(uid).display_name)
        user_match = db.users.find_one({
            "username" : username
        })
        type_u = request.args.get("type")

        if(user_match == None):
            return "Faill"
        user_info = db.users.find_one({"username": username})
        if(type_u == "loaner"):
            loans = []
            loan_list = user_info["loan_payments"]
            for i in loan_list:
                #loans.append({"id":i["id"],"amount":i["amount"]})
                payment_info = db.loan_payments.find_one({"_id":str(ObjectId(i))})
                amount = payment_info["amount"]
                loan_id = payment_info["loan_id"]
                user_loan = db.users.find_one({"loan_requests": loan_id})
                current_amount = db.loan_requests.find_one({"_id":str(ObjectId(loan_id))})["current_amount"]
                title = db.loan_requests.find_one({"_id":str(ObjectId(loan_id))})["title"]
                loans.append({"id":i, "current_amount":  current_amount, "amount": payment_info["amount"],"risk":user_loan["credit_score"],"title": title})
            return jsonify(loans)
        elif(type_u == "borrower"):
            requests = []
            request_list = user_info["loan_requests"]
            for i in request_list:
                print(i)
                loan_request_info = db.loan_requests.find_one({"_id": ObjectId(str(i))})
                print("hi",loan_request_info)
                current_amount = loan_request_info["current_amount"]
                amount = loan_request_info["amount"]
                title = loan_request_info["title"]
                risk = loan_request_info["credit_rating"]

                requests.append({"id":str(i), "current_amount":  current_amount, "amount": amount,"risk": risk,"title": title})
            # print()
            # return Response(requests, mimetype=)
            print(requests)
            return jsonify(requests)
        return "Fail"


            #total  payment, money paid, monthly
@server.route('/api/v1/loan_get', methods=['GET'])
def loan_get():
    if request.method == 'GET':
        ses_id = request.args.get("auth_token")


        auth_token = str(ses_id)
        decoded_token = auth.verify_id_token(auth_token)
        uid = -1
        if "uid" in decoded_token.keys():
            uid = decoded_token['uid']
        else:
            return "Fail"
        # username = auth

        username = str(auth.get_user(uid).display_name)
        username = ses_id
        user_match = db.users.find_one({
            "username" : username
        })
        type_u = request.args.get("type")

        if(user_match == None):
            return "Fail"
        user_info = db.users.find_one({"username": username})
        if(type_u == "borrower"):
            loan_request_id = request.args.get("loan_request_id")

            loan_request_info = db.loan_requests.find_one({"_id":ObjectId(str(loan_request_id))})
            print(loan_request_info)
            amount = loan_request_info["amount"]
            current_amount = loan_request_info["current_amount"]
            term = loan_request_info["term"]
            amount = loan_request_info["amount"]
            title = loan_request_info["title"]
            monthly_payment = loan_request_info["monthly_payment"]
            credit_rating = loan_request_info["credit_rating"]
            description = loan_request_info["description"]

            out = {"loan_request_id":loan_request_id, "current_amount":  current_amount, "amount": amount,"risk":credit_rating,"title": title, "term":term, "monthly_payment":monthly_payment, "description":description}
            return jsonify(out)
        elif(type_u == "loaner"):
            loan_payment_id = request.args.get("loan_payment_id")
            loan_payment_info = db.loan_requests.find_one({"_id":ObjectId(str(loan_payment_id))})

            user_id = loan_payment_info["user_id"]
            amount = loan_payment_info["amount"]

            out = {"loan_payment_id":loan_payment_id, "user_id":user_id, "amount":amount}
            return jsonify(out)

        return "Fail"


@server.route('/api/v1/loan_post', methods=['POST'])
def loan_post():
    if request.method == 'POST':
        user_info = request.form.to_dict()


        auth_token = str(user_info["auth_token"])
        try:
            decoded_token = auth.verify_id_token(auth_token)
        except ValueError:
            return "Fail"
        uid = decoded_token['uid']
        username = auth

        username = str(auth.get_user(uid).display_name)
        user_match = db.users.find_one({
            "username" : username
        })


        if(user_match == None):
            return "Fail"
        amount = user_info["amount"]
        interest = user_info["interest"]
        term = user_info["term"]
        title = user_info["title"]
        description = user_info["description"]
        print(description)
        credit_rating = user_info["creditrating"]
        # user_info = db.users.find_one({"username": username})

        loan_requests_insert = db.loan_requests.insert_one(
        {"amount": amount,
           "current_amount": 0,
           "interest": interest,
           "term": term,
           "title": title,
           "description": description,
           "contibutors": [],
           "credit_rating": credit_rating,
           "monthly_payment": (amount/term)*(1+interest)
        })
        loan_requests_id = loan_requests_insert.inserted_id
        db.users.update({"username": username},{"$push": {"loan_requests": str(loan_requests_id)}})
        return "Success"
@server.route('/api/v1/invest_in_loan', methods=['POST'])
def loan_post():
    if request.method == 'POST':
        user_info = request.form.to_dict()


        auth_token = str(user_info["auth_token"])
        user_match = db.users.find_one({
            "username" : auth_token
        })

        amount = user_info["amount"]
        user_id = user_info["user_id"]
        username = auth_token
        loan_request_id = request.args.get("loan_request_id")
				loan_payments_insert = db.loan_payments.insert_one(
        {
          "loan_request_id": loan_request_id
          "amount": amount,
          "user_id": user_id
        })
  			loan_payment_id = loan_payments_insert.inserted_id
        db.users.update({"username": username},{"$push": {"loan_payments": loan_payment_id}})
        db.loan_requests.update({"_id":ObjectId(str(loan_request_id))},{"$incr" : {"current_amount": amount}})
        return "Success"

@server.route('/api/v1/get_dash_data', methods=['GET'])
def get_dash_data():
    if request.method == 'GET':
        res_id = request.args.get("auth_token")


        auth_token = str(ses_id)
        decoded_token = auth.verify_id_token(auth_token)
        uid = -1
        if "uid" in decoded_token.keys():
            uid = decoded_token['uid']
        else:
            return "Fail"
        # username = auth

        username = str(auth.get_user(uid).display_name)
        user_info = db.users.find_one({"username": username})
        loan_payments = user_info["loan_payments"]
        total = 0
        for i in loan_payments:
          	total += int(db.loan_payments.find_one({"loan_payment_id": i})["amount"])
        boshal = []
        boshal2 = []
        mice = 0
        for j in range(0, 29):
            boshal.append(j)
            r = random.randint(0,5)
            boshal2.append(mice)
            mice += r
        mice = total
        boshal.append(29)
        boshal2.append(mice)
        return jsonify({"keys":boshal,
                        "values":boshal2})
@server.route('/api/v1/get_unfunded_loans', methods=['GET'])
def get_unfunded_loans():
    if request.method == 'GET':
        ses_id = request.args.get("auth_token")


        auth_token = str(ses_id)
        decoded_token = auth.verify_id_token(auth_token)
        uid = -1
        if "uid" in decoded_token.keys():
            uid = decoded_token['uid']
        else:
            return "Fail"
        # username = auth

        username = str(auth.get_user(uid).display_name)
        unfunded_loans = db.loan_requests.find({"funded": False})
        sice = []
        for block in unfunded_loans:
            amount = block["amount"]
            current_amount = block["current_amount"]
            term = block["term"]
            amount = block["amount"]
            title = block["title"]
            monthly_payment = block["monthly_payment"]
            credit_rating = block["credit_rating"]
            description = block["description"]
            sice.append({"loan_request_id":loan_request_id, "current_amount":  current_amount, "amount": amount,"risk":credit_rating,"title": title, "term":term, "monthly_payment":monthly_payment, "description":description})
        return jsonify(sice)
if __name__ == '__main__':
    server.run(host='0.0.0.0',debug=True)
