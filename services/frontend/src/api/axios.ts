import axios from 'axios';
import {
  applyAuthTokenInterceptor,
} from 'axios-jwt';
import {
  stringify,
} from 'qs';
import {
  refreshToken,
} from '@/services/auth.ts';
import config from '@/config';

const carlosApi = axios.create({
  baseURL: config.VITE_APP_API_URL,
  paramsSerializer: {
    serialize: (params) => {
      return stringify(params, {
        arrayFormat: 'repeat',
      });
    },
  },
});

applyAuthTokenInterceptor(carlosApi, {
  requestRefresh: refreshToken,
});

export function setToken(token: string | undefined) {
  if (token) {
    carlosApi.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }
  delete carlosApi.defaults.headers.common.Authorization;
}

export default carlosApi;
