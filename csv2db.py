import os
import core
import csv


db = core.connect()
tables = set(db.tables)

for f in os.listdir('.'):
    if f.endswith('.csv'):
        name = f.replace('.csv', '')

        if name not in tables:
            with open(f, encoding='cp1252') as csv_file:
                reader = csv.DictReader(csv_file)

                for row in reader:
                    db[name].insert({k: v for k, v in row.items()
                                     if k is not None and len(k) > 0})
