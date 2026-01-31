import argparse

class Cli:
  def __init__(self):
    self.parser = argparse.ArgumentParser(description='get list of github projeccts')
    self.parser.add_argument('-f', action='store_true', help='force download')
    self.args = self.parser.parse_args()

  def get_args(self):
    return self.args
