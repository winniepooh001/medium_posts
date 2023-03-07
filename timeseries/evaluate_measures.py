import numpy as np

def rmse(truth, predicted):
    return np.sqrt(np.mean((truth-predicted) ** 2))

def dir_accuracy(truth, predicted):
    truth_dir = (truth>=0).astype(int)
    predicted_dir = (predicted>=0).astype(int)

    cnts = (truth_dir==predicted_dir).astype(int).sum()
    return cnts/len(truth)