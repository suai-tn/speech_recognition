import os
import json
from speechbrain.utils.data_utils import download_file
from speechbrain.dataio.dataio import read_audio


DATA_URL = "https://www.openslr.org/resources/46/Tunisian_MSA.tar.gz"
DEST_FILE = DATA_URL.split('/')[-1]
FOLDER_EXTRACT = DEST_FILE.split('.')[0]
DATA_PATH = os.path.join(FOLDER_EXTRACT, "data")

SAMPLERATE = 16000

T_EXTENSION = [".tsv"]
S_EXTENSION = [".wav"]

BASE = "Answers_Arabic"


def check_data():
    if not os.path.exists(DEST_FILE):
        download_file(DATA_URL, DEST_FILE, True)


def split_test_valid(data, test_path, valid_path, max_test=20):
    i = 0
    with open(data, 'r') as f:
        d = json.loads(f.read())
    valid = {}
    test = {}
    for key in d:
        if i >= max_test:
            valid[key] = d[key]
        else:
            test[key] = d[key]
        i += 1

    with open(test_path, mode="w", encoding='utf8') as json_f:
        json.dump(test, json_f, indent=2)

    with open(valid_path, mode="w", encoding='utf8') as json_f:
        json.dump(valid, json_f, indent=2)


def id_to_path(id):
    if id.count('_') >= 2:
        ids = id.split('_')
        return os.path.join(ids[0], BASE, ids[1], ids[4]) + S_EXTENSION[0]
    else:
        return id + S_EXTENSION[0]


def prepare_speechfile(save_json_train="data/train.json", save_json_test="data/test.json", save_json_valid="data/valid.json"):

    check_data()

    train_trans_file = os.path.join(DATA_PATH, "transcripts/train/answers.tsv")
    train_speech_folder = os.path.join(DATA_PATH, "speech/train")

    test_trans_file = os.path.join(
        DATA_PATH, "transcripts/test/mbt/recordings/mbt_recordings.tsv")
    test_speech_folder = os.path.join(
        DATA_PATH, "speech/test/mbt/recordings/mbt")

    # dev_trans_file = os.path.join(
    #     DATA_PATH, "transcripts/devtest/recordings.tsv")
    # dev_speech_folder = os.path.join(DATA_PATH, "speech/devtest")

    create_json(train_trans_file, train_speech_folder, save_json_train)
    print('train file done !')
    create_json(test_trans_file, test_speech_folder, save_json_test)
    print('test file done !')
    split_test_valid(save_json_test, save_json_test, save_json_valid)
    print('valid file done !')


def create_json(trans_file, speech_folder, json_file):
    json_dict = {}

    with open(trans_file, encoding='utf8') as f:
        i = 1
        for line in f:
            id, text = line.split("\t")
            text = text.rstrip().split(" ")
            text = " ".join(text)
            wav = os.path.join(speech_folder, id_to_path(id))

            signal = read_audio(wav)
            duration = signal.shape[0] / SAMPLERATE

            json_dict[i] = {
                "wav": wav,
                "length": duration,
                "words": text,
            }

            i += 1

    with open(json_file, mode="w", encoding='utf8') as json_f:
        json.dump(json_dict, json_f, indent=2)
