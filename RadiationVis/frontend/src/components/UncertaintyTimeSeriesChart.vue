<template>
  <div :id="cid">
    <div class="uncertainty_times_series_chart"></div>
  </div>
</template>

<script>
import * as d3 from "d3"
export default {
  name: 'RadiationTimeSeriesChart',
  props: {
    cid: String,
    checkedItem: Array,
    datatye: Array,
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
      this.svg = d3.select(`#${this.cid} .uncertainty_times_series_chart`).append("svg")
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
            sem: parseFloat(d.sem),
            lower95: parseFloat(d.lower95),
            avg: parseFloat(d.avg),
            upper95: parseFloat(d.upper95),
            std: parseFloat(d.std)
          };
        });

        d3.csv('/static/data/MobileSequenceStatistics.csv').then(mobileData => {
          let mobile_data = mobileData.map(function (d) {
            return {
              date:  parseDate(d.time),
              sem: parseFloat(d.sem),
              lower95: parseFloat(d.lower95),
              avg: parseFloat(d.avg),
              upper95: parseFloat(d.upper95),
              std: parseFloat(d.std)
            };
        });
          _this.makeChart(static_data, mobile_data);
        })
      });
    },
    addX(g, xAxis, margin, chartWidth, chartHeight) {
      g.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + chartHeight + ')')
        .call(xAxis);
    },
    addY(g, yAxis, margin, chartWidth, chartHeight) {
      g.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .text('(std)');
    },
    addLegend (g, chartWidth) {

      let legendWidth  = 70,
          legendHeight = 45,
          rectWidth = 20,
          rectHeight = 10;

      let legendMargin = {left: 5, top: 5, right: 5, bottom: 5};

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(' + (chartWidth - legendWidth) + ', -10)');

      legend.append('rect')
        .attr('class', 'legend-bg')
        .attr('width',  legendWidth)
        .attr('height', legendHeight);

      legend.append('rect')
        .attr('class', 'static_uncertainty')
        .attr('width',  rectWidth)
        .attr('height', rectHeight)
        .attr('x', legendMargin.left)
        .attr('y', legendMargin.top);

      legend.append('text')
        .attr('x', legendMargin.left + rectWidth)
        .attr('y', legendMargin.top)
        .attr('dx', '.5em')
        .attr('dy', '1em')
        .text('static')
        .style('font-size', 10);

      legend.append('rect')
        .attr('class', 'mobile_uncertainty')
        .attr('width',  rectWidth)
        .attr('height', rectHeight)
        .attr('x', legendMargin.left)
        .attr('y', legendMargin.top + rectHeight * 2);

      legend.append('text')
        .attr('x', legendMargin.left + rectWidth)
        .attr('y', legendMargin.top + rectHeight * 2)
        .attr('dx', '.5em')
        .attr('dy', '1em')
        .text('mobile')
        .style('font-size', 10);

    },
    drawPath (g, data, x, y, color) {

      let medianLine = d3.line()
        .x(function (d) { return x(d.date); })
        .y(function (d) { return y(d.std); })
        .curve(d3.curveMonotoneX);

      g.datum(data);

      g.append('path')
        // .attr('class', 'median-line')
        .attr('d', medianLine)
        .style('fill', 'none')
        .style('stroke', color)
        .style('stroke-width', 2);
    },
    drawBaseline(g, data, x, y) {
      let baseline = d3.line()
        .x(function (d) { return x(d.date); })
        .y(function (d) { return y(d.value); });
      g.datum(data);
      g.append('path')
        .attr('d', baseline)
        .style('stroke', 'grey')
        .style('stroke-width', 1);
    },
    makeChart(static_data, mobile_data) {
      let _this = this;


      let max = 0;
        let max1 = d3.max(static_data, d => d.std);
        let max2 = d3.max(mobile_data, d => d.std);
        if(this.checkedItem.length == 2) {
          max = max1 > max2 ? max1: max2;
        } else {
          if(this.checkedItem[0] == 'static') {
            max = max1;
          } else if(this.checkedItem[0] == 'mobile') {
            max = max2;
          }
        }

      let begin = static_data[0].date;
      let end = static_data[static_data.length-1].date;
      let basedata = [{date: begin, value: 15}, {date: end, value: 15}];

      let margin = { top: 10, right: 30, bottom: 30, left: 30 },
          chartWidth  = _this.svgWidth  - margin.left - margin.right,
          chartHeight = _this.svgHeight - margin.top  - margin.bottom;

      let x = d3.scaleTime().range([0, chartWidth])
                .domain([begin, end]),
          y = d3.scaleLinear().range([chartHeight, 0])
                .domain([0, max]);

      let xAxis = d3.axisBottom(x)
        .tickSize(5).ticks(d3.timeHour.every(6)).tickFormat((d, i) => {
         var formatMonth = d3.timeFormat("%B %d")
          if(d.getHours() %24 == 0) {
              return formatMonth(d);
            } else {
              return `${d.getHours()}:00`
            }
        }),
      yAxis = d3.axisLeft(y)
        .tickSizeInner(-5).tickSizeOuter(0).tickPadding(10).ticks(3);

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

      if(this.checkedItem.length == 2) {
        _this.addX(g, xAxis, margin, chartWidth, chartHeight);
        // _this.addY(g, yAxis, margin, chartWidth, chartHeight);
        _this.addLegend(g, chartWidth);
        _this.drawPath(g, static_data, x, y, "rgba(255,182,193, 0.8)");
        _this.drawPath(g, mobile_data, x, y, "rgba(127, 127, 255, 0.8)");
      } else {
        if(this.checkedItem[0] == 'static') {
          _this.addX(g, xAxis, margin, chartWidth, chartHeight);
          _this.addY(g, yAxis, margin, chartWidth, chartHeight);
          // _this.addLegend(g, chartWidth);
          _this.drawPath(g, static_data, x, y, "rgba(255,182,193, 0.8)");
          // _this.drawPath(g, mobile_data, x, y, "mobile_uncertainty");
        } else if(this.checkedItem[0] == 'mobile') {
          _this.addX(g, xAxis, margin, chartWidth, chartHeight);
          _this.addY(g, yAxis, margin, chartWidth, chartHeight);
          // _this.addLegend(g, chartWidth);
          // _this.drawPath(g, static_data, x, y, "static_uncertainty");
          _this.drawPath(g, mobile_data, x, y, "rgba(127, 127, 255, 0.8)");
        }
      }
    },
    clearAllg() {
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
    }
  },
  watch: {
    checkedItem(n, o) {
      this.clearAllg();
      if(n.length != 0) {
        this.drawChart();
      }
    },
    datatye(n, o) {
      this.clearAllg();
      if(n.length != 0) {
        this.drawChart();
      }
    }
  }
}
</script>

<style scoped>
.uncertainty_times_series_chart .axis >>> path, line {
  fill: none;
  stroke: 'black';
  shape-rendering: crispEdges;
}

.uncertainty_times_series_chart >>> .axis text {
  fill: #000;
}

.uncertainty_times_series_chart >>> .axis .tick line {
  stroke: rgba(0, 0, 0, 1);
}

.uncertainty_times_series_chart >>> .area {
  stroke-width: 1;
}

.uncertainty_times_series_chart >>> .area.outer, 
.legend .outer {
  fill: rgba(230, 230, 255, 0.8);
  stroke: rgba(216, 216, 255, 0.8);
}

.uncertainty_times_series_chart >>> .mobile_uncertainty {
  fill: rgba(127, 127, 255, 0.8);
  stroke: rgba(96, 96, 255, 0.8);
}

.uncertainty_times_series_chart >>> .static_uncertainty {
  fill: rgba(255,182,193, 0.8);
  stroke: rgba(255,182,193, 0.8);
}

.uncertainty_times_series_chart >>> .median-line,
.legend .median-line {
  fill: none;
  stroke: #000;
  stroke-width: 1;
}

.uncertainty_times_series_chart >>> .legend .legend-bg {
  fill: rgba(0, 0, 0, 0.5);
  stroke: rgba(0, 0, 0, 0.5);
  opacity: 0.1;
}


.uncertainty_times_series_chart >>> .legend text {
  font-size: 10px;
}

</style>
