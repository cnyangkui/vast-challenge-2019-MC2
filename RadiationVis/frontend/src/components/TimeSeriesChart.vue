<template>
  <div :id="cid">
    <div class="times_series_chart"></div>
  </div>
</template>

<script>
import * as d3 from "d3"
export default {
  name: 'TimeSeriesChart',
  props: {
    cid: String
  },
  data() {
    return {
      svg: null,
      svgWidth: null,
      svgHeight: null,
      // defaultTimeRange: {begintime: '2020-04-06 00:00:00', endtime: '2020-04-11 00:00:00'},
      timeRange: null,
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.loadChart();
    })
  },
  methods: {
    loadChart() {
      this.selfAdaptionSvgSize();
      this.drawSvg();
      this.drawChart();
    },
    selfAdaptionSvgSize() {
      let parentNode = document.querySelector(`#${this.cid}`).parentNode;
      this.svgWidth = parentNode.clientWidth;
      this.svgHeight = parentNode.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select(`#${this.cid} .times_series_chart`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    drawChart() {
      let _this = this;
      let parseDate  = d3.timeParse('%Y-%m-%d %H:%M');
      d3.csv('/static/data/StaticSequenceStatistics.csv').then(staticData => {

        let static_data = staticData.map(function (d) {
          return {
            date:  parseDate(d.time),
            lower95: parseFloat(d.lower95),
            avg: parseFloat(d.avg),
            upper95: parseFloat(d.upper95)
          };
        });

        d3.csv('/static/data/MobileSequenceStatistics.csv').then(mobileData => {
          let mobile_data = mobileData.map(function (d) {
          return {
            date:  parseDate(d.time),
            lower95: parseFloat(d.lower95),
            avg: parseFloat(d.avg),
            upper95: parseFloat(d.upper95)
          };
        });
          _this.makeChart(static_data, mobile_data);
        })
      });
    },
    addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight) {

      let axes = g.append('g')
        .attr('clip-path', 'url(#axes-clip)');

      axes.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + chartHeight + ')')
        .call(xAxis);

      axes.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .text('(cpm)');

    },
    addLegend (g, chartWidth) {
      let legendWidth  = 70,
          legendHeight = 45;

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(' + (chartWidth+5) + ', 0)');

      legend.append('rect')
        .attr('class', 'legend-bg')
        .attr('width',  legendWidth)
        .attr('height', legendHeight);

      legend.append('rect')
        .attr('class', 'mobile_uncertainty')
        .attr('width',  20)
        .attr('height', 10)
        .attr('x', 5)
        .attr('y', 5);

      legend.append('text')
        .attr('x', 30)
        .attr('y', 15)
        .text('mobile');

      legend.append('rect')
        .attr('class', 'static_uncertainty')
        .attr('width',  20)
        .attr('height', 10)
        .attr('x', 5)
        .attr('y', 25);

      legend.append('text')
        .attr('x', 30)
        .attr('y', 35)
        .text('static');

      // legend.append('path')
      //   .attr('class', 'median-line')
      //   .attr('d', 'M10,80L85,80');

      // legend.append('text')
      //     .attr('x', 115)
      //     .attr('y', 85)
      //     .text('Median');
    },
    drawPaths (g, data, x, y, styleClass) {

      let upperInnerArea = d3.area()
        .x (function (d) { return x(d.date) || 1; })
        .y0(function (d) { return y(d.upper95); })
        .y1(function (d) { return y(d.avg); });

      let medianLine = d3.line()
        .x(function (d) { return x(d.date); })
        .y(function (d) { return y(d.avg); });

      let lowerInnerArea = d3.area()
        .x (function (d) { return x(d.date) || 1; })
        .y0(function (d) { return y(d.avg); })
        .y1(function (d) { return y(d.lower95); });

      g.datum(data);

      g.append('path')
        .attr('class', 'area upper ' + styleClass)
        .attr('d', upperInnerArea)
        .attr('clip-path', 'url(#rect-clip)');

      g.append('path')
        .attr('class', 'area lower ' + styleClass)
        .attr('d', lowerInnerArea)
        .attr('clip-path', 'url(#rect-clip)');

      g.append('path')
        .attr('class', 'median-line')
        .attr('d', medianLine)
        .attr('clip-path', 'url(#rect-clip)');
    },
    makeChart(static_data, mobile_data) {
      let _this = this;

      let margin = { top: 10, right: 80, bottom: 30, left: 30 },
          chartWidth  = _this.svgWidth  - margin.left - margin.right,
          chartHeight = _this.svgHeight - margin.top  - margin.bottom;

      let x = d3.scaleTime().range([0, chartWidth])
                .domain(d3.extent(mobile_data, function (d) { return d.date; })),
          y = d3.scaleLinear().range([chartHeight, 0])
                .domain([0, d3.max(mobile_data, function (d) { return d.upper95; })]);

      let xAxis = d3.axisBottom(x)
        .tickSizeInner(-chartHeight).tickSizeOuter(0).tickPadding(10).ticks(120).tickFormat((d, i) => {
          if(i % 2 == 0) {
            if(i == 0 || static_data[i].date.getDate() != static_data[i-1].date.getDate()) {
              return `${d.getMonth()+1}/${d.getDate()}`;
            } else {
              return `${d.getHours()}`
            }
          }
        }),
      yAxis = d3.axisLeft(y)
        .tickSizeInner(-chartWidth).tickSizeOuter(0).tickPadding(10).ticks(3);

      let g = _this.svg.append('g')
          .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      let brush = d3.brushX()
        .extent([[0, 0], [chartWidth, chartHeight]])
        .on("end", brushmoved);

      function brushmoved() {
        let s = d3.event.selection;
        if (s != null) {
          let sx = s.map(x.invert);
          let timeFormat = d3.timeFormat('%Y-%m-%d %H:%M:%S');
          _this.$root.eventHub.$emit("timeRangeUpdated", {begintime: timeFormat(sx[0]), endtime: timeFormat(sx[1])});
        } else {
          _this.$root.eventHub.$emit("timeRangeUpdated", null);
        }
      }

      let gBrush = g.append("g")
        .attr("class", "brush")
        .call(brush);

      _this.addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight);
      _this.addLegend(g, chartWidth);
      _this.drawPaths(g, static_data, x, y, "static_uncertainty");
      _this.drawPaths(g, mobile_data, x, y, "mobile_uncertainty");
    }
  }
}
</script>

<style scoped>
.times_series_chart >>> .axis path, 
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.times_series_chart >>> .axis text {
  fill: #000;
}

.times_series_chart >>> .axis .tick line {
  stroke: rgba(0, 0, 0, 0.1);
}

.times_series_chart >>> .area {
  stroke-width: 1;
}

.times_series_chart >>> .area.outer, 
.legend .outer {
  fill: rgba(230, 230, 255, 0.8);
  stroke: rgba(216, 216, 255, 0.8);
}

.times_series_chart >>> .mobile_uncertainty {
  fill: rgba(127, 127, 255, 0.8);
  stroke: rgba(96, 96, 255, 0.8);
}

.times_series_chart >>> .static_uncertainty {
  fill: rgba(255,182,193, 0.8);
  stroke: rgba(255,182,193, 0.8);
}

.times_series_chart >>> .median-line,
.legend .median-line {
  fill: none;
  stroke: #000;
  stroke-width: 1;
}

.times_series_chart >>> .legend .legend-bg {
  fill: rgba(0, 0, 0, 0.5);
  stroke: rgba(0, 0, 0, 0.5);
  opacity: 0.1;
}


.times_series_chart >>> .legend text {
  font-size: 10px;
}

</style>
