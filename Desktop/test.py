import pickle
from io import BytesIO

with open("dbdb.db", "rb") as f:
    data = f.read()
file = BytesIO(data)
dat = pickle.load(file)
file1 = BytesIO()
pickle.dump(dat, file1)
file1.seek(0)
dat = pickle.load(file1)
print(dat)