# This module contains the dependencies of the serialized classes
# used for the AI models that power this service.
# Source code for this file might need to be updated when models
# are changed.
#
# Authored by:
# - Alejandro Guerrero-López (https://github.com/aguerrerolopez)
# - Albert Belenguer (https://github.com/albello1)
#
# Adapted by:
# - José Miguel Moreno (https://github.com/josemmo)

import numpy as np

class LR_ARD(object):
    def predict_proba(self, Z_tst):
        # Calculamos el minimo y maximo de la prob con las salidas de los datos de train
        probs1 = self.predict_proba_one_class(self.X,self.X, self.A_mean1, self.A_cov1, self.tau1, self.prune, self.maximo1)
        probs2 = self.predict_proba_one_class(self.X,self.X, self.A_mean2, self.A_cov2, self.tau2, self.prune, self.maximo2)
        probs3 = self.predict_proba_one_class(self.X,self.X, self.A_mean3, self.A_cov3, self.tau3, self.prune, self.maximo3)

        prob_p = np.hstack((probs1,probs2))
        probs = np.hstack((prob_p,probs3))

        maximo = np.max(probs.ravel())
        minimo = np.min(probs.ravel())

        # Calculamos las probs del test
        ones = np.ones((np.shape(Z_tst)[0],1))
        Z_tst = np.hstack((Z_tst,ones))

        probs1 = self.predict_proba_one_class(Z_tst,self.X, self.A_mean1, self.A_cov1, self.tau1, self.prune, self.maximo1)
        probs2 = self.predict_proba_one_class(Z_tst,self.X, self.A_mean2, self.A_cov2, self.tau2, self.prune, self.maximo2)
        probs3 = self.predict_proba_one_class(Z_tst,self.X, self.A_mean3, self.A_cov3, self.tau3, self.prune, self.maximo3)

        prob_p = np.hstack((probs1,probs2))
        probs = np.hstack((prob_p,probs3))

        # Normalizamos las probabilidades de salida respecto a los datos de train
        probs_norm = self.normalize_data(probs, maximo, minimo)

        # Chequeamos que ningun casi se ha salido de [0,1]
        probs_norm = np.where(probs_norm > 1.0, 1.0, probs_norm)
        probs_norm = np.where(probs_norm < 0.0, 0.0, probs_norm)

        return probs_norm

    def predict_proba_one_class(self, Z_test, X, A_mean, A_cov, tau, prune, maximo):
        fact = np.arange(X.shape[1])[(abs(X.T @ A_mean) > maximo*prune).flatten()].astype(int)
        X = X[:,fact]
        Z_test = Z_test[:,fact]
        mean = Z_test @ X.T @ A_mean
        sig = np.diag(tau + Z_test @ X.T @ A_cov @ X @ Z_test.T).reshape(-1,1)
        probs = self.sigmoid(mean/(np.sqrt(1+(np.pi/8)*sig)))
        return probs

    def normalize_data(self, X, maximo, minimo):
        return (X - minimo) / (maximo - minimo)

    def sigmoid(self, x):
        if any(x < 0):
            return np.exp(x) / (1 + np.exp(x))
        else:
            return 1 / (1 + np.exp(-x))
