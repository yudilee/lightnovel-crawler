import { API_BASE_URL } from '@/config';
import { store } from '@/store';
import { Auth } from '@/store/_auth';
import axios, { AxiosError } from 'axios';

export function setupAxios() {
  const state = store.getState();

  axios.defaults.baseURL = API_BASE_URL;
  axios.defaults.headers.common.Accept = 'application/json';
  axios.defaults.headers.post['Content-Type'] = 'application/json';

  // authorization header
  axios.defaults.headers.common.Authorization =
    Auth.select.authorization(state);

  // auto logout
  axios.interceptors.response.use(null, (error: AxiosError) => {
    if (error.response?.status === 401) {
      store.dispatch(Auth.action.clearAuth());
    }
  });
}
