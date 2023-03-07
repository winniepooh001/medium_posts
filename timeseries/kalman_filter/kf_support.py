import numpy as np

class kalman_filter:
    def __init__(self, x_init, F, Q, R, H, B=None, u=None, sd=np.array([[0]])):
        self.x_init = x_init
        self.F = F
        self.Q = Q
        self.R = R
        self.H = H
        self.X_post = self.x_init
        self.P_post = sd
        self.X_prior = None
        self.P_prior = None
        if B is not None and u is not None:
            self.B = B
            self.u = u
        else:
            self.B = np.array([[0]])
            self.u = np.array([[0]])

        self.mean = np.array([[]])
        self.covar = np.array([[]])

    def fit(self, data, num_state=1, fit_step=None):
        self.num_state = num_state
        fit_step = fit_step if fit_step is not None and fit_step < data.shape[1] else data.shape[1]
        for i in range(fit_step):
            z_k = data[:, i]
            # predict
            self._predict(self.X_post, self.P_post)
            self._update(z_k)
            # update
            self.mean = np.append(self.mean, self.X_post)
            self.covar = np.append(self.covar, self.P_post)

    def _predict(self, X_post, P_post):
        self.X_prior = np.dot(self.F, X_post) + np.dot(self.B, self.u)
        self.X_prior = self.X_prior.reshape(X_post.shape)
        self.P_prior = np.dot(np.dot(self.F, P_post), self.F.T) + self.Q

    def _update(self, observation):
        resid = observation - np.dot(self.H, self.X_prior)
        S_k = np.dot(np.dot(self.H, self.P_prior), self.H.T) + self.R
        K_k = np.dot(np.dot(self.P_prior, self.H.T), np.linalg.inv(S_k))
        self.X_post = self.X_prior + np.dot(K_k, resid)
        self.P_post = np.dot(np.eye(self.num_state) - np.dot(K_k, self.H), self.P_prior)

    def new_observation(self, observation):
        num_new_obs = observation.shape(self.num_state)
        for i in range(num_new_obs):
            obs = observation[:,i]
            self._predict(self.X_post, self.P_post)
            self._update(self, obs)


def forecast_kf(forecast_len, prev_state, F, H):
    filtered_pred = np.zeros((H.shape[0],forecast_len))
    for i in range(1, forecast_len + 1):
        next_state = np.dot(F, prev_state)
        filtered_pred[:,i-1] = np.dot(H, next_state)
        prev_state = next_state

    return filtered_pred



class extend_kalman_filter:
    def __init__(self, x_init, transition_model, observation_model, F_partial, Q, R, H_partial,
                 L_partial, M_partial
                 , B=None, u=None,  sd=np.array([[0]])):
        self.x_init = x_init
        self.F = F_partial
        self.Q = Q
        self.R = R
        self.H = H_partial
        self.L = L_partial
        self.M = M_partial
        self.transition_model = transition_model
        self.observation_model = observation_model
        self.X_post = self.x_init
        self.P_post = sd
        self.X_prior = None
        self.P_prior = None
        if B is not None and u is not None:
            self.B = B
            self.u = u
        else:
            self.B = np.array([[0]])
            self.u = np.array([[0]])

        self.mean = np.zeros_like(self.x_init)
        self.covar = np.zeros((sd.shape[0], sd.shape[1]))

    def fit(self, data, num_state=1, fit_step=None):
        self.num_state = num_state
        fit_step = fit_step if fit_step is not None and fit_step < data.shape[1] else data.shape[1]
        for i in range(fit_step):
            z_k = data[:, i]
            # predict
            self._predict(self.X_post, self.P_post)
            self._update(z_k)
            # update
            self.mean = np.append(self.mean, self.X_post, axis=1)
            self.covar = np.append(self.covar, self.P_post, axis=0)

    def _predict(self, X_post, P_post):
        self.F_current = self.F(X_post)
        self.L_current = self.L(X_post)
        self.X_prior = self.transition_model(X_post, self.B, self.u)
        self.X_prior = self.X_prior.reshape(X_post.shape)
        self.P_prior = np.dot(np.dot(self.F_current, P_post), self.F_current.T) + \
                       np.dot(np.dot(self.L_current,self.Q),self.L_current.T)

    def _update(self, observation):
        self.H_current = self.H(self.X_prior)
        self.M_current = self.M(self.X_prior)
        resid = observation - self.observation_model(self.X_prior)
        S_k = np.dot(np.dot(self.H_current, self.P_prior), self.H_current.T) + \
              np.dot(np.dot(self.M_current,self.R),self.M_current)

        K_k = np.dot(np.dot(self.P_prior, self.H_current.T), np.linalg.inv(S_k))
        self.X_post = self.X_prior + np.dot(K_k, resid).reshape(self.X_prior.shape)

        self.P_post = np.dot(np.eye(self.num_state) - np.dot(K_k, self.H_current), self.P_prior)

    def new_observation(self, observation):
        num_new_obs = observation.shape(self.num_state)
        for i in range(num_new_obs):
            obs = observation[:,i]
            self._predict(self.X_post, self.P_post)
            self._update(self, obs)

    def get_observation(self):
        fitted = np.zeros((self.H_current.shape[0], self.mean.shape[1]))
        for i in range(self.mean.shape[1]):
            fitted[:,i] = self.observation_model(self.mean[:,i])

        return fitted[:,1:]

    def predict(self, n_step=1, B_new=None, u_new = None):
        ## assume no control
        pred_array = np.zeros((self.H_current.shape[0], n_step))
        X_cur = self.X_post
        for i in range(n_step):
            X_new = self.transition_model(X_cur)
            Y_new = self.observation_model(X_new)
            pred_array[:,i] = Y_new
            X_cur = X_new

        return pred_array







