import pickle
import csv

def save_model(model, filename):
    with open(filename, 'wb') as file:
        pickle.dump(model, file)

def load_model(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)

def save_model_info(history, filename):
    with open(filename, 'wb') as file:
        pickle.dump(history, file)

def load_model_info(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)

def save_model_info_csv(history, filename):
    keys = history.keys()
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for i in range(len(history[next(iter(keys))])):
            row = {key: history[key][i] for key in keys}
            writer.writerow(row)
