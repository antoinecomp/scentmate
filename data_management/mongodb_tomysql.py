import pandas as pd
import pymongo

import config

username = config.username
password = config.password

### CREATING DATAFRAME ###
mongo_client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.n2hnd.mongodb.net/ifresearch?retryWrites=true&w=majority")
collection = mongo_client.test.sephora_backup3

all_perfumes = list(collection.aggregate([
            {"$project": {"d": 1}}
        ]))

# Necesito filtrar los perfumes que ya estan en la Base de Datos MySQL
# o los que no han sido modificados
rows_list = []
for perfume in all_perfumes:
    for attribute in perfume['d']['attributs'].items():
        up_dict = {attribute[0]: sum(attribute[1].values())}
        perfume['d']['attributs'].update(up_dict)
    perfume['d']['attributs'].update({"_id": str(perfume['_id'])})
    rows_list.append(perfume['d']['attributs'])
df = pd.DataFrame(rows_list)
print(df.head())

