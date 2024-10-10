from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'


users = {}
appointments = {}
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        address = request.form['address']
        passport = request.form['passport']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        
        users[username] = {
            'fullname': fullname,
            'address': address,
            'passport': passport,
            'phone': phone,
            'email': email,
            'password': password
        }
        
        flash(f'Ваш логин: {username}', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user_data = users.get(username)
    if user_data and user_data['password'] == password:
        return redirect(url_for('profile', username=username))
    
    flash('Неверный логин или пароль', 'error')
    return redirect(url_for('home'))

@app.route('/profile/<username>')
def profile(username):
    user_data = users.get(username)
    user_appointments = appointments.get(username, [])
    if user_data:
        qr_data = f"ФИО: {user_data['fullname']}, Телефон: {user_data['phone']}"
        qr = qrcode.make(qr_data)
        buffered = io.BytesIO()
        qr.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        print(f"Записи для {username} при загрузке профиля: {user_appointments}")  
        return render_template('profile.html', user=user_data, qr_code=qr_base64, appointments=user_appointments)
    
    return "Пользователь не найден", 404

@app.route('/doctors')
def doctors_list_view():
    specialties = ["Терапевт", "Хирург", "Стоматолог", "Педиатр", "Ортопед"]
    return render_template('doctors_list.html', specialties=specialties)

@app.route('/doctors/<specialty>')
def doctors_list_by_specialty(specialty):
    doctors = {
        "Терапевт": ["Иванов И.И.", "Петров П.П."],
        "Хирург": ["Сидоров С.С.", "Кузнецов К.К."],
        "Стоматолог": ["Смирнова С.С.", "Орлова О.О."],
        "Педиатр": ["Николаева Н.Н.", "Федорова Ф.Ф."],
        "Ортопед": ["Коваленко А.А.", "Морозов В.В."]
    }

   
    username = request.args.get('username')  
    user_data = users.get(username) if username else None

    return render_template('doctors_by_specialty.html', specialty=specialty, doctors=doctors.get(specialty, []), user=user_data)


@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    data = request.get_json()
    username = data['username']
    doctor = data['doctor']
    date_time = data['date_time']

    if username not in appointments:
        appointments[username] = []
    
    appointments[username].append({'doctor': doctor, 'date_time': date_time})
    
    print(f"Записи для {username}: {appointments[username]}")  
    flash('Запись успешно добавлена!', 'success')
    return '', 204






if __name__ == '__main__':
    app.run(debug=True)
