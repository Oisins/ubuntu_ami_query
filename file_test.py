#!/usr/bin/env python
import unittest
import json
from mock import Mock
import ubuntu_ami_query


class mainTest(unittest.TestCase):
    def test_probe(self):
        resp = open("test.json").read()

        argsMock = Mock()
        argsMock.search = ["eu-west-1", "amd64", "^ebs"]
        
        ubuntu_ami_query.connectToCI = Mock(return_value=resp)
        ubuntu_ami_query.readArgs = Mock(return_value=argsMock)
        ubuntu_ami_query.logLatest = Mock()
        ubuntu_ami_query.main()

        expected = "ami-73cfaf50"
        ubuntu_ami_query.logLatest.assert_called_with(expected)

if __name__ == '__main__':
    unittest.main()
