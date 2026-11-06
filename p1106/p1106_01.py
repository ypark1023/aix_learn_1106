from sklearn import svm, metrics


data = [
        [0,0],[0,1],[1,0],[1,1]
]

label = [0,1,1,0]

test_data = [ [0,0], [1,0]]
test_label = [0,1]


clf = svm.SVC()      #알고리즘 섬택
clf.fit(data,label) #알고리즘 학습

#데이터 예측
results = clf.predict(test_data)
print('결과:', results)

score = metrics.accuracy_score(test_label, results)
print('정답률:', score)


# 결과값은 아래와 같다
# 결과: [0 1]
# 정답률: 1.0