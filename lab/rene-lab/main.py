"""
Created on July 29 11:59, 2020

@author: fassial
"""
import os
import math
import shutil
import numpy as np
from collections import Counter
# local dep
import sys
sys.path.append("./rene")
import utils
# import rene
import rene_full as rene

# file loc params
PREFIX = ".."
# dataset & predataset
DATASET = os.path.join(PREFIX, "dataset")
PREDATASET = os.path.join(PREFIX, "predataset")
# data file
FEATURE_FILE = os.path.join(DATASET, "feature.csv")
LABEL_FILE   = os.path.join(DATASET, "label.csv")
FEATURE_ENCODE_FILE = os.path.join(DATASET, "feature_encode.csv")
# train set
TRAINSET = os.path.join(DATASET, "train")
TRAINSET_FEATUREENCODE = os.path.join(TRAINSET, "feature_encode")
TRAINSET_RANGEENCODE = os.path.join(TRAINSET, "range_encode")
TRAINSET_LABEL = os.path.join(TRAINSET, "label")
PRETRAINSET = os.path.join(PREDATASET, "train")
# test set
TESTSET = os.path.join(DATASET, "test")
TESTSET_FEATUREENCODE = os.path.join(TESTSET, "feature_encode")
TESTSET_LABEL = os.path.join(TESTSET, "label")
PRETESTSET = os.path.join(PREDATASET, "test")
# eval dir
EVALDIR = os.path.join(DATASET, "eval")
# ecode params
W = 8
HMAX = 8
H = [4, 6, 8]
# train & test params
P_TRAIN = 0.7
N_TOP = 20
MAX_ROW = 2000
# eval params
H = [2**i for i in range(1, 5)]     # [2, 4, 8, 16]

"""
_split_dataset:
    split the dataset into trainset and testset
    @params:
        x_all(np.array) : feature of dataset
        y_all(np.array) : label of dataset
        ptrain(float)   : P of trainset
    @rets:
        x_train(np.array)   : feature of trainset
        y_train(np.array)   : label of trainset
        x_test(np.array)    : feature of testset
        y_test(np.array)    : label of testset
"""
def _split_dataset(x_all, y_all, ptrain = P_TRAIN):
    # init res
    x_train, y_train, x_test, y_test = [], [], [], []
    # get conter
    y_all_counter = Counter(y_all)
    for label in set(y_all):
        n_train = int(y_all_counter[label] * ptrain)
        n_test = y_all_counter[label] - n_train
        # get label_train
        index = 0
        while n_train > 0:
            if y_all[index] == label:
                x_train.append(x_all[index])
                y_train.append(y_all[index])
                n_train -= 1
            index += 1
        # get label_test
        while n_test > 0:
            if y_all[index] == label:
                x_test.append(x_all[index])
                y_test.append(y_all[index])
                n_test -= 1
            index += 1
    return np.array(x_train), np.array(y_train), np.array(x_test), np.array(y_test)

"""
split_dataset:
    split the dataset into trainset and testset, save on disk
    @params:
        None
    @rets:
        None
"""
def split_dataset():
    # get feature & label
    feature = utils.load_data(FEATURE_FILE)[:, 1:].astype(np.float64)
    label = utils.load_data(LABEL_FILE)[:, 1].astype(np.int32)
    # get train_set & test_set
    x_train, y_train, x_test, y_test = _split_dataset(
        x_all = feature,
        y_all = label
    )
    # check whether dir exists
    if os.path.exists(TRAINSET): shutil.rmtree(TRAINSET)
    if os.path.exists(TESTSET): shutil.rmtree(TESTSET)
    os.mkdir(TRAINSET)
    os.mkdir(TESTSET)
    # save raw data
    utils.store_data(
        os.path.join(TRAINSET, "feature.csv"),
        x_train
    )
    utils.store_data(
        os.path.join(TRAINSET, "label.csv"),
        y_train
    )
    utils.store_data(
        os.path.join(TESTSET, "feature.csv"),
        x_test
    )
    utils.store_data(
        os.path.join(TESTSET, "label.csv"),
        y_test
    )

"""
save_encodeset:
    save the RENE-encode of trainset & testset
    @params:
        None
    @rets:
        None
"""
def save_encodeset():
    # get raw dataset
    feature = utils.load_data(FEATURE_FILE)[:, 1:]
    feature_max = np.max(feature)
    # get trainset
    train_feature = utils.load_data(
        os.path.join(TRAINSET, "feature.csv")
    )
    train_label = utils.load_data(
        os.path.join(TRAINSET, "label.csv")
    )[:].reshape(-1, 1)
    # remap trainset to Z
    feature_remap = utils.remap(train_feature, (0, 2**W-1), feature_max)
    # check trainset dir
    if os.path.exists(TRAINSET_FEATUREENCODE): os.removedirs(TRAINSET_FEATUREENCODE)
    if os.path.exists(TRAINSET_LABEL): os.removedirs(TRAINSET_LABEL)
    os.mkdir(TRAINSET_FEATUREENCODE)
    os.mkdir(TRAINSET_LABEL)
    # check testset dir
    if os.path.exists(TESTSET_FEATUREENCODE): shutil.rmtree(TESTSET_FEATUREENCODE)
    if os.path.exists(TESTSET_LABEL): shutil.rmtree(TESTSET_LABEL)
    os.mkdir(TESTSET_FEATUREENCODE)
    os.mkdir(TESTSET_LABEL)
    # save x_train & y_train
    for i in range(feature_remap.shape[0] // MAX_ROW):
        feature_encode = utils.encode(feature_remap[(i*MAX_ROW):(i+1)*MAX_ROW, :], feature_remap[0].shape[0], W, HMAX)
        feature_encode = feature_encode.reshape(feature_encode.shape[0], -1)
        utils.store_data(
            os.path.join(TRAINSET_FEATUREENCODE, "feature_encode_" + str(i*MAX_ROW) + "_" + str((i+1)*MAX_ROW) + ".csv"),
            feature_encode
        )
        utils.store_data(
            os.path.join(TRAINSET_LABEL, "label_" + str(i*MAX_ROW) + "_" + str((i+1)*MAX_ROW) + ".csv"),
            train_label[(i*MAX_ROW):((i+1)*MAX_ROW)]
        )
    if feature_remap.shape[0] % MAX_ROW != 0:
        feature_encode = utils.encode(feature_remap[((feature_remap.shape[0] // MAX_ROW)*MAX_ROW):feature_remap.shape[0], :], feature_remap[0].shape[0], W, HMAX)
        feature_encode = feature_encode.reshape(feature_encode.shape[0], -1)
        utils.store_data(
            os.path.join(TRAINSET_FEATUREENCODE, "feature_encode_" + str((feature_remap.shape[0] // MAX_ROW)*MAX_ROW) + "_" + str(feature_remap.shape[0]) + ".csv"),
            feature_encode
        )
        utils.store_data(
            os.path.join(TRAINSET_LABEL, "label_" + str((feature_remap.shape[0] // MAX_ROW)*MAX_ROW) + "_" + str(feature_remap.shape[0]) + ".csv"),
            train_label[((feature_remap.shape[0] // MAX_ROW)*MAX_ROW):feature_remap.shape[0]]
        )
    # save x_train's range encode
    if os.path.exists(TRAINSET_RANGEENCODE): shutil.rmtree(TRAINSET_RANGEENCODE)
    os.mkdir(TRAINSET_RANGEENCODE)
    for h in H:
        range_encode_path = os.path.join(TRAINSET_RANGEENCODE, "range_encode_" + str(h))
        if os.path.exists(range_encode_path): shutil.rmtree(range_encode_path)
        os.mkdir(range_encode_path)
    for i in range(feature_remap.shape[0] // MAX_ROW):
        # get range encode
        for h in H:
            range_encode = utils.encode(feature_remap[(i*MAX_ROW):(i+1)*MAX_ROW, :], feature_remap[0].shape[0], W, HMAX, h)
            range_encode = range_encode.reshape(range_encode.shape[0], -1)
            utils.store_data(
                os.path.join(TRAINSET_RANGEENCODE, "range_encode_" + str(h), str(i*MAX_ROW) + "_" + str((i+1)*MAX_ROW) + ".csv"),
                range_encode
            )
    if feature_remap.shape[0] % MAX_ROW != 0:
        # get range encode
        for h in H:
            range_encode = utils.encode(feature_remap[((feature_remap.shape[0] // MAX_ROW)*MAX_ROW):feature_remap.shape[0], :], feature_remap[0].shape[0], W, HMAX, h)
            range_encode = range_encode.reshape(range_encode.shape[0], -1)
            utils.store_data(
                os.path.join(TRAINSET_RANGEENCODE, "range_encode_" + str(h), str((feature_remap.shape[0] // MAX_ROW)*MAX_ROW) + "_" + str(feature_remap.shape[0]) + ".csv"),
                range_encode
            )
    # get testset
    test_feature = utils.load_data(
        os.path.join(TESTSET, "feature.csv")
    )
    test_label = utils.load_data(
        os.path.join(TESTSET, "label.csv")
    )[:].reshape(-1, 1)
    # remap testset to Z
    feature_remap = utils.remap(test_feature, (0, 2**W-1), feature_max)
    # save x_test & y_test
    for i in range(feature_remap.shape[0] // MAX_ROW):
        feature_encode = utils.encode(feature_remap[(i*MAX_ROW):(i+1)*MAX_ROW, :], feature_remap[0].shape[0], W, HMAX)
        feature_encode = feature_encode.reshape(feature_encode.shape[0], -1)
        utils.store_data(
            os.path.join(TESTSET_FEATUREENCODE, "feature_encode_" + str(i*MAX_ROW) + "_" + str((i+1)*MAX_ROW) + ".csv"),
            feature_encode
        )
        utils.store_data(
            os.path.join(TESTSET_LABEL, "label_" + str(i*MAX_ROW) + "_" + str((i+1)*MAX_ROW) + ".csv"),
            test_label[(i*MAX_ROW):((i+1)*MAX_ROW)]
        )
    if feature_remap.shape[0] % MAX_ROW != 0:
        feature_encode = utils.encode(feature_remap[((feature_remap.shape[0] // MAX_ROW)*MAX_ROW):feature_remap.shape[0], :], feature_remap[0].shape[0], W, HMAX)
        feature_encode = feature_encode.reshape(feature_encode.shape[0], -1)
        utils.store_data(
            os.path.join(TESTSET_FEATUREENCODE, "feature_encode_" + str((feature_remap.shape[0] // MAX_ROW)*MAX_ROW) + "_" + str(feature_remap.shape[0]) + ".csv"),
            feature_encode
        )
        utils.store_data(
            os.path.join(TESTSET_LABEL, "label_" + str((feature_remap.shape[0] // MAX_ROW)*MAX_ROW) + "_" + str(feature_remap.shape[0]) + ".csv"),
            test_label[((feature_remap.shape[0] // MAX_ROW)*MAX_ROW):feature_remap.shape[0]]
        )

"""
_ternaryMatch:
    ternary match
    @params:
        _point(np.array)    : point with shape(n_feature, )
        _range(np.array)    : range with shape(n_feature, 2)
    @rets:
        flag(bool)          : whether _point & _range ternary math
"""
def _ternaryMatch(_point, _range):
    # print(_point.shape, _range.shape)
    if _point.shape[0] != _range.shape[0]: return False
    for i in range(_point.shape[0]):
        # print(_range[i, 0], _range[i, 1], _point[i])
        if not rene.ternary_match(_range[i, 0], _range[i, 1], _point[i], np.zeros(_point[i].shape)):
            # print(i)
            return False
    return True

"""
_get_cubes:
    get cubes from (points, h)
    @params:
        points(np.array)    : feature matrix with shape(n_point, n_feature)
        h(int)              : side length of cube
    @rets:
        cubes(np.array)     : cubes of (points, h) with shape(n_point, n_feature, 2, bit_width)
"""
def _get_cubes(points, h):
    cubes = []
    for i in range(points.shape[0]):
        cube = rene.tcode(
            p = points[i],
            d = points[i].shape[0],
            w = W,
            hmax = max(HMAX, h),
            h = h
        )# ; print(np.array(cube).shape)
        cubes.append(cube)
    return np.array(cubes).astype(np.int32)

"""
_get_nmatch:
    get the number of match(query point & points' cubes)
    @params:
        points(np.array)        : dataset with shape(n_points, n_feature) to build cubes
        querys_encode(np.array) : queryset_encode with shape(n_querys, n_feature) to query cubes
        h(int)                  : side length of cube
    @rets:
        nmatch(np.array)        : the number of match(query point & points' cubes) with shape(n_querys,)
"""
def _get_nmatch(points, querys_encode, h = 32):
    # init nmatch
    nmatch = []
    # get cubes
    cubes = _get_cubes(
        points = points,
        h = h
    )# ; print(cubes.shape)
    # set nmatch
    for i in range(querys_encode.shape[0]):
        count = 0
        for j in range(cubes.shape[0]):
            if _ternaryMatch(querys_encode[i], cubes[j]): count += 1
        nmatch.append(count)
    return np.array(nmatch)

def get_nmatch():
    # set params
    h = 64
    # get x_train & x_test
    # get trainset
    train_feature = utils.load_data(
        # os.path.join(TRAINSET, "feature.csv")
        os.path.join(PRETRAINSET, "feature.csv")
    )[:1, :]
    # get testset
    test_feature = utils.load_data(
        # os.path.join(TESTSET, "feature.csv")
        os.path.join(PRETESTSET, "feature.csv")
    )[:1, :]
    train_feature_max = np.max(train_feature)
    test_feature_max = np.max(test_feature)
    feature_max = max(train_feature_max, test_feature_max)
    # remap trainset to Z
    train_feature_remap = utils.remap(train_feature, (0, 2**W-1), feature_max)
    # get RENE-encode
    train_feature_encode = utils.encode(train_feature_remap, train_feature_remap[0].shape[0], W, max(HMAX, h))
    # remap testset to Z
    test_feature_remap = utils.remap(test_feature, (0, 2**W-1), feature_max)
    # get RENE-encode
    test_feature_encode = utils.encode(test_feature_remap, test_feature_remap[0].shape[0], W, max(HMAX, h))
    # get nmatch
    # print(train_feature_remap[0, 6], test_feature_remap[0, 6])
    # print(train_feature_encode[0, 6], test_feature_encode[0, 6])
    nmatch = _get_nmatch(
        points = train_feature_remap,
        querys_encode = test_feature_encode,
        h = h
    )
    # check eval_dir
    if os.path.exists(EVALDIR): shutil.rmtree(EVALDIR)
    os.mkdir(EVALDIR)
    # store nmatch
    utils.store_data(
        os.path.join(EVALDIR, "nmatch_" + str(h) + ".csv"),
        nmatch
    )
    # get pmatch
    pmatch = sum(nmatch > 0) / nmatch.shape[0]
    print("pmatch:", pmatch)

def _get_nmatch2(points, querys, h = 16):
    # init nmatch
    nmatch = []
    # set nmatch
    for i in range(querys.shape[0]):
        if i % 100 == 0: print("cycle:", i)
        count = 0
        for j in range(points.shape[0]):
            diff = np.abs(points[j] - querys[i])
            if (diff < h).all(): count += 1
        nmatch.append(count)
    return np.array(nmatch)

def get_nmatch2():
    # set params
    _h = 4
    h = _h // 2
    # get x_train & x_test
    # get trainset
    train_feature = utils.load_data(
        os.path.join(TRAINSET, "feature.csv")
        # os.path.join(PRETRAINSET, "feature.csv")
    )# [:1, :]
    # get testset
    test_feature = utils.load_data(
        os.path.join(TESTSET, "feature.csv")
        # os.path.join(PRETESTSET, "feature.csv")
    )# [:1, :]
    train_feature_max = np.max(train_feature)
    test_feature_max = np.max(test_feature)
    feature_max = max(train_feature_max, test_feature_max)
    # remap trainset to Z
    train_feature_remap = utils.remap(train_feature, (0, 2**W-1), feature_max)
    # remap testset to Z
    test_feature_remap = utils.remap(test_feature, (0, 2**W-1), feature_max)
    # get nmatch
    nmatch = _get_nmatch2(
        points = train_feature_remap,
        querys = test_feature_remap,
        h = h
    )
    # check eval_dir
    if os.path.exists(EVALDIR): shutil.rmtree(EVALDIR)
    os.mkdir(EVALDIR)
    # store nmatch
    utils.store_data(
        os.path.join(EVALDIR, "nmatch_" + str(_h) + ".csv"),
        nmatch
    )
    # get pmatch
    pmatch = sum(nmatch > 0) / nmatch.shape[0]
    print("pmatch:", pmatch)

"""
ptopN:
    calculate accuracy of dist-classifier based on RENE-encode
    @params:
        x_train(np.array)   : feature of trainset
        y_train(np.array)   : label of trainset
        x_test(np.array)    : feature of testset
        y_test(np.array)    : label of testset
        n_top(int)          : number of check
    @rets:
        P(float)            : accuracy of classifier
"""
def ptopN(x_train, y_train, x_test, y_test, n_top = N_TOP):
    P = 0
    n_test = y_test.shape[0]
    # get sim(n_test, n_train)
    sim = x_test.dot(x_train.T)
    order = np.argsort(-sim)
    # get accu
    for i in range(n_test):
        if i % 100 == 0: print("cycle:", i)
        correct = 0
        for j in range(n_top):
            if y_test[i, 0] == y_train[order[i, j], 0]: correct += 1
        P += correct / n_top
    P /= n_test
    return P

def _get_index(points, querys, h = 16, k = 10, _ord = 2):
    # init indexes
    indexes = []
    # set indexes
    for i in range(querys.shape[0]):
        if i % 100 == 0: print("cycle:", i)
        index = []
        for j in range(points.shape[0]):
            diff = np.abs(points[j] - querys[i])
            if (diff < h).all(): index.append(j)
        if len(index) > k:
            query = querys[i]
            dist = np.zeros((len(index),))
            for i in range(dist.shape[0]):
                dist[i] = np.linalg.norm(
                    query - self.points[i],
                    ord = _ord
                )
            # sort dist
            k_index = np.argsort(dist)[:k]
            # get index
            index = np.array(index)[k_index].tolist()
        indexes.append(index)
    return indexes

def get_rene():
    # get trainset & testset
    # x_train, y_train, x_test, y_test = utils.load_dataset(dirpath = PREDATASET); print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)
    import pandas as pd
    from sklearn.model_selection import train_test_split
    data_file = os.path.join(".", "renedataset", 'pc_coords_full_0721.csv')
    label_file = os.path.join(".", "renedataset", 'global_label_full_0721.csv')
    all_feature = pd.read_csv(data_file, encoding='utf-8', engine='python', header=None)
    all_feature.drop([0], axis=1, inplace=True)
    all_label = pd.read_csv(label_file, encoding='utf-8', engine='python', header=None)
    all_label.drop([0], axis=1, inplace=True)

    all_feature = np.array(all_feature)
    all_label = np.array(all_label).reshape(-1)
    labels = np.unique(all_label)
    print (all_feature.shape)
    print (all_label.shape)
    print (labels.shape)
    train_feature = []
    db_label = []
    test_feature = []
    query_label = []
    for i in range(len(labels)):
        idx = np.where(all_label==labels[i])[0]
        if len(idx) > 1:
            X_train, X_test, y_train, y_test = train_test_split(all_feature[idx,:], all_label[idx],test_size=0.3, random_state=0)
            point = int(X_train.shape[0]*1)
            if point <= 0:
                point = 1
            train_feature.extend(X_train[0:point,:].reshape(-1, all_feature.shape[1]))
            db_label.extend(y_train[0:point])
            test_feature.extend(X_test)
            query_label.extend(y_test)
    train_feature = np.array(train_feature).reshape(-1, all_feature.shape[1])
    test_feature = np.array(test_feature).reshape(-1, all_feature.shape[1])
    db_label = np.array(db_label).reshape(-1, )
    query_label = np.array(query_label).reshape(-1, )
    # get max
    train_feature_max = np.max(train_feature)
    test_feature_max = np.max(test_feature)
    feature_max = max(train_feature_max, test_feature_max)
    # remap trainset to Z
    train_feature_remap = utils.remap(train_feature, (0, 2**W-1), feature_max)
    # remap testset to Z
    test_feature_remap = utils.remap(test_feature, (0, 2**W-1), feature_max)
    # get encode
    train_feature_encode = utils.encode(train_feature_remap, train_feature_remap[0].shape[0], W, HMAX); train_feature_encode = train_feature_encode.reshape((train_feature_encode.shape[0], -1))
    test_feature_encode = utils.encode(test_feature_remap, test_feature_remap[0].shape[0], W, HMAX); test_feature_encode = test_feature_encode.reshape((test_feature_encode.shape[0], -1))
    # get str encode
    all_encode = []
    for i in range(train_feature_encode.shape[0]):
        reneencode = ""
        for j in range(train_feature_encode.shape[1]):
            reneencode += str(train_feature_encode[i, j])
        all_encode.append(reneencode)
    for i in range(test_feature_encode.shape[0]):
        reneencode = ""
        for j in range(test_feature_encode.shape[1]):
            reneencode += str(test_feature_encode[i, j])
        all_encode.append(reneencode)
    all_encode_counter = Counter(all_encode); print(all_encode_counter)

"""
main:
    main func
"""
def main(k = 10):
    mainH = 4
    # get trainset & testset
    # x_train, y_train, x_test, y_test = utils.load_dataset(dirpath = PREDATASET); print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)
    import pandas as pd
    from sklearn.model_selection import train_test_split
    data_file = os.path.join(".", "renedataset", 'pc_coords_full_0721.csv')
    label_file = os.path.join(".", "renedataset", 'global_label_full_0721.csv')
    all_feature = pd.read_csv(data_file, encoding='utf-8', engine='python', header=None)
    all_feature.drop([0], axis=1, inplace=True)
    all_label = pd.read_csv(label_file, encoding='utf-8', engine='python', header=None)
    all_label.drop([0], axis=1, inplace=True)

    all_feature = np.array(all_feature)
    all_label = np.array(all_label).reshape(-1)
    labels = np.unique(all_label)
    print (all_feature.shape)
    print (all_label.shape)
    print (labels.shape)
    train_feature = []
    db_label = []
    test_feature = []
    query_label = []
    for i in range(len(labels)):
        idx = np.where(all_label==labels[i])[0]
        if len(idx) > 1:
            X_train, X_test, y_train, y_test = train_test_split(all_feature[idx,:], all_label[idx],test_size=0.15, random_state=0)
            point = int(X_train.shape[0]*0.42)
            if point <= 0:
                point = 1
            train_feature.extend(X_train[0:point,:].reshape(-1, all_feature.shape[1]))
            db_label.extend(y_train[0:point])
            test_feature.extend(X_test)
            query_label.extend(y_test)
    train_feature = np.array(train_feature).reshape(-1, all_feature.shape[1])
    test_feature = np.array(test_feature).reshape(-1, all_feature.shape[1])
    db_label = np.array(db_label).reshape(-1, )
    query_label = np.array(query_label).reshape(-1, )
    # get max
    train_feature_max = np.max(train_feature)
    test_feature_max = np.max(test_feature)
    feature_max = max(train_feature_max, test_feature_max)
    # remap trainset to Z
    train_feature_remap = utils.remap(train_feature, (0, 2**W-1), feature_max)
    # remap testset to Z
    test_feature_remap = utils.remap(test_feature, (0, 2**W-1), feature_max)
    # get indexes
    indexes = _get_index(train_feature_remap, test_feature_remap, h = mainH, k = k)
    # get P_count & P
    P = 0
    P_count = 0
    for i in range(len(indexes)):
        index = indexes[i]
        if len(index) != 0:
            P_count += 1
            label = query_label[i]
            match_label = db_label[index]
            P += 1 if np.sum(match_label == label) > 0 else 0
    print(str((P/P_count)) + "," + str((P_count/len(indexes))))

if __name__ == "__main__":
    get_rene()
