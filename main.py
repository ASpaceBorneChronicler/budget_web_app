from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, g
from flask_login import login_user, current_user, logout_user, user_logged_in
from werkzeug.security import generate_password_hash, check_password_hash
from setup import *
from icecream import ic
from forms import *
from dateutil.relativedelta import relativedelta


# TODO Make it such that by default the in budget selected is that of the current time in header link 'Current Budget'
@app.route('/')
def home():
    if current_user.is_authenticated:
        budget_list = (db.session.query(Budgets.id, Budgets.name, Budgets.start_date, Budgets.end_date)
                       .where(Budgets.user_id == current_user.id).all())
        budget_list = [{'id': id, 'name': name, 'start_date': start, 'end_date': end}
                       for id, name, start, end in budget_list]
        ic(current_user)
        return render_template('index.html', budget_list=budget_list)
    return render_template('index.html')


# Registration, Login and logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # form = LoginForm()
    if request.method == "POST":
        form = request.form
        password = form['password']
        email = form['email']
        remember = 'remember' in form
        result = db.session.execute(db.select(Users).where(Users.email == email))

        user = result.scalar()

        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))

        # Password incorrect
        elif not check_password_hash(user.password_hash, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=remember)
            return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/sign-up', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        remember = 'remember_me' in form
        # print(form)
        # print(form['check'])

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(Users).where(Users.email == form['email']))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form['password'],
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = Users(
            username=form['username'],
            email=form['email'],
            password_hash=hash_and_salted_password,
            created_at=date.today()
        )
        db.session.add(new_user)
        db.session.commit()

        # This line will authenticate the user with Flask-Login
        login_user(new_user, remember=remember)
        return redirect(url_for("home"))
    return render_template('register.html')


# In-memory list to store items


items = []


# DONE Make a add_budget method


@app.route('/new_budget', methods=["POST", "GET"])
def budget_form():
    # TODO add a way to edit individual budgets so make a list with the budgets created have the option to edit or view
    #  button +++
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    # DONE add a check for if there is an on going budget - Added a list with made budgets that one can click on ^^^
    # TODO Make the list only show current budgets ? might not be worth it ... should potentially make it such that it
    #  skips straight to budget_view

    budget_list = (db.session.query(Budgets.id, Budgets.name, Budgets.start_date, Budgets.end_date)
                   .where(Budgets.user_id == current_user.id).all())
    budget_list = [{'id': id, 'name': name, 'start_date': start, 'end_date': end}
                   for id, name, start, end in budget_list]
    # print(budget_list)
    form = BudgetCreation()
    if request.method == "POST":
        budget = request.form
        new_budget = Budgets(
            name=budget['name'],
            start_date=budget['start_month'],
            end_date=budget['end_month'],
            user_id=current_user.id
        )
        db.session.add(new_budget)
        db.session.commit()
        budget_id = new_budget.id
        return redirect(url_for('input_recurring', budget_id=budget_id))

    return render_template('make_budget.html', form=form, budget_list=budget_list)


# TODO Differentiate between expected income/expenses/savings and received income/expenses/savings ??
#  add a journal after evey month and budget

# TODO Make a savings db and find a way to link it


@app.route('/add_recurring/<int:budget_id>', methods=['GET', 'POST'])
def input_recurring(budget_id):
    # DONE Check if there are items then add them to tables
    # TODO send budget to view ++++

    expense_query = (db.session.query(Transactions.name, Transactions.amount, Transactions.description)
                     .where(Transactions.budget_id == budget_id)
                     .group_by(Transactions.name, Transactions.amount)
                     .all())
    income_query = (db.session.query(IncomeStreams.name, IncomeStreams.amount, IncomeStreams.description)
                    .where(Transactions.budget_id == budget_id)
                    .group_by(IncomeStreams.name, IncomeStreams.amount)
                    .all())

    expense_query = [{'name': row.name, 'amount': row.amount, 'description': row.description} for row in
                     expense_query]
    income_query = [{'name': row.name, 'amount': row.amount, 'description': row.description} for row in
                    income_query]

    return render_template('input_recurring.html',
                           income={},
                           currency='KSH',
                           expenses=expense_query,
                           incomes=income_query,
                           budget_id=budget_id,
                           )


@app.route('/budget_dashboard/<int:budget_id>')
def budget_view(budget_id):
    month = date.today().month
    result = (db.session.query(IncomeStreams.name, IncomeStreams.amount)
              .where(IncomeStreams.budget_id == budget_id)
              .all())
    labels_i = [x.name for x in result]
    data_i = [{'id': str(x.name), 'nested': {'value': str(x.amount)}} for x in result]

    result2 = (db.session.query(Transactions.name, Transactions.amount)
               .where(Transactions.budget_id == budget_id, extract('month', Transactions.transaction_date) == month)
               .all())
    labels_t = [x.name for x in result2]
    data_t = [{'id': str(x.name), 'nested': {'value': str(x.amount)}} for x in result2]

    # TODO Make monthly report page widgets include :-
    #  time to end (progress bar),
    #  in vs out (grouped bar),
    #  categories (bar)
    #  table for savings, expenses and income in the budget view
    # url_for('jxjsjs',)
    return render_template('dashboard.html',
                           incomeChart={'labels': labels_i, 'datasets': data_i},
                           expenseChart={'labels': labels_t, 'datasets': data_t},
                           budget_id=budget_id
                           )


@app.route('/income_view/<int:budget_id>')
def income_view(budget_id):
    today = datetime.today()
    t_day = today.day
    # Get the total number of days in the current month
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day_of_month = next_month - timedelta(days=next_month.day)

    month_name = today.strftime("%B")
    total_days_in_month = last_day_of_month.day
    current_day_of_month = today.day

    # Calculate the percentage of the month that has passed
    percentage = round(((current_day_of_month / total_days_in_month) * 100), 1)
    return render_template('income.html',
                           budget_id=budget_id,
                           prog=percentage,
                           last_day=last_day_of_month.day,
                           today=t_day,
                           user_first=current_user.username,
                           month_name=month_name
                           )


@app.route('/savings_view/<int:budget_id>')
def savings_view(budget_id):
    today = datetime.today()
    t_day = today.day
    # Get the total number of days in the current month
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day_of_month = next_month - timedelta(days=next_month.day)

    month_name = today.strftime("%B")
    total_days_in_month = last_day_of_month.day
    current_day_of_month = today.day

    # Calculate the percentage of the month that has passed
    percentage = round(((current_day_of_month / total_days_in_month) * 100), 1)
    return render_template('savings.html',
                           budget_id=budget_id,
                           prog=percentage,
                           last_day=last_day_of_month.day,
                           today=t_day,
                           user_first=current_user.username,
                           month_name=month_name
                           )


@app.route('/expense_view/<int:budget_id>')
def expense_view(budget_id):
    today = datetime.today()
    t_day = today.day
    # Get the total number of days in the current month
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day_of_month = next_month - timedelta(days=next_month.day)

    month_name = today.strftime("%B")
    total_days_in_month = last_day_of_month.day
    current_day_of_month = today.day

    # Calculate the percentage of the month that has passed
    percentage = round(((current_day_of_month / total_days_in_month) * 100), 1)
    return render_template('expense.html',
                           budget_id=budget_id,
                           prog=percentage,
                           last_day=last_day_of_month.day,
                           today=t_day,
                           user_first=current_user.username,
                           month_name=month_name
                           )


#
class RecurringItem:

    def __init__(self, m, d, b):
        self.budget_id = db.get_or_404(Budgets, b)
        self.start = datetime.strptime(self.budget_id.start_date, '%Y-%m')
        self.end = datetime.strptime(self.budget_id.end_date, '%Y-%m')
        self.date = int(d)
        self.mode = m  # Todo Make users able to make weekly transactions

    def months_between(self):
        return (self.end.year - self.start.year) * 12 + (self.end.month - self.start.month)

    def make_trans(self, amount, category, description, name):
        count = 0
        current_date = self.start
        entries = []
        for _ in range(self.months_between() + 1):
            new_trans = Transactions(
                transaction_date=current_date.replace(day=self.date),  # DONE has to input the correct date
                name=name,
                amount=amount,
                description=description,
                category=category,
                budget_id=self.budget_id.id
            )
            entries.append(new_trans)
            current_date += relativedelta(months=1)
            count += 1
        return entries

    def make_inc(self, amount, description, name):
        count = 0
        current_date = self.start
        entries = []
        for _ in range(self.months_between() + 1):
            new_incs = IncomeStreams(
                income_date=current_date.replace(day=self.date),  # DONE has to replace 'day' with date the correct date
                name=name,
                amount=amount,
                description=description,
                budget_id=self.budget_id.id
            )
            entries.append(new_incs)
            current_date += relativedelta(months=1)
            count += 1
        return entries


# Done Make the class return a list of db objects


@app.route("/create_transaction", methods=['POST', 'GET'])
def create_transaction_r():
    """
    This route collects the data from the json sent and tries to
    add it to the database then returns the new item in a json
    """
    data = request.get_json()

    description = data.get('description')
    name = data.get("name")
    category = data.get("category")  # Todo Make the category have a dropdown with the option to add a new category
    date = data.get("date")
    amount = data.get("amount")
    budget_id = data.get("budget_id")
    recurring = data.get('recurring')

    if not all([amount, category, name, date, budget_id]):
        return jsonify({"error": False}), 400
    new_item = {
        'name': name,
        'amount': amount,
        'description': description
    }
    if recurring:
        n = RecurringItem(b=budget_id, m=0, d=date)
        # TODO m should tell us if we are ment to add entries monthly or weekly
        db.session.add_all(
            n.make_trans(amount=amount,
                         category=category,
                         description=description,
                         name=name
                         )
        )
    else:
        new_trans = Transactions(
            transaction_date=date,
            amount=amount,
            category=category,
            budget_id=budget_id,
            description=description,
        )
        db.session.add(new_trans)

    db.session.commit()

    return jsonify({'success': True, 'item': new_item}), 201


@app.route('/add_income', methods=['POST'])
def add_income():
    # Fetch the fields from the JSON request
    amount = request.json.get('amount')
    name = request.json.get('name')
    date_i = request.json.get('date')
    budget_id = request.json.get('budget_id')
    description = request.json.get('description')
    recurring = request.json.get('recurring')

    if not all([amount, name, date_i, budget_id]):
        # TODO make this a flash message somehow or handle validation in the front
        return jsonify({"error": False}), 400
    # Append the new item as a dictionary
    new_item = {
        'name': name,
        'amount': amount,
        'description': description
    }
    items.append(new_item)
    if recurring:
        n = RecurringItem(b=budget_id, m=0, d=date_i)
        # TODO m should tell us if we are ment to add entries monthly or weekly
        db.session.add_all(
            n.make_inc(amount=amount,
                       description=description,
                       name=name,
                       )
        )
    else:
        new_income_stream = IncomeStreams(
            amount=amount,
            name=name,
            description=description,
            income_date=date_i,
            budget_id=budget_id,
        )
        db.session.add(new_income_stream)
    db.session.commit()
    return jsonify({'success': True, 'item': new_item})  # Return the new item as JSON


if __name__ == "__main__":
    app.run(debug=True)

# DONE Make data visualizations with Matplot lib, seaborn or px- made with pychart.js
# TODO Make make it an app to with Flet ?
