from sqlalchemy.orm import relationship, backref
from sqlalchemy import (Column, Date, DateTime, Time, ForeignKey, Integer,
                        String, Numeric, Boolean)

from gd.database import Base


class Team(Base):
    __tablename__ = "team"

    code = Column(String, primary_key=True)
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    name_full = Column(String, nullable=False)
    name_brief = Column(String, nullable=False)
    division_id = Column(Integer, nullable=False)
    league_id = Column(Integer, nullable=False)
    league = Column(String, nullable=False)

    players = relationship("Player")
    replays = relationship("Replay", backref="team")

    def __repr__(self):
        return "<%s id=%s>" % (self.name_full, self.id)


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, nullable=False, primary_key=True)
    first = Column(String, nullable=False)
    last = Column(String, nullable=False)
    num = Column(Integer, nullable=False)
    boxname = Column(String, nullable=False)
    rl = Column(String, nullable=False)
    bats = Column(String, nullable=False)
    position = Column(String, nullable=False)
    status = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)

    # The following is available in the /batters/ dir. Could be merged here.
    # height  = Column(String, nullable=False)
    # weight = Column(Integer, nullable=False)
    # throws = Column(String, nullable=False)
    # dob = Column(String, nullable=False)

    def __repr__(self):
        return "<Player id=%s, name=%s %s>" % (self.id, self.first, self.last)


class Umpire(Base):
    __tablename__ = "umpire"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)

    games = relationship("Game")

    def __repr__(self):
        return "Umpire(id=%d, name='%s')" % (self.id, self.name)


class Stadium(Base):
    __tablename__ = "stadium"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)

    def __repr__(self):
        return "Stadium(id=%d, name='%s', location='%s')" % (self.id,
                                                             self.name,
                                                             self.location)


class Game(Base):
    __tablename__ = "game"

    game_pk = Column(Integer, nullable=False, primary_key=True)
    type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    local_game_time = Column(Time, nullable=False)
    game_time_et = Column(String, nullable=False)
    gameday_sw = Column(String, nullable=False)
    home_team = Column(Integer, ForeignKey("team.code"), nullable=False)
    away_team = Column(Integer, ForeignKey("team.code"), nullable=False)
    stadium = Column(Integer, ForeignKey("stadium.id"), nullable=False)
    umpire_id = Column(Integer, ForeignKey("umpire.id"), nullable=False)

    atbats = relationship("AtBat", backref="game")
    actions = relationship("Action", backref="game")
    pitches = relationship("Pitch", backref="game")
    replays = relationship("Replay", backref="game")
    umpire = relationship("Umpire", backref=backref("game", uselist=False))

    def __repr__(self):
        return "Game #%d %s@%s" % (self.game_pk, self.away_team,
                                   self.home_team)


class AtBat(Base):
    __tablename__ = "atbat"

    atbat_id = Column(Integer, autoincrement=True, primary_key=True)
    num = Column(Integer, nullable=False)
    b = Column(Integer, nullable=False)
    s = Column(Integer, nullable=False)
    o = Column(Integer, nullable=False)
    start_tfs = Column(Time, nullable=False)
    start_tfs_zulu = Column(DateTime, nullable=False)
    batter = Column(Integer, ForeignKey("player.id"), nullable=False)
    stand = Column(String, nullable=False)
    b_height = Column(String, nullable=False)
    pitcher = Column(Integer, ForeignKey("player.id"), nullable=False)
    p_throws = Column(String, nullable=False)
    des = Column(String, nullable=False)
    des_es = Column(String, nullable=False)
    event = Column(String, nullable=False)
    score = Column(Boolean)
    home_team_runs = Column(Integer)
    away_team_runs = Column(Integer)

    # Added
    game_pk = Column(Integer, ForeignKey("game.game_pk"), nullable=False)

    replay = relationship("Replay", backref="atbat")
    pitches = relationship("Pitch", backref="atbat")

    def __repr__(self):
        return "AtBat #%d, batter %d facing pitcher %d" % (self.num,
                                                           self.batter,
                                                           self.pitcher)


class Pitch(Base):
    __tablename__ = "pitch"

    pitch_id = Column(Integer, autoincrement=True, primary_key=True)
    des = Column(String, nullable=False)
    des_es = Column(String, nullable=False)
    # This is an in-game pitch ID, not universal.
    id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    tfs = Column(Time)
    tfs_zulu = Column(DateTime)
    x = Column(Numeric)
    y = Column(Numeric)
    on_1b = Column(Integer)
    on_2b = Column(Integer)
    on_3b = Column(Integer)
    sv_id = Column(String)
    start_speed = Column(Numeric)
    end_speed = Column(Numeric)
    sz_top = Column(Numeric)
    sz_bot = Column(Numeric)
    pfx_x = Column(Numeric)
    pfx_z = Column(Numeric)
    px = Column(Numeric)
    pz = Column(Numeric)
    x0 = Column(Numeric)
    y0 = Column(Numeric)
    z0 = Column(Numeric)
    vx0 = Column(Numeric)
    vy0 = Column(Numeric)
    vz0 = Column(Numeric)
    ax = Column(Numeric)
    ay = Column(Numeric)
    az = Column(Numeric)
    break_y = Column(Numeric)
    break_angle = Column(Numeric)
    break_length = Column(Numeric)
    pitch_type = Column(String)
    type_confidence = Column(Numeric)
    zone = Column(Integer)
    nasty = Column(Integer)
    spin_dir = Column(Numeric)
    spin_rate = Column(Numeric)
    cc = Column(String)
    mt = Column(String)

    # Added
    start_tfs_zulu = Column(DateTime, ForeignKey("atbat.start_tfs_zulu"),
                            nullable=False)
    game_pk = Column(Integer, ForeignKey("game.game_pk"), nullable=False)

    def __repr__(self):
        return "<Pitch id=%s at %s>" % (self.id, self.tfs_zulu)


class Action(Base):
    __tablename__ = "action"

    id = Column(Integer, autoincrement=True, primary_key=True)
    game_pk = Column(Integer, ForeignKey("game.game_pk"), nullable=False)
    b = Column(Integer, nullable=False)
    s = Column(Integer, nullable=False)
    o = Column(Integer, nullable=False)
    pitch = Column(Integer, nullable=False)
    player = Column(Integer, nullable=False)
    event = Column(String, nullable=False)
    event2 = Column(String)
    des = Column(String, nullable=False)
    des_es = Column(String)
    tfs = Column(Time, nullable=False)
    tfs_zulu = Column(DateTime, nullable=False)

    replay = relationship("Replay", backref="action")

    def __repr__(self):
        return "<Action id=%s %s>" % (self.id, self.event)


class Replay(Base):
    __tablename__ = "replay"

    id = Column(Integer, autoincrement=True, primary_key=True)
    atbat_id = Column(Integer, ForeignKey("atbat.atbat_id"))
    action_id = Column(Integer, ForeignKey("action.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    game_pk = Column(Integer, ForeignKey("game.game_pk"), nullable=False)
    play = Column(String, nullable=False)
    result = Column(String, nullable=False)
    des = Column(String, nullable=False)
    des_es = Column(String)
    tfs = Column(Time, nullable=False)
    tfs_zulu = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<Replay id=%s result=%s>" % (self.id, self.result)
