export function isObject(item: any) {
  return (item && typeof item === 'object' && !Array.isArray(item));
}

export function deepUnion<T>(obj1: T, overwrite: T): T {
  const result = {
    ...obj1,
  };

  for (const key in overwrite) {
    if (isObject(overwrite[key]) && isObject(obj1[key])) {
      result[key] = deepUnion(obj1[key], overwrite[key]);
    } else {
      result[key] = overwrite[key];
    }
  }

  return result;
}
