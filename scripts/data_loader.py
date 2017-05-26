import simstring
import unicodecsv as csv
import unicodedata
import hashlib

class HashVal(object):
    def __init__(self):
        self.hash_func = hashlib.md5()

    def getHash(self, token):
        return token

def load_data_dict(csv_file):
    name_to_id = {}
    hash_v = HashVal()
    with open(csv_file, "rb") as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            bcs_id = int(row[0])
            token = row[1]
            str_token = unicodedata.normalize('NFKD', token).encode('ascii', 'ignore')
            hash_key = hash_v.getHash(str_token.lower());
            if name_to_id.has_key(hash_key):
                name_to_id[hash_key] += [bcs_id]
            else:
                name_to_id[hash_key] = [bcs_id]
    return name_to_id

def load_data(csv_file, db_file):
    db = simstring.writer(db_file, 3, False, True)
    with open(csv_file, "rb") as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            word = row[0].lower()
            str_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore')
            try:
                db.insert(str_word);
            except UnicodeEncodeError as e:
                print word
                pass
    db.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print "Wrong usage", sys.argv[0], " <input.json> <output.json>"
        sys.exit(-1)
    load_data(sys.argv[1], sys.argv[2])
