from os.path import join
from xml.etree import ElementTree
import argparse
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gd import parser
from gd import database
from gd.models import Base
from gd.models import (Action, AtBat, Game, Player, Pitch, Stadium,
                       Team, Umpire)


ROOT = "/Users/brian/dev/gd/2014_data/gd2.mlb.com/components/game/mlb/year_2014/"


def add_teams(session, teams):
    query = session.query(Team.id)
    for team in teams:
        if query.filter(Team.id.is_(int(team["id"]))).scalar() is None:
            session.add(Team(**team))


def add_players(session, players):
    query = session.query(Player.id)
    for player in players:
        if query.filter(Player.id.is_(int(player["id"]))).scalar() is None:
            session.add(Player(**player))


def add_umpire(session, umpire):
    query = session.query(Umpire.id)
    if query.filter(Umpire.id.is_(int(umpire["id"]))).scalar() is None:
        session.add(Umpire(**umpire))


def add_stadium(session, stadium):
    query = session.query(Stadium.id)
    if query.filter(Stadium.id.is_(int(stadium["id"]))).scalar() is None:
        session.add(Stadium(**stadium))


def add_game(session, game):
    query = session.query(Game.game_pk)
    if query.filter(
        Game.game_pk.is_(int(game["game_pk"]))).scalar() is None:
        session.add(Game(**game))


def do_initdb(args):
    database.init()


def do_import(args):
    engine = database.engine

    for root, dirs, files in os.walk(args.root):
        game_path = join(root, "game.xml")
        inning_path = join(root, "inning/inning_all.xml")
        player_path = join(root, "players.xml")

        exist = [os.path.exists(x) for x in [game_path, inning_path,
                                             player_path]]
        if not all(exist):
            continue

        with open(game_path, "r") as game_file:
            game_tree = ElementTree.fromstring(game_file.read())
        with open(inning_path, "r") as inning_file:
            inning_tree = ElementTree.fromstring(inning_file.read())
        with open(player_path, "r") as player_file:
            player_tree = ElementTree.fromstring(player_file.read())

        date = parser.get_date(player_tree)
        teams = list(parser.get_teams(game_tree))
        players = parser.get_players(player_tree)
        plate_umpire = parser.get_plate_umpire(player_tree)
        stadium = parser.get_stadium(game_tree)
        game = parser.get_game(game_tree)
        atbats = list(parser.get_atbats(inning_tree))
        pitches = list(parser.get_pitches(inning_tree))
        actions = list(parser.get_actions(inning_tree))

        # Skip spring training and exhibition games since they won't have
        # any data, and I've also seen players in these games with non-unique
        # player IDs. Just forget that...
        if game["type"] in ("S", "E"):
            continue

        add_teams(database.session, teams)
        add_players(database.session, players)
        add_umpire(database.session, plate_umpire)
        add_stadium(database.session, stadium)

        # This home/away determination is risky depending on ordering,
        # but every game I've looked at has worked this way.
        game["date"] = date
        game["home_team"] = teams[0]["id"]
        game["away_team"] = teams[1]["id"]
        game["stadium"] = stadium["id"]
        game["umpire_id"] = plate_umpire["id"]
        add_game(database.session, game)

        for action in actions:
            action["game_pk"] = game["game_pk"]
        database.session.add_all([Action(**action) for action in actions])

        for atbat in atbats:
            atbat["game_pk"] = game["game_pk"]
        database.session.add_all([AtBat(**atbat) for atbat in atbats])

        for pitch in pitches:
            pitch["game_pk"] = game["game_pk"]
        # HBPs don't seem to have anything in them, so skip 'em
        pitches = [p for p in pitches if p["des"] != "Hit By Pitch"]
        database.session.add_all([Pitch(**pitch) for pitch in pitches])

        database.session.commit()


def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser("initdb")
    init_parser.set_defaults(func=do_initdb)

    import_parser = subparsers.add_parser("import")
    import_parser.set_defaults(func=do_import)
    import_parser.add_argument("--root",
        help="Root directory to search for Gameday files")

    return parser.parse_args()


def main():
    args = get_args()
    args.func(args)
