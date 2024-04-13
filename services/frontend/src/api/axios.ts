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
  paramsSerializer: (params) => stringify(params, {
    arrayFormat: 'repeat',
  }),
});

applyAuthTokenInterceptor(carlosApi, {
  requestRefresh: refreshToken,
});

export default carlosApi;
