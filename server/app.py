#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')
        
        if not username:
            return {'error': 'Username is required'}, 422
        
        if not password:
            return {'error': 'Password is required'}, 422
        
        try:
            user = User(
                username=username,
                image_url=image_url,
                bio=bio
            )
            user.password_hash = password
            
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            
            return user.to_dict(), 201
            
        except IntegrityError:
            return {'error': 'Username already exists'}, 422
        except ValueError as e:
            return {'error': str(e)}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                return user.to_dict(), 200
        
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter(User.username == username).first()
        
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        
        if user_id:
            session['user_id'] = None
            return {}, 204
        
        return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        user = User.query.filter(User.id == user_id).first()
        if not user:
            return {'error': 'User not found'}, 401
        
        recipes = [recipe.to_dict() for recipe in user.recipes]
        return recipes, 200
    
    def post(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        data = request.get_json()
        
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')
        
        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )
            
            db.session.add(recipe)
            db.session.commit()
            
            return recipe.to_dict(), 201
            
        except ValueError as e:
            return {'error': str(e)}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)