from app import app, db
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from app.models import User, Character
import requests
import hashlib


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email.lower()).first()
        if user is None or not user.check_password(password):
            flash('invalid e-mail or password', 'danger')
            return redirect(request.referrer)
        flash('login successful!', 'success')    
        login_user(user)
        return redirect(url_for('profile'))
    return render_template('authentication/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data.get('email')).first()
        if user is not None:
            flash('an account associated with your e-mail is already on file', 'warning')
            return redirect(request.referrer)
        if data.get('password') != data.get('password2'):
            flash('passwords do not match!', 'warning')
            return redirect(request.referrer)
        new_user = User(
            name =data.get('name'),
            email=data.get('email'),
            password=data.get('password')
        )
        db.session.add(new_user)
        db.session.commit()

        flash('registration successful! - you are now logged in', 'success')
        login_user(new_user)
        return redirect(url_for('profile'))
    return render_template('authentication/register.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('successfully logged out', 'primary')
    return render_template('home.html')

@app.route('/profile')
def profile():
    heroes = Character.query.filter_by(user_id=current_user.id).all()
    collection = [] 
    for h in heroes:
            heroes_dict = {
            'name': h.name,
            'description': h.description,
            'image': h.image
            }
            collection.append(heroes_dict)
    context = {
        'heroes': collection
    }

    return render_template('profile.html', **context)


def hero_selection(hero):
    hash = '123'+'70f69b5d693311250448678613459545138553f4'+'a210202d0c751a3a4ad95cfa8d6fe5f6'
    api_link = f'http://gateway.marvel.com/v1/public/characters?name={hero}&ts=123&apikey=a210202d0c751a3a4ad95cfa8d6fe5f6&hash={(hashlib.md5(hash.encode())).hexdigest()}'
    info = requests.get(api_link).json()
    return info


@app.route('/choose', methods=['GET', 'POST'])
def choose():
    if request.method == 'POST':
        try:
            chosen = request.form.get('chosen')
            result = hero_selection(chosen)
            new_character = Character(
                name =result['data']['results'][0]['name'],
                description=result['data']['results'][0]['description'],
                comics_appeared_in=result['data']['results'][0]['comics']['available'],
                image = result['data']['results'][0]['thumbnail']['path'],
                user_id=current_user.id)
        except:
            flash('that hero does not exist - please try again', 'warning')
            return redirect(request.referrer)

        context = {
            'name': new_character.name,
            'description': new_character.description,
            'comics': new_character.comics_appeared_in,
            'image': new_character.image
        }
        return render_template('current_hero.html', **context)
    return render_template('choose.html')

@app.route('/hero/add/<name>')
def add(name):

    result = hero_selection(name)
    new_character = Character(
        name =result['data']['results'][0]['name'],
        description=result['data']['results'][0]['description'],
        comics_appeared_in=result['data']['results'][0]['comics']['available'],
        image = result['data']['results'][0]['thumbnail']['path'],
        user_id=current_user.id)

    hero_to_add = Character.query.filter_by(name=new_character.name).filter_by(user_id=current_user.id).first()
    if hero_to_add:
        flash('that hero is already in your collection!', 'warning')
        return redirect(url_for('choose'))
    else:
        db.session.add(new_character)
        db.session.commit()
    return redirect(url_for('profile'))
    

@app.route('/products/hero/<name>')
def remove_hero(name):
    dead_hero = Character.query.filter_by(name=name).filter_by(user_id=current_user.id).first()
    db.session.delete(dead_hero)
    db.session.commit()
    flash(f'hero removed from collection', 'success')
    return redirect(url_for('profile'))
