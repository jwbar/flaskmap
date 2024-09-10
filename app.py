from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from flask_session import Session

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Use a strong secret key for session security

# Configure server-side session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# MongoDB connection
try:
    client = MongoClient('mongodb://127.0.0.1:27017/')
    db = client.lettekiez
    collection = db.seite
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Helper function to get content from the database
def get_content(page_name):
    try:
        content = collection.find_one({'seitenamen': page_name})
        if content:
            title = content.get('title', f'{page_name.capitalize()} Coming')
            text = content.get('text', 'Content coming soon.')
            bild = content.get('bild', '')
        else:
            title = f'{page_name.capitalize()} Coming'
            text = 'Content coming soon.'
            bild = ''
    except Exception as e:
        print(f"Error fetching content for {page_name}: {e}")
        title, text, bild = f'{page_name.capitalize()} Coming', 'Content coming soon.', ''
    return title, text, bild

@app.route('/')
def karte():
    title, text, bild = get_content('karte')
    return render_template('index.html', title=title, text=text, bild=bild)

@app.route('/yoga')
def yoga():
    title, text, bild = get_content('yoga')
    return render_template('yoga.html', title=title, text=text, bild=bild)

@app.route('/kyoga')
def kyoga():
    title, text, bild = get_content('kyoga')
    return render_template('kyoga.html', title=title, text=text, bild=bild)

@app.route('/garten')
def garten():
    title, text, bild = get_content('garten')
    return render_template('garten.html', title=title, text=text, bild=bild)

@app.route('/home')
def home():
    title, text, bild = get_content('home')
    return render_template('home.html', title=title, text=text, bild=bild)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add authentication logic here
        if username == 'admin' and password == 'password':  # Simple check
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
    return render_template('admin.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('admin'))
    return render_template('admin_dashboard.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin'))


@app.route('/edit/<seitenamen>', methods=['GET', 'POST'])
def edit_content(seitenamen):
    if 'logged_in' not in session:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        bild = request.form['bild']
        try:
            collection.update_one(
                {'seitenamen': seitenamen},
                {'$set': {'title': title, 'text': text, 'bild': bild}},
                upsert=True
            )
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            print(f"Error updating content for {seitenamen}: {e}")
    else:
        content = collection.find_one({'seitenamen': seitenamen})
        if content:
            title = content.get('title', '')
            text = content.get('text', '')
            bild = content.get('bild', '')
        else:
            title = ''
            text = ''
            bild = ''
        return render_template('edit_content.html', seitenamen=seitenamen, title=title, text=text, bild=bild)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
