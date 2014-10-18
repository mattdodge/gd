"""
Parser for MLB's Gameday XML data
"""
from gd.utils import create_date, create_datetime, create_time


def _strip_keys(obj, valid):
    """Given a dictionary and a set of valid keys, return a dictionary which
    only contains keys found in `valid`."""
    return {key: obj[key] for key in obj if key in valid}


def _get_all_attributes(tree, element, valid):
    """Given a tree, yield the attribute dictionary of each element."""
    yield from [_strip_keys(x.attrib, valid) for x in tree.findall(element)]


def get_date(tree):
    """Parse players.xml file and return the date these players are playing."""
    return create_date(tree.attrib["date"])


def get_players(tree):
    """Parse players.xml file and return players and their attributes."""
    valid_keys = ("id", "first", "last", "num", "boxname", "rl", "bats",
                  "position", "status", "team_id")
    yield from _get_all_attributes(tree, ".//player", valid_keys)


def get_plate_umpire(tree):
    """Parse players.xml data to find the plate umpire."""
    umpires = tree.findall(".//umpire")
    for ump in umpires:
        if ump.attrib["position"] == "home":
            return {k: v for k, v in ump.attrib.items() if k in ("id", "name")}
    else:
        raise Exception("No plate umpire found.")


def get_game(tree):
    """Parse game.xml data to find the game information."""
    valid_keys = ("game_pk", "type", "local_game_time", "game_time_et",
                  "gameday_sw", "home_team", "away_team", "stadium",
                  "plate_umpire")
    tree.attrib["local_game_time"] = create_time(
        tree.attrib["local_game_time"])
    return {k: v for k, v in tree.attrib.items() if k in valid_keys}


def get_actions(tree):
    valid_keys = ("id", "game_pk", "b", "s", "o", "pitch", "player", "event",
                  "event2", "des_es", "des", "tfs", "tfs_zulu")

    for action in tree.findall(".//action"):
        action.attrib["tfs"] = create_time(action.attrib["tfs"])
        action.attrib["tfs_zulu"] = create_datetime(action.attrib["tfs_zulu"])
        yield {k: v for k, v in action.attrib.items() if k in valid_keys}


def get_teams(tree):
    """Parse game.xml data to find the teams involved."""
    valid_keys = ("code", "id", "name", "name_full", "name_brief",
                  "division_id", "league_id", "league")
    yield from _get_all_attributes(tree, ".//team", valid_keys)


def get_stadium(tree):
    """Parse game.xml data to find the stadium."""
    stadium = tree.find(".//stadium")
    if stadium is None:
        raise Exception("Did not find a stadium.")

    valid_keys = ("id", "name", "location")

    return {k: v for k, v in stadium.attrib.items() if k in valid_keys}


def get_atbats(tree):
    """Parse inning_all.xml data to find the atbats."""
    valid_keys = ("num", "b", "s", "o", "start_tfs", "start_tfs_zulu",
                  "batter", "stand", "b_height", "pitcher", "p_throws",
                  "des", "des_es", "event", "score", "home_team_runs",
                  "away_team_runs")
    for atbat in _get_all_attributes(tree, ".//atbat", valid_keys):
        atbat["start_tfs"] = create_time(atbat["start_tfs"])
        atbat["start_tfs_zulu"] = create_datetime(
            atbat["start_tfs_zulu"])
        atbat["score"] = True if atbat["score"] == "T" else False
        yield atbat


def get_pitches(tree):
    """Parse inning_all.xml data to find the pitches."""
    for atbat in tree.findall(".//atbat"):
        for pitch in atbat.findall(".//pitch"):
            pitch.attrib["tfs"] = create_time(pitch.attrib["tfs"])
            pitch.attrib["tfs_zulu"] = create_datetime(
                pitch.attrib["tfs_zulu"])
            # Tie pitches back to the atbat they came from.
            pitch.attrib["start_tfs_zulu"] = create_datetime(
                atbat.attrib["start_tfs_zulu"])
            yield pitch.attrib
