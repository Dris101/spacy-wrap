from setuptools import setup, find_packages


with open("spacy_wrap/about.py") as f:
     v = f.read()
     for l in v.split("\n"):
         if l.startswith("__version__"):
             __version__ = l.split('"')[-2]


 def setup_package():
     setup(version=__version__)



if __name__ == "__main__":
    setup_package()
