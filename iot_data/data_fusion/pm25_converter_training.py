# -*- coding: UTF-8 -*-from argparse import ArgumentParser
import os
import pickle
from argparse import ArgumentParser

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import GridSearchCV
from sklearn.kernel_ridge import KernelRidge
from sklearn.svm import SVR
import numpy as np
import pandas as pd



from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split


def best_svr_model(train_x, train_y):
    svr = GridSearchCV(SVR(kernel='rbf', gamma=0.1), cv=5,
                       n_jobs=-1, verbose=3,
                       param_grid={"C": [1e0, 1e1, 1e2, 1e3],
                                   "gamma": np.logspace(-2, 2, 5),'kernel':['rbf']})
    svr.fit(train_x, train_y)
    print(svr.best_score_)
    return svr.best_estimator_

def best_krr_model(train_x, train_y):
    kr = GridSearchCV(KernelRidge(kernel='rbf', gamma=0.1), cv=5,
                      n_jobs=-1, verbose=3,
                      param_grid={"alpha": [1e0, 0.1, 1e-2, 1e-3],
                                  "gamma": np.logspace(-2, 2, 5),'kernel':['rbf']})
    kr.fit(train_x, train_y)
    print(kr.best_score_)
    return kr.best_estimator_


class PM25Converter(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.svr_model = None
        self.krr_model = None
    def fit(self,target_pm25, dst_pm25):
        self.svr_model = best_svr_model(target_pm25, dst_pm25)
        self.krr_model = best_krr_model(target_pm25, dst_pm25)

    def transform(self, pm25_to_be_converted):
        assert self.svr_model is None or self.krr_model is None, 'Use fit() to train the model first'
        _input = np.array([pm25_to_be_converted])
        converted_pm25 = (self.svr_model.predict(_input)[0] +
                          self.krr_model.predict(_input)[0]) / 2

        return converted_pm25

def training_converter(prefix, n_km_feature):
    feature_filename = './data/training_feature_using_nearby_{}_km_data.csv'.format(n_km_feature)
    output_filename = './models/{}_svr_trained_using_{}_records_with_rmse_{}.pickle'

    if os.path.isfile(feature_filename):
        train_data = pd.read_csv(feature_filename)
    else:
        raise Exception('Feature data does not exist, '
                        'use prepare_training_features.py to produce one')

    train_x = train_data.trainx.values.reshape((-1, 1))
    train_y = train_data.train_y.values.reshape((-1,))

    train_x, train_y = shuffle(train_x, train_y, random_state=0)

    train_x, test_x, train_y, test_y = train_test_split(train_x, train_y, test_size=0.05)

    model = best_krr_model(train_x, train_y)
    model.fit(train_x, train_y)


    y_pred = model.predict(test_x)
    rmse = np.sqrt((test_y - y_pred) ** 2).mean()



    output_filename = output_filename.format(prefix, len(train_x), rmse)

    if os.path.isfile(output_filename):
        raise Exception('Model already existed, using another filename')


    with open(output_filename, 'wb') as f:
        pickle.dump(model, f)

    print('Done training pm25 converter!')

    # index = np.where(rmse > 5)






if __name__ == '__main__':

    arg_parser = ArgumentParser()
    arg_parser.add_argument('-km', '--training_feature_using_n_km', required=True)
    arg_parser.add_argument('-m_p', '--model_prefix', required=True)
    args = vars(arg_parser.parse_args())

    n_km = args['training_feature_using_n_km']
    model_prefix = args['model_prefix']
    training_converter(model_prefix, n_km)





