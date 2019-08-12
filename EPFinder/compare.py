import pandas as pd
from sklearn.cluster import KMeans

from tree_process import *
from file_process import *


def compare_tree(root_node1, root_node2):
    collector1 = NodeVisitorLevel(root_node1)
    collector1.generic_visit_level()
    collector1.process_tree()
    collector2 = NodeVisitorLevel(root_node2)
    collector2.generic_visit_level()
    collector2.process_tree()
    maxNum = max(collector1.nodesNum,collector2.nodesNum)
    values = [[] for i in range(0,maxNum+1)]
    for key in collector2.d.keys():
        values[collector2.d[key][0]].append(key)
    collector1.others_dict = collector2.d
    collector1.others_values = values
    collector1.generic_visit(root_node1)
    if collector1.nodesNum+collector2.nodesNum==0:
        return 0
    return float(collector1.same_nodes)/(collector1.nodesNum+collector2.nodesNum)


def detect_pair(code1, code2):
    try:
        root1 = ast.parse(code1)
        root2 = ast.parse(code2)
    except Exception as e:
        print(e)
        return 0
    return compare_tree(root1, root2)


def detect_directory(root, number, th):
    codes = []
    asts = []
    vectors = []
    codes_path = get_all_py_path(root)
    codes_path_new = []
    collectors = []
    for path in codes_path:
        try:
            f = open(path,'r+',errors='ignore')
            code = f.read()
            f.close()
            codes.append(code)
            root_node = ast.parse(code)
            collector = FuncNodeCollector()
            collector.visit(root_node)
            vector = [collector._expr, collector._call, collector._classdef,
                      collector._funcdef, collector._name, collector._attribute]
            levelVisit = NodeVisitorLevel(root_node)
            levelVisit.generic_visit_level()
            levelVisit.process_tree()
            if max(vector) == min(vector):
                continue
            Z_ScoreNormalization(vector)
            asts.append(root_node)
            collectors.append(collector)
            codes_path_new.append(path)
            vectors.append(vector)
        except Exception as err:
            print(err)
    X = np.array(vectors)

    d = pd.DataFrame(X)
    d.head()
    # 聚类
    mod = KMeans(n_clusters=number, n_jobs=4, max_iter=500)  # 聚成3类数据,并发数为4，最大循环次数为500
    mod.fit_predict(d)  # y_pred表示聚类的结果

    # 聚成3类数据，统计每个聚类下的数据量，并且求出他们的中心
    r1 = pd.Series(mod.labels_).value_counts()
    r2 = pd.DataFrame(mod.cluster_centers_)
    r = pd.concat([r2, r1], axis=1)
    r.columns = list(d.columns) + [u'number']
    print(r)

    # 给每一条数据标注上被分为哪一类
    r = pd.concat([d, pd.Series(mod.labels_, index=d.index)], axis=1)
    r.columns = list(d.columns) + [u'kind']
    print(r)
    labels = list(mod.labels_)

    dict = {}
    dict2 = {}
    dict3 = {}
    dic_root = {}
    for i in range(0,len(labels)):
        if labels[i] in dict.keys():
            array = dict[labels[i]]
            array.append(codes_path_new[i])
            dict[labels[i]] = array
            array = dict2[labels[i]]
            array.append(collectors[i])
            dict2[labels[i]] = array
            array = dict3[labels[i]]
            array.append(codes[i])
            dict3[labels[i]] = array

            roots = dic_root[labels[i]]
            roots.append(asts[i])
            dic_root[labels[i]] = roots
        else:
            array = []
            array.append(codes_path_new[i])
            dict[labels[i]] = array
            array = []
            array.append(collectors[i])
            dict2[labels[i]] = array
            array = []
            array.append(codes[i])
            dict3[labels[i]] = array

            roots = []
            roots.append(asts[i])
            dic_root[labels[i]] = roots
    for key in dict.keys():
        if len(dict[key])<2:
            continue
        for i in range(0,len(dict[key])-1):
            for j in range(i+1,len(dict[key])):
                sim = compare_tree(dic_root[key][i],dic_root[key][j])
                if sim>th:
                    print(dict[key][i])
                    print(dict[key][j])
                    print(sim)


def detect_content(notes,codes,number,th):
    asts = []
    vectors = []
    collectors = []
    for code in codes:
        try:
            root_node = ast.parse(code)
            collector = FuncNodeCollector()
            collector.visit(root_node)
            vector = [collector._expr, collector._call, collector._classdef,
                      collector._funcdef, collector._name, collector._attribute]
            levelVisit = NodeVisitorLevel(root_node)
            levelVisit.generic_visit_level()
            levelVisit.process_tree()
            if max(vector) == min(vector):
                continue
            Z_ScoreNormalization(vector)
            asts.append(root_node)
            collectors.append(collector)
            vectors.append(vector)
        except Exception as err:
            print(err)
    X = np.array(vectors)

    d = pd.DataFrame(X)
    d.head()
    # 聚类
    mod = KMeans(n_clusters=number, n_jobs=4, max_iter=500)  # 聚成3类数据,并发数为4，最大循环次数为500
    mod.fit_predict(d)  # y_pred表示聚类的结果

    # 聚成3类数据，统计每个聚类下的数据量，并且求出他们的中心
    r1 = pd.Series(mod.labels_).value_counts()
    r2 = pd.DataFrame(mod.cluster_centers_)
    r = pd.concat([r2, r1], axis=1)
    r.columns = list(d.columns) + [u'number']
    print(r)

    # 给每一条数据标注上被分为哪一类
    r = pd.concat([d, pd.Series(mod.labels_, index=d.index)], axis=1)
    r.columns = list(d.columns) + [u'kind']
    print(r)
    labels = list(mod.labels_)

    dict = {}
    dict2 = {}
    dict3 = {}
    dic_root = {}
    for i in range(0, len(labels)):
        if labels[i] in dict.keys():
            array = dict[labels[i]]
            array.append(notes[i])
            dict[labels[i]] = array
            array = dict2[labels[i]]
            array.append(collectors[i])
            dict2[labels[i]] = array
            array = dict3[labels[i]]
            array.append(codes[i])
            dict3[labels[i]] = array

            roots = dic_root[labels[i]]
            roots.append(asts[i])
            dic_root[labels[i]] = roots
        else:
            array = []
            array.append(notes[i])
            dict[labels[i]] = array
            array = []
            array.append(collectors[i])
            dict2[labels[i]] = array
            array = []
            array.append(codes[i])
            dict3[labels[i]] = array

            roots = []
            roots.append(asts[i])
            dic_root[labels[i]] = roots
    for key in dict.keys():
        if len(dict[key]) < 2:
            continue
        for i in range(0, len(dict[key]) - 1):
            for j in range(i + 1, len(dict[key])):
                sim = compare_tree(dic_root[key][i], dic_root[key][j])
                if sim > th:
                    print(dict[key][i])
                    print(dict[key][j])
                    print(sim)

