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
      this.svg = d3.select(`#${this.cid} .times_series_chart`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    drawChart() {
      let _this = this;
      let parseDate  = d3.timeParse('%Y-%m-%d %H:%M');
      d3.csv('/static/data/StaticSequenceStatistics2.csv').then(staticData => {

        let static_data = staticData.map(function (d) {
          return {
            date:  parseDate(d.time),
            sem: parseFloat(d.sem),
            lower95: parseFloat(d.lower95),
            avg: parseFloat(d.avg),
            upper95: parseFloat(d.upper95)
          };
        });

        d3.csv('/static/data/MobileSequenceStatistics2.csv').then(mobileData => {
          let mobile_data = mobileData.map(function (d) {
            return {
              date:  parseDate(d.time),
              sem: parseFloat(d.sem),
              lower95: parseFloat(d.lower95),
              avg: parseFloat(d.avg),
              upper95: parseFloat(d.upper95)
            };
        });
          _this.makeChart(static_data, mobile_data);
        })
      });
    },
    addX(g, xAxis,margin, chartWidth, chartHeight) {
      g.append('g')
        .attr('class', 'x-axis')
        .attr('transform', 'translate(0,' + chartHeight + ')')
        .call(xAxis);

      d3.selectAll("g.x-axis g.tick line")//选中所有g下类别为tick
        .attr("y2",(d) => {
          if(d.getHours() %24 == 0) {
              return 6;
            } else {
              return 4
            }
        })
        .style("stroke-width",(d) => {
          if(d.getHours() %24 == 0) {
              return 1.3;
            } else {
              return 1
            }
        });
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
        .text('(cpm)');
    },
    addLegend (g, chartWidth) {
      // let legendWidth  = 70,
      //     legendHeight = 45;

      // let legend = g.append('g')
      //   .attr('class', 'legend')
      //   .attr('transform', 'translate(' + (chartWidth+5) + ', 0)');

      // legend.append('rect')
      //   .attr('class', 'legend-bg')
      //   .attr('width',  legendWidth)
      //   .attr('height', legendHeight);

      // legend.append('rect')
      //   .attr('class', 'mobile_uncertainty')
      //   .attr('width',  20)
      //   .attr('height', 10)
      //   .attr('x', 5)
      //   .attr('y', 5);

      // legend.append('text')
      //   .attr('x', 30)
      //   .attr('y', 15)
      //   .text('mobile');

      // legend.append('rect')
      //   .attr('class', 'static_uncertainty')
      //   .style('stroke-width',  20)
      //   .attr('height', 10)
      //   .attr('x', 5)
      //   .attr('y', 25);

      // legend.append('text')
      //   .attr('x', 30)
      //   .attr('y', 35)
      //   .text('static');

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
        .text('static');

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
        .text('mobile');

    },
    drawPathAndArea (g, data, x, y, color) {

      let upperInnerArea = d3.area()
        .x (function (d) { return x(d.date) || 1; })
        .y0(function (d) { return y(d.upper95); })
        .y1(function (d) { return y(d.avg); })
        .curve(d3.curveMonotoneX);

      let medianLine = d3.line()
        .x(function (d) { return x(d.date); })
        .y(function (d) { return y(d.avg); })
        .curve(d3.curveMonotoneX);

      let lowerInnerArea = d3.area()
        .x (function (d) { return x(d.date) || 1; })
        .y0(function (d) { return y(d.avg); })
        .y1(function (d) { return y(d.lower95); })
        .curve(d3.curveMonotoneX);

      g.datum(data);

      g.append('path')
        // .attr('class', 'area upper ' + styleClass)
        .attr('d', upperInnerArea)
        .style('fill', color)
        .style('stroke', color);

      g.append('path')
        // .attr('class', 'area lower ' + styleClass)
        .attr('d', lowerInnerArea)
        .style('fill', color)
        .style('stroke', color);

      g.append('path')
        // .attr('class', 'median-line')
        .attr('d', medianLine)
        .attr('fill', 'none')
        .attr('stroke', 'black');
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
      g.append('text')
        .attr('x', '0px')
        .attr('y', y(15))
        .attr('dx', '0em')
        .attr('dy', '1em')
        .attr("font-size",10)
        .text('background');
      g.append('text')
        .attr('x', '-15px')
        .attr('y', y(15))
        .attr('dx', '0em')
        .attr('dy', '1em')
        .attr("font-size",10)
        .text('15');
    },
    makeChart(static_data, mobile_data) {
      let _this = this;


      let max = 0;
        let max1 = d3.max(static_data, d => d.upper95);
        let max2 = d3.max(mobile_data, d => d.upper95);
        if(this.checkedItem.length == 2) {
          mobile_data = mobile_data.map(d => {
            if(d.avg > 80) {
              return {
                date:  d.date,
                avg: 80 + (parseFloat(d.avg) - 80) * 0.03,
                lower95: 80 + (parseFloat(d.avg) - 80) * 0.03 - 1.96 * d.sem,
                upper95: 80 + (parseFloat(d.avg) - 80) * 0.03 + 1.96 * d.sem
              }
            } else {
              return {
                date:  d.date,
                lower95: parseFloat(d.lower95),
                avg: parseFloat(d.avg),
                upper95: parseFloat(d.upper95)
              }
            }
          })
          max2 = d3.max(mobile_data, d => d.upper95);
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
        .tickSize(5)
        .ticks(d3.timeHour.every(6)).tickFormat((d, i) => {
          var formatMonth = d3.timeFormat("%B %d")
          if(d.getHours() %24 == 0) {
              return formatMonth(d);
            } else {
              return `${d.getHours()}:00`
            }
        });

      let yAxis = d3.axisLeft(y)
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
        _this.drawPathAndArea(g, static_data, x, y, "rgba(196, 60, 48, 0.8)");
        _this.drawPathAndArea(g, mobile_data, x, y, "rgba(54,95,139, 0.8)");
        _this.drawBaseline(g, basedata, x, y);
      } else {
        if(this.checkedItem[0] == 'static') {
          _this.addX(g, xAxis, margin, chartWidth, chartHeight);
          _this.addY(g, yAxis, margin, chartWidth, chartHeight);
          // _this.addLegend(g, chartWidth);
          _this.drawPathAndArea(g, static_data, x, y, "rgba(196, 60, 48, 0.8)");
          // _this.drawPathAndArea(g, mobile_data, x, y, "mobile_uncertainty");
          _this.drawBaseline(g, basedata, x, y);
        } else if(this.checkedItem[0] == 'mobile') {
          _this.addX(g, xAxis, margin, chartWidth, chartHeight);
          _this.addY(g, yAxis, margin, chartWidth, chartHeight);
          // _this.addLegend(g, chartWidth);
          // _this.drawPathAndArea(g, static_data, x, y, "static_uncertainty");
          _this.drawPathAndArea(g, mobile_data, x, y, "rgba(54,95,139, 0.8)");
          _this.drawBaseline(g, basedata, x, y);
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
.times_series_chart .axis >>> path, line {
  fill: none;
  stroke: 'black';
  shape-rendering: crispEdges;
}

.times_series_chart >>> .axis text {
  fill: #000;
}

.times_series_chart >>> .axis .tick line {
  stroke: rgba(0, 0, 0, 1);
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
  //fill: rgba(127, 127, 255, 0.8);
  //stroke: rgba(96, 96, 255, 0.8);
  fill: #41709e;
  stroke: #385e8a;
}

.times_series_chart >>> .static_uncertainty {
  //fill: rgba(255,182,193, 0.8);
  //stroke: rgba(255,182,193, 0.8);
  fill: #d33b33;
  stroke: #a04434;
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
