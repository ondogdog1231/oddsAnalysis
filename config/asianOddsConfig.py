import json
import sys
import os

# https://betfair-datascientists.github.io/modelling/EPLmlPython/
projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor

from xgboost import XGBClassifier

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression


class config:

    def model_list(self):
        classifiers = {
            16: {
                # 荷甲
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
                "RandomForest": RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1, random_state=42),
                "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
                "SVC": SVC(gamma=2, C=1, probability=True, random_state=42),
            },
            9: {
                # 德乙
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                # "SVC": SVC(gamma=2, C=1, probability=True, random_state=42),
                # "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
                "RandomForest": RandomForestClassifier(max_depth=2, n_estimators=17, max_features=4, random_state=42),
            },
            34: {
                # 意大利甲组
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
                # "Ada": AdaBoostClassifier(random_state=42),
                # "KNN": KNeighborsClassifier(3),
            },
            31: {
                # 西甲
                "RandomForest": RandomForestClassifier(max_depth=1, n_estimators=12, max_features=4, random_state=42),
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
                "SVC": SVC(gamma=2, C=1, probability=True, random_state=42),
            },
            36: {
                # "RandomForest": RandomForestClassifier(max_depth=1, n_estimators=9, max_features=15, random_state=42),
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                # "KNN": KNeighborsClassifier(3),
                # "DecisionTree": DecisionTreeClassifier(max_depth=5, random_state=42),
                "QDA": QuadraticDiscriminantAnalysis()

            },
            11: {
                "RandomForest": RandomForestClassifier(max_depth=1, n_estimators=65, max_features=15, random_state=42),
                "QDA": QuadraticDiscriminantAnalysis(),
                "NaiveBayes": GaussianNB(),

            },
            103: {
                # "KNN": KNeighborsClassifier(3),
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
                # "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                # "QDA": QuadraticDiscriminantAnalysis(),

                # "svc": SVC(gamma=10, C=10, probability=True, random_state=42),
            },
            17: {
                # 荷乙
                "Neural_Net": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
            },
            39: {
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "Neural_Net": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
                "DecisionTree": DecisionTreeClassifier(max_depth=5, random_state=42),
            },
            4: {
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "SVM": SVC(gamma=2, C=1, probability=True, random_state=42),
                "decisionTress": DecisionTreeClassifier(max_depth=5, random_state=42)
            },
            8: {
                # 德甲
                "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
                "SVM": SVC(gamma=2, C=1, probability=True, random_state=42),
                "decisionTress": DecisionTreeClassifier(max_depth=5, random_state=42)
            },
            37: {
                # 英冠
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "decisionTress": DecisionTreeClassifier(max_depth=5, random_state=42)
            },
            284: {
                # 日职乙
                "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
                "decisionTress": DecisionTreeClassifier(max_depth=5, random_state=42),
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
            },
            29: {

                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
                "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
            },
            23: {
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
                "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
                "AdaBoost": AdaBoostClassifier(random_state=42),
            },
            25: {
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "decisionTress": DecisionTreeClassifier(max_depth=5, random_state=42),
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),

            },
            468: {
                "KNN": KNeighborsClassifier(3),
                "RandomForest": RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1, random_state=42),
                # "AdaBoost": AdaBoostClassifier(random_state=42),
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
            },
            279: {
                "SVM": SVC(gamma=2, C=1, probability=True, random_state=42),
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
            },
            113: {
                "SVM": SVC(gamma=2, C=1, probability=True, random_state=42),
                "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
            },
            140: {
                "NeuralNet": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
            },
            273: {
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
            },
            10: {
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
                "decisionTress": DecisionTreeClassifier(max_depth=5, random_state=42),
            },
            75:{
                "LogisticRegression": LogisticRegression(solver='lbfgs', max_iter=10000),
                "Gaussian_Process": GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
            }

        }
        return classifiers
