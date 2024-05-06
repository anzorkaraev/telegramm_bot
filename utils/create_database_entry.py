from datetime import date

from database.botbase import TicketsInfo


def database_entry(user: int, orig: str, orig_i: str, dest: str, dest_i: str, dep_date: date, ret_date: date):
    TicketsInfo.create(
        user_id=user,
        origin=orig,
        origin_iata=orig_i,
        destination=dest,
        destination_iata=dest_i,
        depart_date=dep_date,
        return_date=ret_date
    )
