import numpy as np
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import os
from sklearn.model_selection import KFold  # 从sklearn导入KFold包
import concurrent.futures


# 输入数据推荐使用numpy数组，使用list格式输入会报错
def K_Flod_spilt(K, fold, data, label):
    """
    :param K: 要把数据集分成的份数。如十次十折取K=10
    :param fold: 要取第几折的数据。如要取第5折则 flod=5
    :param data: 需要分块的数据
    :param label: 对应的需要分块标签
    :return: 对应折的训练集、测试集和对应的标签
    """
    split_list = []
    kf = KFold(n_splits=K)
    for train, test in kf.split(data):
        split_list.append(train.tolist())
        split_list.append(test.tolist())
    train, test = split_list[2 * fold], split_list[2 * fold + 1]
    return data[train], data[test], label[train], label[test]  # 已经分好块的数据集


def function_1(x_tra, x_tes, y_tra, y_tes):
    CLF = make_pipeline(StandardScaler(), SVC(gamma='auto'))
    CLF.fit(x_tra, y_tra)
    Result = CLF.predict(x_tes)
    Accuracy = sklearn.metrics.accuracy_score(y_tes, Result)
    Precision = sklearn.metrics.precision_score(y_tes, Result)
    Recall = sklearn.metrics.recall_score(y_tes, Result)
    print('完成', i, '折交叉验证')
    return Accuracy, Precision, Recall


print('开始数据读取')
rumor_files = os.listdir('feature1_10')
non_files = os.listdir('feature2_10')
array = []
for rumor_file in rumor_files:
    with open('feature1_10/' + rumor_file, 'r')as f:
        temp = []
        for line in f.readlines():
            if len((line.split(',')[:-1])) != 36:
                print(len((line.split(',')[:-1])))
            for item in line.split(',')[:-1]:
                temp.append(float(item))
        array.append(temp)
for non_file in non_files:
    with open('feature2_10/' + non_file, 'r')as f:
        temp = []
        for line in f.readlines():
            for item in line.split(',')[:-1]:
                temp.append(float(item))
        array.append(temp)

X = np.array(array)
y = np.array([0] * len(rumor_files) + [1] * len(non_files))
print('完成数据读取')
accuracy = 0
precision = 0
recall = 0
# with concurrent.futures.ProcessPoolExecutor() as executor:  # 并行化处理
#     executor.map(function_1, range(10))
for i in range(5):
    X_train, X_test, y_train, y_test = K_Flod_spilt(5, i, X, y)
    clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
    clf.fit(X_train, y_train)
    result = clf.predict(X_test)
    accuracy += sklearn.metrics.accuracy_score(y_test, result)
    precision += sklearn.metrics.precision_score(y_test, result, average='weighted')
    # average='weighted' 为每个标签计算指标，并通过各类占比找到它们的加权均值（每个标签的正例数）
    recall += sklearn.metrics.recall_score(y_test, result, average='weighted')
    print('完成', (i+1)*20, '%')

accuracy /= 5
precision /= 5
recall /= 5
print('accuracy:', accuracy)  # 准确率是分类正确的样本占总样本个数的比例
print('precision:', precision)  # 精确率指模型预测为正的样本中实际也为正的样本占被预测为正的样本的比例
print('recall:', recall)  # 召回率指实际为正的样本中被预测为正的样本所占实际为正的样本的比例
print('F1 score:', 2 * precision * recall / (precision + recall))  # F1 score越高，说明模型越稳健
