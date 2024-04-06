import {
  useAuth0,
} from '@auth0/auth0-vue';

const {
  getAccessTokenSilently,
} = useAuth0();

// @ts-ignore - The interface requires a value to be passed, but we don't need it.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function refreshToken(token: string) {
  return getAccessTokenSilently();
}
