<template>
  <div :id="cid">
    <div class="trendchart"></div>
  </div>
</template>

<script>
import * as d3 from "d3"
export default {
  name: 'TrendChartWithTimeBrush',
  props: {
    cid: String
  },
  data() {
    return {
      svg: null,
      svgWidth: null,
      svgHeight: null,
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
      // console.log(parentNode.clientWidth, parentNode.clientHeight)
      this.svgWidth = parentNode.clientWidth;
      this.svgHeight = parentNode.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select(`#${this.cid} .trendchart`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    drawChart() {
      function addAxesAndLegend (g, xAxis, yAxis, margin, chartWidth, chartHeight) {
        var legendWidth  = 200,
            legendHeight = 100;

        // clipping to make sure nothing appears behind legend
        // g.append('clipPath')
        //   .attr('id', 'axes-clip')
        //   .append('polygon')
        //   .attr('points', (-margin.left)                 + ',' + (-margin.top)                 + ' ' +
        //                     (chartWidth - legendWidth - 1) + ',' + (-margin.top)                 + ' ' +
        //                     (chartWidth - legendWidth - 1) + ',' + legendHeight                  + ' ' +
        //                     (chartWidth + margin.right)    + ',' + legendHeight                  + ' ' +
        //                     (chartWidth + margin.right)    + ',' + (chartHeight + margin.bottom) + ' ' +
        //                     (-margin.left)                 + ',' + (chartHeight + margin.bottom));

        var axes = g.append('g')
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
            .text('radition (cpm)');

        // var legend = g.append('g')
        //   .attr('class', 'legend')
        //   .attr('transform', 'translate(' + (chartWidth - legendWidth) + ', 0)');

        // legend.append('rect')
        //   .attr('class', 'legend-bg')
        //   .attr('width',  legendWidth)
        //   .attr('height', legendHeight);

        // legend.append('rect')
        //   .attr('class', 'outer')
        //   .attr('width',  75)
        //   .attr('height', 20)
        //   .attr('x', 10)
        //   .attr('y', 10);

        // legend.append('text')
        //   .attr('x', 115)
        //   .attr('y', 25)
        //   .text('5% - 95%');

        // legend.append('rect')
        //   .attr('class', 'inner')
        //   .attr('width',  75)
        //   .attr('height', 20)
        //   .attr('x', 10)
        //   .attr('y', 40);

        // legend.append('text')
        //   .attr('x', 115)
        //   .attr('y', 55)
        //   .text('25% - 75%');

        // legend.append('path')
        //   .attr('class', 'median-line')
        //   .attr('d', 'M10,80L85,80');

        // legend.append('text')
        //     .attr('x', 115)
        //     .attr('y', 85)
        //     .text('Median');
      }

      function drawPaths (g, data, x, y, styleClass) {

        var upperInnerArea = d3.area()
          .x (function (d) { return x(d.date) || 1; })
          .y0(function (d) { return y(d.upper95); })
          .y1(function (d) { return y(d.avg); });

        var medianLine = d3.line()
          .x(function (d) { return x(d.date); })
          .y(function (d) { return y(d.avg); });

        var lowerInnerArea = d3.area()
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
      }

      function startTransitions (g, chartWidth, chartHeight, rectClip, x) {
        rectClip.transition()
          .attr('width', chartWidth);
      }

      let _this = this;

      function makeChart (data1, data2) {
        var margin = { top: 10, right: 20, bottom: 30, left: 30 },
            chartWidth  = _this.svgWidth  - margin.left - margin.right,
            chartHeight = _this.svgHeight - margin.top  - margin.bottom;

        var x = d3.scaleTime().range([0, chartWidth])
                  .domain(d3.extent(data2, function (d) { return d.date; })),
            y = d3.scaleLinear().range([chartHeight, 0])
                  .domain([0, d3.max(data2, function (d) { return d.upper95; })]);

        var xAxis = d3.axisBottom(x)
                      .tickSizeInner(-chartHeight).tickSizeOuter(0).tickPadding(10).ticks(10),//.tickFormat(d => d.getHours()),
            yAxis = d3.axisLeft(y)
                      .tickSizeInner(-chartWidth).tickSizeOuter(0).tickPadding(10);

        var g = _this.svg.append('g')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        var brush = d3.brushX()
          .extent([[0, 0], [chartWidth, chartHeight]])
          .on("end", brushmoved);

        function brushmoved() {
          var s = d3.event.selection;
          if (s != null) {
            var sx = s.map(x.invert);
            let timeFormat = d3.timeFormat('%Y-%m-%d %H:%M:%S');
            // console.log(timeFormat(sx[0]), timeFormat(sx[1]))
            _this.$root.eventHub.$emit("timeRangeUpdate", {begintime: timeFormat(sx[0]), endtime: timeFormat(sx[1])});
          }
        }

        var gBrush = g.append("g")
          .attr("class", "brush")
          .call(brush);

        addAxesAndLegend(g, xAxis, yAxis, margin, chartWidth, chartHeight);
        drawPaths(g, data1, x, y, "inner2");
        drawPaths(g, data2, x, y, "inner");
        // startTransitions(g, chartWidth, chartHeight, rectClip, x);
      }
      var parseDate  = d3.timeParse('%Y-%m-%d %H:%M');
      d3.csv('/static/data/StaticSequenceStatistics.csv').then(staticData => {

        var data1 = staticData.map(function (d) {
          return {
            date:  parseDate(d.time),
            lower95: parseFloat(d.lower95),
            avg: parseFloat(d.avg),
            upper95: parseFloat(d.upper95)
          };
        });

        d3.csv('/static/data/MobileSequenceStatistics.csv').then(mobileData => {
          var data2 = mobileData.map(function (d) {
          return {
            date:  parseDate(d.time),
            lower95: parseFloat(d.lower95),
            avg: parseFloat(d.avg),
            upper95: parseFloat(d.upper95)
          };
        });
          makeChart(data1, data2);
        })
      });
    },
  }
}
</script>

<style scoped>
.trendchart >>> .axis path, 
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.trendchart >>> .axis text {
  fill: #000;
}

.trendchart >>> .axis .tick line {
  stroke: rgba(0, 0, 0, 0.1);
}

.trendchart >>> .area {
  stroke-width: 1;
}

.trendchart >>> .area.outer, 
.legend .outer {
  fill: rgba(230, 230, 255, 0.8);
  stroke: rgba(216, 216, 255, 0.8);
}

.trendchart >>> .area.inner {
  fill: rgba(127, 127, 255, 0.8);
  stroke: rgba(96, 96, 255, 0.8);
}

.trendchart >>> .area.inner2 {
  fill: rgba(255, 127, 0, 0.8);
  stroke: rgba(255, 127, 0, 0.8);
}

.trendchart >>> .median-line,
.legend .median-line {
  fill: none;
  stroke: #000;
  stroke-width: 1;
}

.trendchart >>> .legend .legend-bg {
  fill: rgba(0, 0, 0, 0.5);
  stroke: rgba(0, 0, 0, 0.5);
}

.trendchart >>> .marker.client .marker-bg,
.marker.client path {
  fill: rgba(255, 127, 0, 0.8);
  stroke: rgba(255, 127, 0, 0.8);
  stroke-width: 3;
}

.trendchart >>> .marker.server .marker-bg,
.trendchart >>> .marker.server path {
  fill: rgba(0, 153, 51, 0.8);
  stroke: rgba(0, 153, 51, 0.8);
  stroke-width: 3;
}

.trendchart >>> .marker path {
  fill: none;
}

#trend_chart_container .legend text,
#trend_chart_container .marker text {
  fill: #fff;
  font-weight: bold;
}

#trend_chart_container .marker text {
  text-anchor: middle;
}
</style>
