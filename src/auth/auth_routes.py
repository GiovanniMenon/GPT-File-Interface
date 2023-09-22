from flask import Blueprint, render_template, redirect, url_for, request 
from flask_login import login_user
from src.user_model import User


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            return render_template('login.html', error=True)

    return render_template('login.html')


