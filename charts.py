from pychartjs import BaseChart, ChartType, Color
from setup import app, db, IncomeStreams, Transactions


def fetch_income(budget_id):
    with app.app_context():
        data = [{'id': str(row.name), 'nested': {'value': str(row.amount)}} for row in
                db.session.query(IncomeStreams.name, IncomeStreams.amount
                                 ).where(IncomeStreams.budget_id == budget_id).group_by(IncomeStreams.name,
                                                                                        IncomeStreams.amount).all()]
        labels = [str(row.name) for row in db.session.query(IncomeStreams.name, IncomeStreams.amount).group_by(
            IncomeStreams.name, IncomeStreams.amount).all()]

        return [data, labels]


def fetch_expenses(budget_id):
    pass


class IncomeDonut(BaseChart):
    type = ChartType.Doughnut

    class data:
        data = fetch_income()[0]

    class labels:
        data = fetch_income()[1]

    class options:
        parsing = {'key': 'nested.value'}
        aspectRatio = 564 / 238
        responsive = True
        padding = 25

    class pluginOptions:
        legend = {
            'position': 'right',

        }
        title = {
            'display': True,
            'text': 'Distribution of income',
            'position': 'top',
            'font': {'weight': 'normal',
                     'size': 16,
                     },
            'align': 'start',
        }


class ExpenseDonut(BaseChart):
    type = ChartType.Doughnut

    class data:
        with app.app_context():
            data = [{'id': str(row.name), 'nested': {'value': str(row.amount)}} for row in
                    db.session.query(Transactions.name, Transactions.amount
                                     ).group_by(Transactions.name, Transactions.amount).all()]
        # backgroundColor = 'transparent',
        # borderColor = '#007bff',
        # borderWidth = 4,

    class labels:
        with app.app_context():
            # TODO maybe make the db query a function that returns the same ?
            data = [str(row.name) for row in db.session.query(Transactions.name, Transactions.amount).group_by(
                Transactions.name, Transactions.amount).all()]

    class options:
        parsing = {'key': 'nested.value'}
        aspectRatio = 564 / 238
        responsive = True
        padding = 25

    class pluginOptions:
        legend = {
            'position': 'right',

        }
        title = {
            'align': 'start',
            'display': True,
            'position': 'top',
            'font': {'weight': 'normal',
                     'size': 16,
                     },
            'text': 'Distribution of expenses',
        }

