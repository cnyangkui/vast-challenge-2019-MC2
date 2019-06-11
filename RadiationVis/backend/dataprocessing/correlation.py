# -*- coding: utf-8 -*-
import csv
import pandas as pd
import numpy as np
from sklearn import manifold
from sklearn.preprocessing import RobustScaler

'''
    使用空缺值之前的四个值的均值进行补全
'''
def Matrix_Completion(m):

    index = np.argwhere(np.isnan(m))
    [rows1, cols1] = index.shape
    for i in range(rows1):
        # tmp = m[index[i,0],index[i,1]]
        if i < 1:
            m[index[i, 0], index[i, 1]] = 0
        elif i < 4:
            m[index[i, 0], index[i, 1]] = m[index[i, 0] - 1, index[i, 1]]
        else:
            m[index[i, 0], index[i, 1]] = 0.25 * (
                m[index[i, 0] - 1, index[i, 1]] + m[index[i, 0] - 2, index[i, 1]] + m[index[i, 0] - 3, index[i, 1]] + m[
                    index[i, 0] - 4, index[i, 1]])
    return m

'''
    余弦距离
'''
def Distance_Metric_Cos(m):
    feature_matrix = np.eye(59)
    [rows2, cols2] = feature_matrix.shape
    for i in range(rows2):
        for j in range(cols2):
            tmp1 = m[:, i].T.tolist()
            tmp2 = m[:, j].T.tolist()

            numerator = sum([(a * b) for (a, b) in zip(tmp1, tmp2)])
            sq1 = np.sqrt(sum([np.power(e, 2) for e in tmp1]))
            sq2 = np.sqrt(sum([np.power(e, 2) for e in tmp2]))
            denominator = sq1 * sq2
            ac = numerator * 1.0 / denominator

            feature_matrix[i, j] = ac
    return feature_matrix

'''减弱异常'''
def Centralized_with_Outliers(m):
    transformer = RobustScaler().fit(m)
    return transformer.transform(m)

'''降维方法： MDS'''
def Dimension_Reduction(feature_matrix):
    mds = manifold.MDS(n_components=2).fit_transform(feature_matrix)
    mds.tolist()
    return mds

if __name__ == '__main__':
    df = pd.read_csv('data/dynamic.csv')
    m = df.iloc[:, 1:].values

    df2 = pd.read_csv('data/static.csv')
    n = df2.iloc[:, 1:].values
    list_n = df2.columns.tolist()
    list_n.remove(list_n[0])
    for i in range(len(list_n)):
        list_n[i] = 's' + list_n[i]


    mn = np.hstack((m,n))

    mn = Matrix_Completion(mn)
    col_mean = np.mean(mn, axis=0).tolist()
    col_var = np.std(mn, axis=0).tolist()
    print(col_mean, col_var)

    feature_matrix = Distance_Metric_Cos(mn)



    mds = Dimension_Reduction(feature_matrix)
    detectorS = []
    i = 0
    for data in mds:
        detectorS.append([data[0], data[1], col_mean[i], col_var[i]])
        i = i + 1

    # k = 0
    # for j in range(50, 59):
    #     detectorS[j][0] = list_n[k]
    #     k = k + 1


    for detector in detectorS:
        print(detector)

    # save as csv
    # test = pd.DataFrame(data=detectorS)
    # test.to_csv('data/result.csv', encoding='utf-8')



