from flask_frozen import Freezer
from generate_site import app   # on importe ton app Flask depuis generate_site.py

freezer = Freezer(app)

if __name__ == "__main__":
    freezer.freeze()
