
import sklearn.pipeline as MLpipeline

import sklearn.model_selection as model_selection
import sklearn.ensemble as ensemble
import sklearn.linear_model as linear_model
import sklearn.naive_bayes as naive_bayes
import sklearn.neighbors as neighbors
import sklearn.svm as svm

import pandas as pd
from sklearn import preprocessing
import sklearn.tree as tree
import sklearn.discriminant_analysis as discriminant_analysis
import sklearn.gaussian_process as gaussian_process
import time as time

class ClassifierEnsemble:

    one_weight = 0.0

    fitClassifiers = []

    # https://www.kaggle.com/ldfreeman3/a-data-science-framework-to-achieve-99-accuracy
    MLA = [
        # Ensemble Methods: http://scikit-learn.org/stable/modules/ensemble.html
        ('ada', ensemble.AdaBoostClassifier()),
        ('bc', ensemble.BaggingClassifier()),
        ('etc', ensemble.ExtraTreesClassifier()),
        ('gbc', ensemble.GradientBoostingClassifier()),
        ('rfc', ensemble.RandomForestClassifier()),

        # Gaussian Processes: http://scikit-learn.org/stable/modules/gaussian_process.html#gaussian-process-classification-gpc
        ('gpc', gaussian_process.GaussianProcessClassifier()),

        # GLM: http://scikit-learn.org/stable/modules/linear_model.html#logistic-regression
        ('lr', linear_model.LogisticRegressionCV()),

        # Navies Bayes: http://scikit-learn.org/stable/modules/naive_bayes.html
        ('bnb', naive_bayes.BernoulliNB()),
        ('gnb', naive_bayes.GaussianNB()),

        # Nearest Neighbor: http://scikit-learn.org/stable/modules/neighbors.html
        ('knn', neighbors.KNeighborsClassifier()),

        # SVM: http://scikit-learn.org/stable/modules/svm.html
        ('svc', svm.SVC(probability=True)),

        # xgboost: http://xgboost.readthedocs.io/en/latest/model.html
        #('xgb', XGBClassifier())

        # lightGBM
        #('lgbm', LightGBMClassifier or whatever)

    ]

    # GridSearchCV parameter values will go in here, one set for each classifier
    grid_n_estimator = [100, 200, 300, 400]
    grid_ratio = [.1, .25, .5, .75, 1.0]
    grid_learn = [.01, .03, .05, .1, .25]
    grid_max_depth = [2, 4, 6, 8, 10, None]
    grid_min_samples = [5, 10, .03, .05, .10]
    grid_criterion = ['gini', 'entropy']
    grid_bool = [True, False]
    grid_seed = [111]


    parameterCandidates = [
        [{
            # AdaBoostClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html
            'n_estimators': grid_n_estimator,  # default=50
            'learning_rate': grid_learn,  # default=1
            'algorithm': ['SAMME', 'SAMME.R'], #default=’SAMME.R
            'random_state': grid_seed
        }],

        [{
            # BaggingClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.BaggingClassifier.html#sklearn.ensemble.BaggingClassifier
            'n_estimators': grid_n_estimator,  # default=10
            'max_samples': grid_ratio,  # default=1.0
            'random_state': grid_seed
        }],

        [{
            # ExtraTreesClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html#sklearn.ensemble.ExtraTreesClassifier
            'n_estimators': grid_n_estimator,  # default=10
            'criterion': grid_criterion,  # default=”gini”
            'max_depth': grid_max_depth,  # default=None
            'random_state': grid_seed
        }],

        [{
            # GradientBoostingClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html#sklearn.ensemble.GradientBoostingClassifier
            # 'loss': ['deviance', 'exponential'], #default=’deviance’
            'learning_rate': grid_learn,
        # default=0.1 -- 12/31/17 set to reduce runtime -- The best parameter for GradientBoostingClassifier is {'learning_rate': 0.05, 'max_depth': 2, 'n_estimators': 300, 'random_state': 0} with a runtime of 264.45 seconds.
            'n_estimators': grid_n_estimator,
        # default=100 -- 12/31/17 set to reduce runtime -- The best parameter for GradientBoostingClassifier is {'learning_rate': 0.05, 'max_depth': 2, 'n_estimators': 300, 'random_state': 0} with a runtime of 264.45 seconds.
            # 'criterion': ['friedman_mse', 'mse', 'mae'], #default=”friedman_mse”
            'max_depth': grid_max_depth,  # default=3
            'random_state': grid_seed
        }],

        [{
            # RandomForestClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier
            'n_estimators': grid_n_estimator,  # default=10
            'criterion': grid_criterion,  # default=”gini”
            'max_depth': grid_max_depth,  # default=None
            'oob_score': [True],
        # default=False -- 12/31/17 set to reduce runtime -- The best parameter for RandomForestClassifier is {'criterion': 'entropy', 'max_depth': 6, 'n_estimators': 100, 'oob_score': True, 'random_state': 0} with a runtime of 146.35 seconds.
            'random_state': grid_seed
        }],

        [{
            # GaussianProcessClassifier
            'max_iter_predict': grid_n_estimator,  # default: 100
            'random_state': grid_seed
        }],

        [{
            # LogisticRegressionCV - http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegressionCV.html#sklearn.linear_model.LogisticRegressionCV
            'fit_intercept': grid_bool,  # default: True
            # 'penalty': ['l1','l2'],
            'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],  # default: lbfgs
            'random_state': grid_seed
        }],

        [{
            # BernoulliNB - http://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.BernoulliNB.html#sklearn.naive_bayes.BernoulliNB
            'alpha': grid_ratio,  # default: 1.0
        }],

        # GaussianNB -
        [{}],

        [{
            # KNeighborsClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html#sklearn.neighbors.KNeighborsClassifier
            'n_neighbors': [1, 2, 3, 4, 5, 6, 7],  # default: 5
            'weights': ['uniform', 'distance'],  # default = ‘uniform’
            'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute']
        }],

        [{
            # SVC - http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC
            # http://blog.hackerearth.com/simple-tutorial-svm-parameter-tuning-python-r
            # 'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
            'C': [1, 2, 3, 4, 5],  # default=1.0
            'gamma': grid_ratio,  # edfault: auto
            'decision_function_shape': ['ovo', 'ovr'],  # default:ovr
            'probability': [True],
            'random_state': grid_seed
        }]

        # [{
        #     # XGBClassifier - http://xgboost.readthedocs.io/en/latest/parameter.html
        #     'learning_rate': grid_learn,  # default: .3
        #     'max_depth': [1, 2, 4, 6, 8, 10],  # default 2
        #     'n_estimators': grid_n_estimator,
        #     'seed': grid_seed
        # }]
    ]

    presetParameters = [
        [{
            # AdaBoostClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html
            'n_estimators': grid_n_estimator,  # default=50
            'learning_rate': grid_learn,  # default=1
            'algorithm': ['SAMME', 'SAMME.R'],  # default=’SAMME.R
            'random_state': grid_seed
        }],

        [{
            # BaggingClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.BaggingClassifier.html#sklearn.ensemble.BaggingClassifier
            'n_estimators': grid_n_estimator,  # default=10
            'max_samples': grid_ratio,  # default=1.0
            'random_state': grid_seed
        }],

        [{
            # ExtraTreesClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html#sklearn.ensemble.ExtraTreesClassifier
            'n_estimators': grid_n_estimator,  # default=10
            'criterion': grid_criterion,  # default=”gini”
            'max_depth': grid_max_depth,  # default=None
            'random_state': grid_seed
        }],

        [{
            # GradientBoostingClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html#sklearn.ensemble.GradientBoostingClassifier
            # 'loss': ['deviance', 'exponential'], #default=’deviance’
            'learning_rate': grid_learn,
            # default=0.1 -- 12/31/17 set to reduce runtime -- The best parameter for GradientBoostingClassifier is {'learning_rate': 0.05, 'max_depth': 2, 'n_estimators': 300, 'random_state': 0} with a runtime of 264.45 seconds.
            'n_estimators': grid_n_estimator,
            # default=100 -- 12/31/17 set to reduce runtime -- The best parameter for GradientBoostingClassifier is {'learning_rate': 0.05, 'max_depth': 2, 'n_estimators': 300, 'random_state': 0} with a runtime of 264.45 seconds.
            # 'criterion': ['friedman_mse', 'mse', 'mae'], #default=”friedman_mse”
            'max_depth': grid_max_depth,  # default=3
            'random_state': grid_seed
        }],

        [{
            # RandomForestClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier
            'n_estimators': grid_n_estimator,  # default=10
            'criterion': grid_criterion,  # default=”gini”
            'max_depth': grid_max_depth,  # default=None
            'oob_score': [True],
            # default=False -- 12/31/17 set to reduce runtime -- The best parameter for RandomForestClassifier is {'criterion': 'entropy', 'max_depth': 6, 'n_estimators': 100, 'oob_score': True, 'random_state': 0} with a runtime of 146.35 seconds.
            'random_state': grid_seed
        }],

        [{
            # GaussianProcessClassifier
            'max_iter_predict': grid_n_estimator,  # default: 100
            'random_state': grid_seed
        }],

        [{
            # LogisticRegressionCV - http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegressionCV.html#sklearn.linear_model.LogisticRegressionCV
            'fit_intercept': grid_bool,  # default: True
            # 'penalty': ['l1','l2'],
            'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],  # default: lbfgs
            'random_state': grid_seed
        }],

        [{
            # BernoulliNB - http://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.BernoulliNB.html#sklearn.naive_bayes.BernoulliNB
            'alpha': grid_ratio,  # default: 1.0
        }],

        # GaussianNB -
        [{}],

        [{
            # KNeighborsClassifier - http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html#sklearn.neighbors.KNeighborsClassifier
            'n_neighbors': [1, 2, 3, 4, 5, 6, 7],  # default: 5
            'weights': ['uniform', 'distance'],  # default = ‘uniform’
            'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute']
        }],

        [{
            # SVC - http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC
            # http://blog.hackerearth.com/simple-tutorial-svm-parameter-tuning-python-r
            # 'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
            'C': [1, 2, 3, 4, 5],  # default=1.0
            'gamma': grid_ratio,  # edfault: auto
            'decision_function_shape': ['ovo', 'ovr'],  # default:ovr
            'probability': [True],
            'random_state': grid_seed
        }]

        # [{
        #     # XGBClassifier - http://xgboost.readthedocs.io/en/latest/parameter.html
        #     'learning_rate': grid_learn,  # default: .3
        #     'max_depth': [1, 2, 4, 6, 8, 10],  # default 2
        #     'n_estimators': grid_n_estimator,
        #     'seed': grid_seed
        # }]
    ]

    def calculate_weights(self, trainingDataFrame, labelColumn):

        #global one_weight

        trainingLabels = trainingDataFrame[labelColumn].values

        one_count = 0.0
        zero_count = 0.0

        for i in trainingLabels:
            if i == 1:
                one_count += 1.0
            if i == 0:
                zero_count += 1.0

        if one_count > zero_count:
            self.one_weight = one_count / zero_count

        if one_count < zero_count:
            self.one_weight = zero_count / one_count

        print("One Count: ", one_count)
        print("Zero Count: ", zero_count)
        print("One Weight: ", self.one_weight)
        print("")

        #return one_weight

    def trainAllClassifiers(self, trainingDataFrame, predictorColumns, labelColumn):

        self.calculate_weights(trainingDataFrame, labelColumn)

        trainingInputs = trainingDataFrame[predictorColumns]
        #trainingInputs = preprocessing.normalize(trainingInputs, axis=0)

        trainingLabels = trainingDataFrame[labelColumn]

        cv_split = model_selection.ShuffleSplit(n_splits=10, test_size=.3, train_size=.7, random_state=0)

        start_total = time.perf_counter()

        messages = []

        normal_names = ["SVC", "MLPClassifier", "NearestNeighbors", "SGDClassifier"]

        for algo, parameters in zip(self.MLA, self.parameterCandidates):

            inputs = trainingInputs

            if type(algo).__name__ in normal_names:
                inputs = preprocessing.normalize(trainingInputs, axis=0)

            if algo[0] == "etc" or algo[0] == "rfc" or algo[0] == "lr" or algo[0] == "svc":
                parameters[0]["class_weight"] = [{1: self.one_weight}]
            #
            # print(parameters)
            # print("")

            start = time.perf_counter()
            best_search = model_selection.GridSearchCV(
                estimator=algo[1],
                param_grid=parameters,
                cv=cv_split,
                scoring='roc_auc',
                n_jobs=-1)


            best_search.fit(inputs, trainingLabels)
            run = time.perf_counter() - start

            best_param = best_search.best_params_
            best_score = best_search.best_score_
            # print('The best parameter for {} is {} with a runtime of {:.2f} seconds, score of {:.2f}'.format(algo[1].__class__.__name__,
            #
            #                                                             best_param, run, best_score))
            messages.append('The best parameter for {} is {} with a runtime of {:.2f} seconds, score of {:.2f}'.format(algo[1].__class__.__name__,
                                                                            best_param, run, best_score))

            algo[1].set_params(**best_param)

            fitModel = algo[1].fit(trainingDataFrame[predictorColumns],
                       trainingDataFrame[labelColumn])

            self.fitClassifiers.append(fitModel)

        run_total = time.perf_counter() - start_total

        print(*messages, sep='\n')
        print('Total optimization time was {:.2f} minutes.'.format(run_total / 60))
        print('-' * 10)


        return None

    def getAndScoreVotingEnsemble(self, trainingDataFrame, predictorColumns, labelColumn, votingMethod="hard"):

        trainingInputs = trainingDataFrame[predictorColumns]
        #trainingInputs = preprocessing.normalize(trainingInputs, axis=0)

        trainingLabels = trainingDataFrame[labelColumn]

        cv_split = model_selection.ShuffleSplit(n_splits=10, test_size=.3, train_size=.7, random_state=0)

        voter = ensemble.VotingClassifier(estimators=self.MLA,
                                               voting=votingMethod)

        voter_cv = model_selection.cross_validate(voter,
                                                  trainingInputs,
                                                  trainingLabels,
                                                  cv = cv_split)

        voter.fit(trainingDataFrame[predictorColumns],
                       trainingDataFrame[labelColumn])

        print("{} Voting Training mean Score: {:.2f}".format(
            votingMethod,
            voter_cv['train_score'].mean() * 100))
        print("{} Voting Test mean Score: {:.2f}".format(
            votingMethod,
            voter_cv['test_score'].mean() * 100))
        print("{} Voting Test Score 3*std: +/- {:.2f}".format(
            votingMethod,
            voter_cv['test_score'].std() * 100 * 3))
        print('-' * 10)


    def getAllClassifierPredictions(self, testDataFrame, predictorColumns, labelColumn):
        print("doSomething")
        normal_names = ["SVC", "MLPClassifier", "NearestNeighbors", "SGDClassifier"]

        inputPredictors = testDataFrame[predictorColumns]

        inputLabels = testDataFrame[labelColumn]

        predictions_df = pd.DataFrame()

        for classifier in self.fitClassifiers:

            inputs = inputPredictors

            if type(classifier).__name__ in normal_names:
                inputs = preprocessing.normalize(inputPredictors, axis=0)

            model_preds = classifier.predict(inputs)
            #predictions_df.append(model_preds[0])
            print(type(classifier).__name__)
            print(model_preds)
            print()

        print(predictions_df)
        print()

        return predictions_df







