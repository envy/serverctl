import unittest
import utils


class CmdSplitTest(unittest.TestCase):

    def test_empty(self):
        _in = ""
        _out = []
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_single(self):
        _in = 'ls'
        _out = ['ls']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_multiple(self):
        _in = 'ls -l'
        _out = ['ls', '-l']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_multiple_short(self):
        _in = 'ls l'
        _out = ['ls', 'l']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_multiple_five(self):
        _in = 'ls -l -a -v /'
        _out = ['ls', '-l', '-a', '-v', '/']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_multiple_space_even(self):
        _in = 'ls  -l'
        _out = ['ls', '-l']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_multiple_space_off(self):
        _in = 'ls   -l'
        _out = ['ls', '-l']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_quote(self):
        _in = 'ls "My Documents"'
        _out = ['ls', 'My Documents']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_mixed(self):
        _in = 'ls -l "My Documents"'
        _out = ['ls', '-l', 'My Documents']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_whole_quotes(self):
        _in = '"ls -l My Documents"'
        _out = ['ls -l My Documents']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_quote_in_arg(self):
        _in = 'ls -l"My Documents"'
        _out = ['ls', '-lMy Documents']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_quote_in_middle(self):
        _in = 'ls -l "My Documents" -a'
        _out = ['ls', '-l', 'My Documents', '-a']
        self.assertEqual(_out, utils.split_cmd(_in))

    def test_quote_in_arg_and_middle(self):
        _in = 'ls -l"My Documents" -a'
        _out = ['ls', '-lMy Documents', '-a']
        self.assertEqual(_out, utils.split_cmd(_in))


if __name__ == '__main__':
    unittest.main()
