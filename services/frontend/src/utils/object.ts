type DeepUnion<T> =
    T extends object ? (
        { [K in keyof T]: DeepUnion<T[K]> }
    )
    : T;

export function deepUnion<T extends object>(obj1: T, overwrite: T): DeepUnion<T> {
  const result = {
    ...obj1,
  };

  for (const key in overwrite) {
    if (Object.prototype.hasOwnProperty.call(overwrite, key)) {
      if (typeof overwrite[key] === 'object' && overwrite[key] !== null) {
        result[key] = deepUnion(obj1[key] ?? {}, overwrite[key]);
      } else {
        result[key] = overwrite[key];
      }
    }
  }

  return result as DeepUnion<T>;
}
