import {
  Chart, ChartEvent,
} from 'chart.js';
import {
  updateGradient,
} from '@/components/charts/chart-utils.ts';
import {
  GradientCache,
  xTicksGradient,
} from '@/components/charts/gradients.ts';

const crossHairGrad: GradientCache = {
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
};

type ChartWithCrosshair = Chart & {
  crosshair: {
    x: number,
    y: number,
    draw: boolean,
  },
};

interface AfterEventArgs {
  cancelable: boolean,
  changed?: boolean,
  event: ChartEvent;
  inChartArea: boolean;
  replay: boolean;
}

interface CrossHairOptions {
    width: number;
}

export default {
  id: 'crosshair',
  defaults: {
    width: 1,
  },
  afterInit: (chart: ChartWithCrosshair) => {
    // eslint-disable-next-line no-param-reassign
    chart.crosshair = {
      x: 0,
      y: 0,
      draw: false,
    };
  },
  afterEvent: (chart: ChartWithCrosshair, args: AfterEventArgs) => {
    const {
      x, y,
    } = args.event;

    if (!x || !y) {
      return;
    }

    // eslint-disable-next-line no-param-reassign
    chart.crosshair = {
      x,
      y,
      draw: args.inChartArea,
    };
    chart.draw();
  },
  beforeDatasetsDraw: (chart: ChartWithCrosshair, opts: CrossHairOptions) => {
    const {
      ctx, chartArea,
    } = chart;
    const {
      x, y, draw,
    } = chart.crosshair;
    if (!draw) {
      return;
    }

    updateGradient(
      crossHairGrad,
      ctx,
      chartArea,
      [
        0,
        1,
      ],
      xTicksGradient,
    );

    ctx.save();

    ctx.beginPath();
    ctx.lineWidth = opts.width;
    ctx.strokeStyle = crossHairGrad.gradient!;
    ctx.moveTo(x, chartArea.bottom + 8);
    ctx.lineTo(x, chartArea.top);
    ctx.moveTo(chartArea.left, y);
    ctx.lineTo(chartArea.right, y);
    ctx.stroke();

    ctx.restore();
  },
};
