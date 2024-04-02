export function normalizeUrl(url: string | undefined): string | undefined {
  if (!url) {
    return url;
  }
  if (url.slice(-1) === '/') {
    return url.slice(0, -1);
  }
  return url;
}
