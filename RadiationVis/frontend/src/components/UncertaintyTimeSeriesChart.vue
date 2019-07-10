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
      d3.csv('/static/data/StaticSequenceStatistics2.csv').then(staticData => {

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

        d3.csv('/static/data/MobileSequenceStatistics2.csv').then(mobileData => {
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
        .text('(STD)');
    },
    addLegend (g) {
      let legendWidth  = 70,
          legendHeight = 45,
          lineWidth = 30,
          span = 10;

      let legendMargin = {left: 25, top: 5, right: 5, bottom: 5};

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(0, -5)');

      legend.append('line')
        .attr('x1', legendMargin.left)
        .attr('y1', legendMargin.top + span)
        .attr('x2', legendMargin.left + lineWidth)
        .attr('y2', legendMargin.top + span)
        .style('stroke', 'rgba(224, 4, 255, 0.6)')
        .style('stroke-width', 2);
        

      legend.append('text')
        .attr('x', legendMargin.left + lineWidth)
        .attr('y', legendMargin.top + span)
        .attr('dx', '.5em')
        .attr('dy', '.4em')
        .text('Standard deviation of all SSs');

      legend.append('line')
        // .attr('class', 'mobile_uncertainty')
        .attr('x1', legendMargin.left)
        .attr('y1', legendMargin.top + span * 3)
        .attr('x2', legendMargin.left + lineWidth)
        .attr('y2', legendMargin.top + span * 3)
        .style('stroke', 'rgba(54,95,139,0.5)')
        .style('stroke-width', 2);

      legend.append('text')
        .attr('x', legendMargin.left + lineWidth)
        .attr('y', legendMargin.top + span * 3)
        .attr('dx', '.5em')
        .attr('dy', '.4em')
        .text('Standard deviation of all MSs');

    },
    addStaticLegend (g) {
      let legendWidth  = 70,
          legendHeight = 45,
          lineWidth = 30,
          span = 10;

      let legendMargin = {left: 25, top: 5, right: 5, bottom: 5};

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(0, -5)');

      legend.append('line')
        .attr('x1', legendMargin.left)
        .attr('y1', legendMargin.top + span)
        .attr('x2', legendMargin.left + lineWidth)
        .attr('y2', legendMargin.top + span)
        .style('stroke', 'rgba(224, 4, 255, 0.6)')
        .style('stroke-width', 2);
        

      legend.append('text')
        .attr('x', legendMargin.left + lineWidth)
        .attr('y', legendMargin.top + span)
        .attr('dx', '.5em')
        .attr('dy', '.4em')
        .text('Standard deviation of all SSs');

    },
    addMobileLegend (g) {
      let legendWidth  = 70,
          legendHeight = 45,
          lineWidth = 30,
          span = 10;

      let legendMargin = {left: 25, top: 5, right: 5, bottom: 5};

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(0, -5)');

      legend.append('line')
        .attr('x1', legendMargin.left)
        .attr('y1', legendMargin.top + span)
        .attr('x2', legendMargin.left + lineWidth)
        .attr('y2', legendMargin.top + span)
        .style('stroke', 'rgba(54,95,139,0.5)')
        .style('stroke-width', 2);
        

      legend.append('text')
        .attr('x', legendMargin.left + lineWidth)
        .attr('y', legendMargin.top + span)
        .attr('dx', '.5em')
        .attr('dy', '.4em')
        .text('Standard deviation of all MSs');

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
    drawTick(g, x, y, max) {
      let domain = y.domain();
      g.append('text')
        .attr('x', '-2')
        .attr('y', y(domain[0]))
        .attr('dy', '.5em')
        .attr("font-size",10)
        .style('text-anchor', 'end')
        .text(domain[0]);
      g.append('text')
        .attr('x', '-2')
        .attr('y', y(domain[1]))
        .attr('dy', '.5em')
        .attr("font-size",10)
        .style('text-anchor', 'end')
        .text(Math.round(max || domain[1]));
      
    },
    makeChart(static_data, mobile_data) {
      let _this= this;
      let max = 0;
      let max1 = d3.max(static_data, d => d.std);
      let max2 = d3.max(mobile_data, d => d.std);
      let realMax = max = max1 > max2 ? max1: max2;
      if(this.checkedItem.length == 2) {
        // mobile_data = mobile_data.map(d => {
        //   if(d.std > 300) {
        //     return {
        //       date:  d.date,
        //       lower95: parseFloat(d.lower95),
        //       avg: parseFloat(d.avg),
        //       upper95: parseFloat(d.upper95),
        //       std: 300 + (d.std-300) * 0.1
        //     }
        //   } else {
        //     return d
        //   }
        // })
        // max2 = d3.max(mobile_data, d => d.std);
        max = max1 > max2 ? max1: max2;
      } else {
        if(this.checkedItem[0] == 'static') {
          max = max1;
        } else if(this.checkedItem[0] == 'mobile') {
          max = max2;
        }
      }
      console.log(max)

      let begin = static_data[0].date;
      let end = static_data[static_data.length-1].date;
      let basedata = [{date: begin, value: 15}, {date: end, value: 15}];

      let margin = { top: 10, right: 30, bottom: 30, left: 30 },
          chartWidth  = _this.svgWidth  - margin.left - margin.right,
          chartHeight = _this.svgHeight - margin.top  - margin.bottom;

      let x = d3.scaleTime().range([0, chartWidth])
                .domain([begin, end]);
      let y = d3.scaleLinear().range([chartHeight, 0])
                .domain([0, max]);

      // let static_y = d3.scaleLinear().range([chartHeight, 0])
      //           .domain([0, max]);
      // let mobile_y = d3.scaleLinear().range([chartHeight, 0])
      //           .domain([0, max]);

      let xAxis = d3.axisBottom(x)
        .tickSize(5).ticks(d3.timeHour.every(6)).tickFormat((d, i) => {
         var formatMonth = d3.timeFormat("%B %d")
          if(d.getHours() %24 == 0) {
              return formatMonth(d);
            } else {
              return `${d.getHours()}:00`
            }
        });
      let yAxis = d3.axisLeft(y)
        .tickSizeInner(0).tickSizeOuter(0).tickPadding(10).ticks(0);
      // let yAxis_static = d3.axisLeft(static_y)
      //   .tickSizeInner(0).tickSizeOuter(0).tickPadding(10).ticks(0);
      // let yAxis_mobile = d3.axisLeft(mobile_y)
      //   .tickSizeInner(0).tickSizeOuter(0).tickPadding(10).ticks(0);

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
        this.addX(g, xAxis, margin, chartWidth, chartHeight);
        this.addY(g, yAxis, margin, chartWidth, chartHeight);
        this.addLegend(g);
        this.drawPath(g, static_data, x, y, "rgba(224, 4, 255, 0.6)");
        this.drawPath(g, mobile_data, x, y, "rgba(54,95,139, 0.6)");
        this.drawTick(g, x, y, realMax);
      } else {
        if(this.checkedItem[0] == 'static') {
          this.addX(g, xAxis, margin, chartWidth, chartHeight);
          this.addY(g, yAxis, margin, chartWidth, chartHeight);
          this.addStaticLegend(g);
          this.drawPath(g, static_data, x, y, "rgba(224, 4, 255, 0.6)");
          this.drawTick(g, x, y);
        } else if(this.checkedItem[0] == 'mobile') {
          this.addX(g, xAxis, margin, chartWidth, chartHeight);
          this.addY(g, yAxis, margin, chartWidth, chartHeight);
          this.addMobileLegend(g);
          this.drawPath(g, mobile_data, x, y, "rgba(54,95,139, 0.6)");
          this.drawTick(g, x, y);
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
  fill: #41709e;
  stroke: #385e8a;
}

.uncertainty_times_series_chart >>> .static_uncertainty {
  fill: #e004ff;
  stroke: #9e08b3;
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
