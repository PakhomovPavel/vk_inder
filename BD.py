import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()

class User_bot(Base):
    __tablename__ = "user_bot"
    id = sq.Column(sq.Integer,primary_key=True )
    name = sq.Column(sq.String(length=40), unique=False)

    def __str__(self):
        return f' {self.id} : {self.name}'


class Search_result(Base):
    __tablename__ = "search_result"
    id_serial = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, nullable=False)
    name = sq.Column(sq.String(length=40),nullable=False)
    user_bot_id = sq.Column(sq.Integer, sq.ForeignKey("user_bot.id"), nullable=False)

    user_bot = relationship(User_bot, backref="id_1")

    def __str__(self):
        return f'{self.id_serial} : {self.id} : {self.name} : {self.user_bot_id} '


def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


