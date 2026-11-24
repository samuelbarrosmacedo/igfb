import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { BarChart } from "echarts/charts";
import { GridComponent, AriaComponent } from "echarts/components";
import { SVGRenderer } from "echarts/renderers";
import type { simulate } from "../lib/simulation";
echarts.use([BarChart, GridComponent, AriaComponent, SVGRenderer]);
export default function ContributionChart({
  rows,
  labels,
}: {
  rows: ReturnType<typeof simulate>;
  labels: Record<string, string>;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current, null, { renderer: "svg" });
    const criteria = [
      ...new Set(
        rows.flatMap((row) => row.contributions.map((item) => item.criterion)),
      ),
    ];
    chart.setOption({
      animation: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      animationDuration: 250,
      aria: {
        enabled: true,
        label: {
          description:
            "Contribuições por critério nas três equipes fictícias. Valores positivos acrescentam pontos; penalidades subtraem. Os valores completos estão na tabela a seguir.",
        },
        decal: { show: true },
      },
      color: ["#87cfa7", "#d0b776", "#dce5d6", "#b57d72"],
      grid: { left: 130, right: 20, top: 15, bottom: 30 },
      xAxis: {
        type: "value",
        axisLabel: {
          color: "#bac4bb",
          formatter: (value: number) => value.toLocaleString("pt-BR"),
        },
        splitLine: { lineStyle: { color: "#303a32" } },
      },
      yAxis: {
        type: "category",
        data: rows.map((row) => row.name),
        inverse: true,
        axisLabel: { color: "#e9ece4", fontSize: 12 },
        axisTick: { show: false },
      },
      series: criteria.map((criterion) => ({
        type: "bar",
        stack: "contributions",
        name: labels[criterion],
        barWidth: 26,
        data: rows.map(
          (row) =>
            row.contributions.find((item) => item.criterion === criterion)
              ?.value || 0,
        ),
      })),
    });
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(ref.current);
    return () => {
      observer.disconnect();
      chart.dispose();
    };
  }, [rows, labels]);
  return (
    <div
      ref={ref}
      className="contribution-chart"
      role="img"
      aria-label="Contribuições por critério nas três equipes fictícias. Os valores estão na tabela a seguir."
    />
  );
}
