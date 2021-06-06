import pandas as pd
from sqlalchemy import create_engine
import pymongo

import config

username = config.username
password = config.password

### CREATING DATAFRAME ###
mongo_client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.n2hnd.mongodb.net/ifresearch?retryWrites=true&w=majority")
collection = mongo_client.test.sephora_backup3

all_perfumes = list(collection.aggregate([
            {"$project": {"attributes": 1}}
        ]))

# Necesito filtrar los perfumes que ya estan en la Base de Datos MySQL
# o los que no han sido modificados
rows_list = []
for perfume in all_perfumes:
    # if 'attributs' in perfume.keys():
    try:
        print(perfume)
        for attribute in perfume['attributes'].items():
            up_dict = {attribute[0]: sum(attribute[1].values())}
            perfume['attributes'].update(up_dict)
        perfume['attributes'].update({"_id": str(perfume['_id'])})
        print(perfume['attributes'])
        rows_list.append(perfume['attributes'])
    except:
        pass
df = pd.DataFrame(rows_list)

# # mysql://bb9f0d500c90e4:1b33575e@eu-cdbr-west-01.cleardb.com/heroku_02c821a76ca04c8?reconnect=true
# host = 'mysql://bb9f0d500c90e4:1b33575e@eu-cdbr-west-01.cleardb.com'
# db = "heroku_02c821a76ca04c8"
# user = "bb9f0d500c90e4"
# pasw = "1b33575e"
#
# engine = create_engine('mysql://bb9f0d500c90e4:1b33575e@eu-cdbr-west-01.cleardb.com/heroku_02c821a76ca04c8')
# df.to_csv('attributs', engine,if_exists='append')
df.to_csv('attributes.csv')




