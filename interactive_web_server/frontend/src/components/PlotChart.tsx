import { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import type { Config, Data, Layout } from 'plotly.js';

interface PlotChartProps {
  data: Data[];
  layout?: Partial<Layout>;
  config?: Partial<Config>;
  className?: string;
  style?: React.CSSProperties;
}

export default function PlotChart({ data, layout = {}, config = {}, className = '', style }: PlotChartProps) {
  const divRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const chart = divRef.current;
    if (!chart) return;

    const defaultConfig = {
      displayModeBar: true,
      displaylogo: false,
      responsive: true,
      ...config,
    };

    Plotly.newPlot(chart, data, layout, defaultConfig);

    return () => {
      Plotly.purge(chart);
    };
  }, [data, layout, config]);

  useEffect(() => {
    const handleResize = () => {
      if (divRef.current) {
        Plotly.Plots.resize(divRef.current);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return <div ref={divRef} className={className} style={style} />;
}
