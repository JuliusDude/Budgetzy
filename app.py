# Imports 
from flask import Flask,redirect,render_template,request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
from flask_wtf.csrf import CSRFProtect




# My app
load_dotenv() 
app = Flask(__name__)



csrf = CSRFProtect(app)
Scss(app, static_dir='static',asset_dir='static/scss')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)




class MyTask(db.Model):
    log_id = db.Column(db.Integer, primary_key=True)
    cash = db.Column(db.Integer, default=0)
    cash_type = db.Column(db.String(100), default="debit")
    desc = db.Column(db.String(100), default="")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Task {self.log_id}"

    
#home 
@app.route("/", methods=["POST","GET"])
def index():
    if request.method == "POST":
        cash = request.form['cash']
        cash_type = request.form['cash_type']
        desc = request.form['desc']
        new_task = MyTask(cash= cash, cash_type=cash_type,desc=desc)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"Error :{e}")
            return f"Error {e}"
    else:        
        tasks = MyTask.query.order_by(MyTask.date_created).all()
        '''balance = db.session.query(
            db.func.sum(
            db.case(
                [(MyTask.cash_type == 'credit', MyTask.cash)],
                else_=-MyTask.cash
            )
            )
        ).scalar() or 0
        '''
        # Calculate balance
        balance = 0
        for task in tasks:
            if task.cash_type.lower() == "credit":
                balance += task.cash
            else:  # debit
                balance -= task.cash
        return render_template("index.html", tasks=tasks, balance=balance)



#Delete 

@app.route("/delete/<int:log_id>")
def delete(log_id:int):
    delete_log = MyTask.query.get_or_404(log_id)
    try:
        db.session.delete(delete_log)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"ERROR: {e}"


# Edit an item 
@app.route("/edit/<int:log_id>",methods=["GET","POST"])
def edit(log_id:int):
    print("working")
    task = MyTask.query.get_or_404(log_id)
    if request.method == "POST":
        cash = request.form['cash']
        cash_type = request.form['cash_type']
        desc = request.form['desc']
        task.cash = cash
        task.cash_type = cash_type
        task.desc = desc
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Error: {e}"
    else:
        return render_template('edit.html',task=task)


#STATS
@app.route("/stats")
def stat():
    tasks = MyTask.query.order_by(MyTask.date_created).all()
    totalTransaction = credit = debit = 0
    balance = 0
    for task in tasks:
        if task.cash_type.lower() == "credit":
            credit+= task.cash
        else:  # debit
            debit += task.cash
    totalTransaction = credit + debit
    balance = credit - debit

    return render_template('stats.html',totalTransaction=totalTransaction, credit=credit, debit= debit, balance=balance)





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)