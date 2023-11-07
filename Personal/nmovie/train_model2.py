import pandas as pd
from konlpy.tag import Okt as okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
import joblib
from scipy.stats import randint
import numpy as np
import re
from google.colab import files

# randomSearchVersion
def load_dataset(path):
    return pd.read_csv(path, sep='\t', encoding='utf-8')

def clean_dirty_data(data):
    count = data.isnull().value_counts()
    boolidx = data['document'].notnull()
    data = data[boolidx]
    data['document'] = data['document'].apply(lambda x : re.sub('[^가-힣ㅏ-ㅣㄱ-ㅎ]', ' ', x))
    return data

def divide_morphs(txt):
    nlp = okt()
    return nlp.morphs(txt)

# google colab path
path = './sample_data/'
review_train = load_dataset(path + 'ratings_train.txt')
cleaned_train_dataset = clean_dirty_data(review_train)

tfidfv = TfidfVectorizer(tokenizer=divide_morphs, ngram_range=(1, 3), min_df=3, max_df=0.9)
tfidfv.fit(cleaned_train_dataset['document'])
vectorized_train = tfidfv.transform(cleaned_train_dataset['document'])

review_test = load_dataset(path + 'ratings_test.txt')
cleaned_test_dataset = clean_dirty_data(review_test)
vectorized_test = tfidfv.transform(cleaned_test_dataset['document'])

sg = SGDClassifier(loss='log', max_iter=10, tol=None)
#logis = LogisticRegression()

params = {'max_iter': randint(50, 150)}
randcv = RandomizedSearchCV(sg, params, n_iter=100, n_jobs=-1, verbose=1)
randcv.fit(vectorized_train, cleaned_train_dataset['label'])
#params = {'C':[1, 3, 3.5, 4, 4.5, 5]}
#grid_cv = GridSearchCV(logis, param_grid=params, cv=5, scoring='accuracy', verbose=1)
#grid_cv.fit(vectorized_train, cleaned_train_dataset['label'])

#print(grid_cv.best_score_)
#logi_best = grid_cv.best_estimator_
sg_best = randcv.best_estimator_
print(np.max(randcv.cv_results_['mean_test_score']))
joblib.dump(sg_best, 'best_review_classifier.pkl') 
files.download('best_review_classifier.pkl')
#joblib.dump(logi_best, 'best_review_logistic.pkl') 
#files.download('best_review_logistic.pkl')
joblib.dump(tfidfv, 'tfidfVectorizer_rand.pkl')
files.download('tfidfVectorizer_rand.pkl')
sg_best.score(vectorized_test, cleaned_test_dataset['label'])