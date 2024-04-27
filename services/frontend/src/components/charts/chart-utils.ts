import dayjs from 'dayjs';

export function generateChartTimestamps(days: number, minutesBetweenSamples: number): string[] {
  const timestamps: string[] = [];

  const currentDate: dayjs.Dayjs = dayjs();

  for (let i: number = 0; i < days; i++) {
    const date: dayjs.Dayjs = currentDate.subtract(i, 'day');

    for (let j: number = 0; j < (24 * 60) / minutesBetweenSamples; j++) {
      const timestamp: dayjs.Dayjs = date.subtract(j * minutesBetweenSamples, 'minute');

      const formattedTimestamp: string = timestamp.format('YYYY-MM-DDTHH:mm:ss');

      timestamps.push(formattedTimestamp);
    }
  }

  // Reverse the array to have the timestamps in ascending order
  return timestamps.reverse();
}

export function generateSinWaveFromTimestamps(timestamps: string[], amplitude: number = 1, offset: number = 0, phaseShift: number = 0): number[] {
  const sinWave: number[] = [];

  const angularFrequency: number = 2 * Math.PI / 24;

  // Loop through the provided timestamps
  for (const timestamp of timestamps) {
    const date: dayjs.Dayjs = dayjs(timestamp);

    const timeHours: number = date.hour() + date.minute() / 60 + date.second() / 3600;

    const sineValue: number = offset + (amplitude / 2) * Math.sin(angularFrequency * timeHours + phaseShift);

    sinWave.push(sineValue);
  }

  return sinWave;
}
