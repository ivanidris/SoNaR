import core
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import confusion_matrix
import numpy as np


db = core.connect()
bing_searches = db['bing_searches']
x = []
y = []

for row in bing_searches.all():
    x.append("{0}\n{1}".format(row['title'], row['description']))
    y.append(row['flag'] == 'Use')

vectorizer = TfidfVectorizer(sublinear_tf=True, stop_words='english')

train_x, test_x, train_y, test_y = train_test_split(x, y,
                                                    random_state=43)
train_features = vectorizer.fit_transform(train_x)
test_features = vectorizer.transform(test_x)
lr = LogisticRegression()
lr.fit(train_features, train_y)
preds = lr.predict(test_features)
print('Test Accuracy', accuracy_score(test_y, preds))
print('Test Kappa', cohen_kappa_score(test_y, preds))
print('Confusion Matrix\n', confusion_matrix(test_y, preds))

feature_names = np.array(vectorizer.get_feature_names())

bottom10 = np.argsort(lr.coef_[0])[:10]
print("Possible negative keywords {}".format(feature_names[bottom10]))
