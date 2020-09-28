# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 13:03:26 2020

@author: 王靖豪
"""

import pandas as pd
import numpy as np
import scipy

data = pd.read_csv('u.data', sep='\t', names=['user_id','item_id','rating','timestamp'])

data['user_id'] = data['user_id'].astype('str')
data['item_id'] = data['item_id'].astype('str')

users = data['user_id'].unique() #list of all users
movies = data['item_id'].unique() #list of all movies

test = pd.DataFrame(columns=data.columns)
train = pd.DataFrame(columns=data.columns)
test_ratio = 0.2 #fraction of data to be used as test set.

for u in users:
    temp = data[data['user_id'] == u]
    n = len(temp)
    test_size = int(test_ratio*n)
    
    temp = temp.sort_values('timestamp').reset_index()
    temp.drop('index', axis=1, inplace=True)
        
    dummy_test = temp.ix[n-1-test_size :]
    dummy_train = temp.ix[: n-2-test_size]
        
    test = pd.concat([test, dummy_test])
    train = pd.concat([train, dummy_train])


from scipy.linalg import sqrtm

def create_utility_matrix(data, formatizer = {'user':0, 'item': 1, 'value': 2}):
    """
        :param data:      Array-like, 2D, nx3
        :param formatizer:pass the formatizer
        :return:          utility matrix (n x m), n=users, m=items
    """

    user_field = formatizer['user']
    item_field = formatizer['item']
    value_field = formatizer['value']
    
    user_list = data.iloc[:,user_field].tolist()
    item_list = data.iloc[:,item_field].tolist()
    value_list = data.iloc[:,value_field].tolist()
    
    users = list(set(data.iloc[:,user_field]))
    items = list(set(data.iloc[:,item_field]))
    
    user_index = {users[i]: i for i in range(len(users))}
    
    pd_dict = {item: [np.nan for i in range(len(users))] for item in items}
    
    for i in range(0,len(data)):
        user = user_list[i]
        item = item_list[i]
        value = value_list[i]
        pd_dict[item][user_index[user]] = value
    
    X = pd.DataFrame(pd_dict)
    X.index = users
        
    itemcols = list(X.columns)
    item_index = {itemcols[i]: i for i in range(len(itemcols))}
    
    # users_index gives us a mapping of user_id to index of user
    # items_index provides the same for items
    
    return X, user_index, item_index 

create_utility_matrix(data, formatizer = {'user':0, 'item': 1, 'value': 2})


def svd(train, k):
    
    utilMat = np.array(train)
    
    # the nan or unavailable entries are masked
    mask = np.isnan(utilMat)
    masked_arr = np.ma.masked_array(utilMat, mask)
    
    # nan entries will be replaced by the average rating for each item
    item_means = np.mean(masked_arr, axis=0)
    utilMat = masked_arr.filled(item_means)
    
    x = np.tile(item_means, (utilMat.shape[0],1))
    # we remove the per item average from all entries.
    # the above mentioned nan entries will be essentially zero now
    utilMat = utilMat - x
    
    # U and V are user and item features
    U, Σ, VT = np.linalg.svd(utilMat, full_matrices=False)
    Σ = np.diag(Σ)
    
    # we take only the k most significant features
    Σ = Σ[0:k,0:k]
    U = U[:,0:k]
    VT = VT[0:k,:]
    
    λ = sqrtm(Σ)
    
    Uλk = np.dot(U,λ)
    λkVT = np.dot(λ,VT)
    
    UΣkVT = np.dot(Uλk, λkVT)
    
    UΣkVT = UΣkVT + x
    
    print("svd done")
    
    return UΣkVT


def rmse(true, pred):
    x = true - pred
    return sum([xi*xi for xi in x])/len(x)

# to test the performance over a different number of features
    
no_of_features = [8,10,12,14,17]

utilMat, user_index, item_index = create_utility_matrix(train)


for f in no_of_features: 
    
    svd_out = svd(utilMat, f)
    
    pred = [] #to store the predicted ratings
    
    for _,row in test.iterrows():
        
        user = row['user_id']
        item = row['item_id']
        
        u_index = user_index[user]
        
        if item in item_index:
            i_index = item_index[item]
            pred_rating = svd_out[u_index, i_index]
        else:
            pred_rating = np.mean(svd_out[u_index, :])
            
    print(rmse(test['rating'], pred_rating))


