from flask import render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import secrets
from __main__ import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import json
from models import *
from forms import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, func
import os
import uuid
from datetime import datetime
import time
import random
import ast
import cards

codeCharacters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
usedWordsDict = {}
playersSubmittedDict = {}
cardNumber = 0

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Player.query.get(int(user_id))

@app.route('/newCard/<code>', methods=['GET'])
def newCard(code):
    all = Player.query.all()
    players = Player.query.filter_by(roomCode=code.upper()).all()
    global cardNumber
    prompt = cards.prompts[cardNumber]
    print(prompt)
    print(cardNumber)

    cardNumber = (cardNumber + 1) % 500
    print(cardNumber)
    return render_template("index.html", logged_in=current_user.is_authenticated, user=None, players=players, roomCode=code, room=True, users=None, flip=False, prompt=prompt)

## user enters name/code to play game
@app.route('/play', methods=['POST'])
def addPlayer():
    form = JoinForm()
    answerForm = AnswerForm()
    if form.validate_on_submit():
        username = form.username.data.upper()
        roomCode = form.roomCode.data.upper()
        user = Player.query.filter_by(name=username, roomCode=roomCode).first()
        if user:
            flash("Name already taken.")
        else:
            new_user = Player(
                name = username,
                roomCode = roomCode,
                points = 0,
                answer = "",
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            # go to main page, but display only answer field and submit button (or go to different page)
            return render_template("index.html", logged_in=current_user.is_authenticated, user=current_user, room=False, answerForm=answerForm)
    return render_template("index.html", logged_in=False, user=None, room=False)

# user clicks to join, sees screen to enter name
@app.route('/join', methods=['POST', 'GET'])
def joinGame():
    form = JoinForm()
    return render_template("index.html",form=form, logged_in=False, user=None, room=False, join=True)

# host clicks to get roomcode
@app.route('/roomcode', methods=['GET'])
def generateRoomCode():
    code = ""
    for x in range(5):
        code += codeCharacters[random.randint(0,1039) % 26]
    return render_template("index.html", code=code, logged_in=current_user.is_authenticated, user=None, room=False)

# create room after getting code
@app.route('/room/<code>', methods=['POST', 'GET'])
def createRoom(code):
    all = Player.query.all()
    players = Player.query.filter_by(roomCode=code.upper()).all()
    print(players)
    for player in all:
        print(player.roomCode)
    return render_template("index.html", logged_in=current_user.is_authenticated, user=None, players=players, roomCode=code, room=True, users=None)

# homepage
@app.route('/home', methods=['POST', 'GET'])
def homePage():
    return render_template("index.html", logged_in=current_user.is_authenticated, user=None, roomCode=None, room=False, users=None)

@app.route('/', methods=['POST', 'GET'])
def landing():
    return render_template("index.html", logged_in=current_user.is_authenticated, user=None, roomCode=None, room=False, users=None)

# user enters their answer
@app.route('/answer', methods=['POST'])
@login_required
def submitAnswer():
    form = AnswerForm()
    if form.validate_on_submit():
        answer = form.answer.data
        user = current_user
        user.answer = answer
        db.session.commit()
        form.answer.data = ""
    return render_template("index.html", logged_in=current_user.is_authenticated, user=current_user, room=False, answerForm=form)

#manually change points
@app.route('/adjust/<code>/<id>/<add>', methods=['GET', 'POST'])
def adjustPoints(code, id, add):
    player = Player.query.filter_by(roomCode=code, id=id).first()
    players = Player.query.filter_by(roomCode=code).order_by(Player.id).all()
    if add == "True":
        player.points += 1
    else:
        player.points -= 1
    db.session.commit()
    return render_template("index.html", logged_in=current_user.is_authenticated, user=None, room=True, roomCode=code, users=None, players=players, flip = False)

#delete all points and answers
@app.route('/newGame/<code>', methods=['GET', 'POST'])
def newGame(code):
    players = Player.query.filter_by(roomCode=code).order_by(Player.id).all()
    for player in players:
        player.points= 0
        player.answer=""
    db.session.commit()
    return render_template("index.html", logged_in=current_user.is_authenticated, user=None, room=True, roomCode=code, users=None, players=players, flip = True)

#manually change points
@app.route('/done/<code>', methods=['GET', 'POST'])
def done(code):
    players = Player.query.filter_by(roomCode=code).order_by(Player.id).all()
    for player in players:
        db.session.delete(player)
    db.session.commit()
    return render_template("index.html", logged_in=current_user.is_authenticated, user=None, roomCode=None, room=False, users=None)

@app.route('/allUsers', methods=['GET'])
def allUsers():
    players = Player.query.all()
    for player in players:
        print(player)
    return "hi"

@app.route('/delete/every/single/player', methods=['GET'])
def deleteAll():
    players = Player.query.all()
    for player in players:
        db.session.delete(player)
    db.session.commit()
    return "Secret page... You probably shouldn't be here..."

#flip user anwers and display points
@app.route('/flip/<code>', methods=['GET'])
def flipAnswers(code):
    playerDict = {}
    players = Player.query.filter_by(roomCode=code).order_by(Player.id).all()
    for player in players:
        if player.answer.upper() in playerDict:
            playerDict[player.answer.upper()].append(player)
        else:
            playerDict[player.answer.upper()] = [player]
        
    print(playerDict)
    for k in playerDict:
        print(playerDict)
        if len(playerDict[k]) == 2 and len(k) > 0:
            for player in playerDict[k]:
                player.points += 3
        elif len(playerDict[k]) > 2 and len(k) > 0:
            for player in playerDict[k]:
                player.points += 1
    db.session.commit()
    maxPoints = 19
    winner = []
    for player in players:
        if player.points > maxPoints:
            maxPoints = player.points
    if maxPoints > 19:
        for player in players:
            if player.points == maxPoints:
                winner.append(player.name)
        if len(winner) > 1:
            return render_template("index.html", logged_in=current_user.is_authenticated, user=None, room=True, roomCode=code, users=None, players=players, flip = True, winners=winner)
        elif len(winner) > 0:
            return render_template("index.html", logged_in=current_user.is_authenticated, user=None, room=True, roomCode=code, users=None, players=players, flip = True, winner=winner[0])
    return render_template("index.html", logged_in=current_user.is_authenticated, user=None, room=True, roomCode=code, users=None, players=players, flip = True)
