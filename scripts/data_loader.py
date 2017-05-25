import simstring
import unicodecsv as csv
import unicodedata
from custom_hashlib import sha1

def load_data_dict(csv_file):
    name_to_id = {}
    with open(csv_file, "rb") as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            bcs_id = int(row[0])
            token = row[1]
            str_token = unicodedata.normalize('NFKD', token).encode('ascii', 'ignore')
            name_to_id[sha1(str_token.lower())] = bcs_id
    return name_to_id

def load_data(csv_file, db_file):
    db = simstring.writer(db_file, 3, False, True)
    with open(csv_file, "rb") as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            word = row[0].lower()
            if type(word) == unicode:
                str_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore')
            else:
                str_word = word
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
