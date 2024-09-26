from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from setup import *
from forms import *
from dateutil.relativedelta import relativedelta


# TODO Make it such that by default the in budget selected is that of the current time in header link 'Current Budget'
@app.route('/')
def home():
    return render_template('index.html')


# In-memory list to store items
items = []


@app.route('/new_budget', methods=["POST", "GET"])
def budget_form():
    # TODO add a way to edit individual budgets so make a list with the budgets created have the option to edit or view
    #  button +++
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    # DONE add a check for if there is an on going budget - Added a list with made budgets that one can click on ^^^
    # TODO Make the list only show current budgets ? might not be worth it ... should potentially make it such that it
    #  skips straight to budget_view

    budget_list = db.session.query(Budgets.id, Budgets.name, Budgets.start_date, Budgets.end_date).all()
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


# DONE Make a add_budget method
@app.route('/add_recurring/<int:budget_id>', methods=['GET', 'POST'])
def input_recurring(budget_id):
    # DONE Check if there are items then add them to tables
    # TODO send budget to view ++++

    expense_query = (db.session.query(Transactions.name, Transactions.amount, Transactions.description)
                     .group_by(Transactions.name, Transactions.amount).all())
    income_query = (db.session.query(IncomeStreams.name, IncomeStreams.amount, IncomeStreams.description)
                    .group_by(IncomeStreams.name, IncomeStreams.amount).all())

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
    t = (db.session.query(IncomeStreams.name, IncomeStreams.amount)
         .where(IncomeStreams.budget_id == budget_id).all())

    print(t)

    # TODO Make monthly report page widgets include :-
    #  time to end (progress bar),
    #  in vs out (grouped bar),
    #  categories (bar)
    #  table for savings, expenses and income in the budget view

    return render_template('budget_view.html',
                           incomeChart='m',
                           # expenseChart=expense_chart.get()
                           )


# TODO Differentiate between expected income/expenses/savings and received income/expenses/savings ??
#  add a journal after evey month and budget

# TODO Make a savings db and find a way to link it


class RecurringItem:
    def __init__(self, m, d, b):
        self.budget_id = db.get_or_404(Budgets, b)
        self.start = datetime.strptime(self.budget_id.start_date, '%Y-%m')
        self.end = datetime.strptime(self.budget_id.end_date, '%Y-%m')
        self.date = d
        self.mode = m  # Todo Make users able to make weekly transactions

    def months_between(self):
        return (self.end.year - self.start.year) * 12 + (self.end.month - self.start.month)

    def make_trans(self, amount, category, description, name):
        count = 0
        current_date = self.start
        entries = []
        for _ in range(self.months_between() + 1):
            new_trans = Transactions(
                transaction_date=current_date.replace(day=self.date),  # fixme has to canotate the correct date
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
    date = request.json.get('date')
    budget_id = request.json.get('budget_id')
    description = request.json.get('description')
    recurring = request.json.get('recurring')

    if not all([amount, name, date, budget_id]):
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
        n = RecurringItem(b=budget_id, m=0, d=date)
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
            income_date=date,
            budget_id=budget_id,
        )
        db.session.add(new_income_stream)
    db.session.commit()
    return jsonify({'success': True, 'item': new_item})  # Return the new item as JSON


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
            login_user(user, remember)

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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

# DONE Make data visualizations with Matplot lib, seaborn or px- made with pychart.js
# TODO Make make it an app to with Flet
