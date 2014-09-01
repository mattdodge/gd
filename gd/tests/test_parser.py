import unittest

from pretend import stub

from gd import parser


class Test_get_game(unittest.TestCase):
    """Test the gd.parser.get_game function."""

    def test_get_game(self):
        expected = "test"
        s = stub(attrib=expected)
        actual = parser.get_game(s)
        self.assertEqual(actual, expected)


class Test_get_players(unittest.TestCase):
    """Test the gd.parser.get_players function."""

    def test_get_players(self):
        expected = "test"
        s1 = stub(attrib=expected)
        s2 = stub(attrib=expected)
        s3 = stub(attrib=expected)
        tree = stub(findall=lambda arg: [s1, s2, s3])
        actual = parser.get_players(tree)
        self.assertEqual(list(actual), [expected]*3)


class Test_get_plate_umpire(unittest.TestCase):
    """Test the gd.parser.get_plate_umpire function."""

    def test_get_plate_umpire(self):
        expected = {"position": "home", "name": "Gerry Davis"}
        element = stub(attrib=expected)
        tree = stub(findall=lambda arg: [element])
        actual = parser.get_plate_umpire(tree)
        self.assertEqual(actual, expected)

    def test_get_plate_umpire_no_pu(self):
        expected = {"position": "first", "name": "Ted Barrett"}
        element = stub(attrib=expected)
        tree = stub(findall=lambda arg: [element])
        self.assertRaisesRegex(Exception, "No plate umpire found.",
                               parser.get_plate_umpire, tree)

    def test_get_plate_umpire_no_umpires(self):
        tree = stub(findall=lambda arg: [])
        self.assertRaisesRegex(Exception, "No plate umpire found.",
                               parser.get_plate_umpire, tree)


class Test_get_teams(unittest.TestCase):
    """Test the gd.parser.get_teams function."""

    def test_get_teams(self):
        value = "team name"
        team = stub(attrib=value)
        tree = stub(findall=lambda arg: [team, team])
        actual = parser.get_teams(tree)
        self.assertEqual(list(actual), [value, value])

    def test_get_teams_not_two_teams(self):
        value = "team name"
        team = stub(attrib=value)

        # We should only ever get two teams.
        for teams in ([], [team, team, team]):
            with self.subTest(teams=teams):
                tree = stub(findall=lambda arg: teams)
                actual = parser.get_teams(tree)
                self.assertRaisesRegex(Exception,
                                       "%d teams found" % len(teams),
                                       list, actual)


class Test_get_stadium(unittest.TestCase):
    """Test the gd.parser.get_stadium function."""

    def test_get_stadium(self):
        expected = "Wrigley Field"
        stadium = stub(attrib=expected)
        tree = stub(find=lambda arg: stadium)
        actual = parser.get_stadium(tree)
        self.assertEqual(actual, expected)

    def test_get_stadium_missing(self):
        tree = stub(find=lambda arg: None)
        self.assertRaisesRegex(Exception, "Did not find a stadium.",
                               parser.get_stadium, tree)


class Test_get_atbats(unittest.TestCase):
    """Test the gd.parser.get_atbats function."""

    def test_get_atbats_no_atbats(self):
        tree = stub(findall=lambda arg: [])
        actual = parser.get_atbats(tree)
        self.assertRaisesRegex(Exception, "No atbats found.",
                               list, actual)

    def test_get_atbats(self):
        expected_value = {"key": "value"}
        value = stub(attrib=expected_value)
        atbat = stub(findall=lambda arg: [value],
                     attrib=expected_value)
        tree = stub(findall=lambda arg: [atbat])

        # Pitches are attached to an atbat as a list, so create ours.
        expected = dict(expected_value)
        expected["pitches"] = [expected_value]
        expected["pickoffs"] = [expected_value]
        expected["runners"] = [expected_value]

        actual = parser.get_atbats(tree)
        self.assertEqual(list(actual), [expected])
