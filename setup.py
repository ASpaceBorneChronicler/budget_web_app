from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, joinedload
from sqlalchemy.future import select
from sqlalchemy import Integer, String, Float, Date, ForeignKey, extract
from datetime import date
from flask_migrate import Migrate
# DONE Merge this and app setup
from flask import Flask,  session
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, UserMixin
from datetime import timedelta

# DONE Make a Flask App - done
app = Flask(__name__)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['SECRET_KEY'] = '1234567890'
Bootstrap5(app)

# DONE Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users, user_id)


# DONE Make SQLAlchemy database- done
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///my_database.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# DONE Create db tables
class Users(db.Model, UserMixin):
    __tablename__ = "Users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    budgets: Mapped['Budgets'] = relationship('Budgets', back_populates='user', cascade='all,delete-orphan')


class Budgets(db.Model):
    __tablename__ = 'Budgets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    # total_amount_budgeted: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[str] = mapped_column(String(30), nullable=False)
    end_date: Mapped[str] = mapped_column(String(30), nullable=False)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'), nullable=False)

    # Relationships
    user: Mapped['Users'] = relationship(Users, back_populates='budgets')
    savings: Mapped[list['Savings']] = relationship(
        "Savings",
        back_populates="budget",
        cascade="all, delete-orphan")
    transactions: Mapped[list['Transactions']] = relationship(
        "Transactions",
        back_populates="budget",
        cascade="all, delete-orphan")
    income: Mapped[list['IncomeStreams']] = relationship(
        "IncomeStreams",
        back_populates="budget",
        cascade="all, delete-orphan")


class IncomeStreams(db.Model):
    __tablename__ = 'Income'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    income_date: Mapped[str] = mapped_column(String(), nullable=False)

    # Foreign key
    budget_id: Mapped[int] = mapped_column(ForeignKey('Budgets.id'))

    # Relationships
    budget: Mapped['Budgets'] = relationship("Budgets", back_populates="income")


class Transactions(db.Model):
    __tablename__ = 'Transactions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(250), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(275), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    # transaction_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Foreign keys
    budget_id: Mapped[int] = mapped_column(ForeignKey('Budgets.id'))

    # Relationships
    budget: Mapped['Budgets'] = relationship("Budgets", back_populates="transactions")


class Savings(db.Model):
    __tablename__='Savings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(275), nullable=True)
    savings_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Foreign keys
    budget_id: Mapped[int] = mapped_column(ForeignKey('Budgets.id'))

    # Relationships
    budget: Mapped['Budgets'] = relationship("Budgets", back_populates="savings")


with app.app_context():
    db.create_all()
migrate = Migrate(app, db)

# class Categories(db.Model):
#     __tablename__ = "Categories"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     allocated_amount: Mapped[float] = mapped_column(Float, nullable=False)
#
#     # user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'), nullable=False)
# budget_id: Mapped[int] = mapped_column(ForeignKey('Budgets.id'), nullable=False)
