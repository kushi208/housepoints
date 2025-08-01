from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

TEACHER_PASSWORD = os.getenv('TEACHER_PASSWORD', 'svteacher123')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'svadmin123')

class HousePoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, nullable=False)

def init_db():
    db.create_all()
    houses = ['Blue', 'Green', 'Orange', 'Red']
    for house in houses:
        if not HousePoints.query.filter_by(house=house).first():
            db.session.add(HousePoints(house=house, points=0))
    db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('teacher_login'))

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        if request.form['password'] == TEACHER_PASSWORD:
            session['teacher'] = True
            return redirect(url_for('teacher_dashboard'))
    return render_template('teacher_login.html')

@app.route('/teacher_dashboard', methods=['GET', 'POST'])
def teacher_dashboard():
    if 'teacher' not in session:
        return redirect(url_for('teacher_login'))
    houses = HousePoints.query.all()
    if request.method == 'POST':
        house = request.form['house']
        points = int(request.form['points'])
        entry = HousePoints.query.filter_by(house=house).first()
        entry.points += points
        db.session.commit()
    return render_template('teacher_dashboard.html', houses=houses)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    houses = HousePoints.query.order_by(HousePoints.points.desc()).all()
    return render_template('admin_dashboard.html', houses=houses)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
