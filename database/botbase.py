from datetime import datetime

from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, DateField


db = SqliteDatabase('bot_database.db')


class BaseModel(Model):
    created_at = DateField(default=datetime.now())

    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField(null=True)
    first_name = CharField()
    last_name = CharField(null=True)


class TicketsInfo(BaseModel):
    user = ForeignKeyField(User, backref="requests")
    origin = CharField()
    origin_iata = CharField(null=True)
    destination = CharField()
    destination_iata = CharField(null=True)
    depart_date = DateField()
    return_date = DateField(null=True)


def create_models():
    db.create_tables(BaseModel.__subclasses__())


if __name__ == '__main__':
    create_models()
