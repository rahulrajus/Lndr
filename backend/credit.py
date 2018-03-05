import requests
from flask import Flask, request, jsonify, json, Response
from flask import render_template
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

server = Flask(__name__)
a = {}
with open("out.txt", "r") as f:
    for line in f:
        lolz = line.split(",")
        a.update({lolz[0]: int(lolz[1])})

@server.route('/api/v1/withdraw', methods=['GET'])
def withdraw():
    global a
    amount = request.args.get("amount")
    user1 = request.args.get("user1")
    user2 = request.args.get("user2")
    a[user1] -= int(amount)
    a[user2] += int(amount)
    f = open("out2.txt", "w")
    f.write(str(a["aneesh"]) + "," + str(a["Rahul"]) + "," + str(a["sid"]))
    return "success"

@server.route('/api/v1/status', methods=['GET'])
def status():
    global a
    return (str(a["aneesh"]) + "," + str(a["Rahul"]) + "," + str(a["sid"]))



server.run(host='0.0.0.0',debug=True)
