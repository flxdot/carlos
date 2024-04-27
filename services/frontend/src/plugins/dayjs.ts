import dayjs from 'dayjs';
import '@/plugins/i18n/dayjs_i18n';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
import minMax from 'dayjs/plugin/minMax';
import LocalizedFormat from 'dayjs/plugin/localizedFormat';

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(duration);
dayjs.extend(relativeTime);
dayjs.extend(minMax);
dayjs.extend(LocalizedFormat);
