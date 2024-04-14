import {
  AxiosResponse,
} from 'axios';

export async function asyncRequestAction<T, K extends string | number | symbol>({
  id,
  callback,
  promiseMap,
  list,
  force,
}: {
  id: K,
  callback: () => Promise<AxiosResponse<T>>,
  promiseMap: Record<K, Promise<AxiosResponse<T>> | undefined>,
  list: Record<K, T | undefined>,
  force?: boolean,
}) {
  if (promiseMap[id]) {
    return (await promiseMap[id]!).data;
  }

  if (list[id] && !force) {
    return list[id]!;
  }

  // eslint-disable-next-line no-param-reassign
  promiseMap[id] = callback();

  try {
    // eslint-disable-next-line no-param-reassign
    list[id] = (await promiseMap[id]!).data;
  } finally {
    // eslint-disable-next-line no-param-reassign
    delete promiseMap[id];
  }

  return list[id]!;
}

export async function asyncRequestActionList<T>({
  callback,
  setPromise,
  setList,
  list,
  promise,
  force,
}: {
  callback: () => Promise<AxiosResponse<T>>,
  setPromise: (promise: Promise<AxiosResponse<T>> | undefined) => void,
  setList: (list: T) => void,
  list: T | undefined,
  promise: Promise<AxiosResponse<T>> | undefined,
  force?: boolean,
}) {
  if (promise) {
    return (await promise).data;
  }

  if (list && !force) {
    return list;
  }

  const localPromise = callback();
  setPromise(localPromise);

  let data: T;
  try {
    data = (await localPromise).data;
    setList(data);
  } finally {
    setPromise(undefined);
  }

  return data;
}
