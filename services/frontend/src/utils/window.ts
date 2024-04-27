export enum MediaSize {
    MOBILE = 481,
    TABLET = 769,
    DESKTOP = 1249,
    DESKTOP_LARGE = 1441,
}

export function getMediaCategory(): MediaSize {
  if (window.innerWidth <= MediaSize.MOBILE) {
    return MediaSize.MOBILE;
  }
  if (window.innerWidth <= MediaSize.TABLET) {
    return MediaSize.TABLET;
  }
  if (window.innerWidth < MediaSize.DESKTOP) {
    return MediaSize.DESKTOP;
  }
  return MediaSize.DESKTOP_LARGE;
}
