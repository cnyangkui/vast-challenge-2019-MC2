<template>
  <div :id="cid">
    <div class="scatterControl">
      <span>SendorId: {{sid}}</span> &nbsp;
      <el-input size="mini" v-model="minInput" placeholder="min"></el-input> &nbsp;<span>-</span>&nbsp;
      <el-input size="mini" v-model="maxInput" placeholder="max"></el-input>
    </div>
    <div class="scatterplot">
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import axios from '../assets/js/http'
export default {
  name: 'SRScatter',
  props: {
    cid: String
  },
  data() {
    return {
      minInput: 0,
      maxInput: 60,
      minValue: null,
      maxValue: null,
      svgWidth: 0,
      svgHeight: 0,
      category: 'mobile',
      sid: 1,
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
      this.drawScatter(this.sid)
    },
    selfAdaptionSvgSize() {
      let parentNode = document.querySelector(`#${this.cid}`).parentNode;
      let parentHeight = parentNode.clientHeight;
      let control = document.querySelector(`#${this.cid} .scatterControl`);
      this.svgWidth = control.clientWidth;
      this.svgHeight = parentHeight - control.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select(`#${this.cid} .scatterplot`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    drawScatter(sid) {
      let margin = {top: 5, right: 15, bottom: 20, left: 25};
      let width = this.svgWidth - margin.left - margin.right;
      let height = this.svgHeight - margin.top - margin.bottom;
      // console.log(this.svgWidth, this.svgHeight)

      let container = d3.select(`#${this.cid} .scatterplot`);

      // Init g
      let g = this.svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

      // Init Canvas
      let canvasChart = container.append('canvas')
          .attr('width', width)
          .attr('height', height)
          .style('margin-left', margin.left + 'px')
          .style('margin-top', margin.top + 'px')
          .attr('class', 'canvas-plot');

      let context = canvasChart.node().getContext('2d');
      let _this = this;
      axios.post("/findSrBySid/", {
        category: this.category,
        sid: this.sid,
      })
      .then(function (response) {
        // console.log(response.data);
        let responseData = response.data;
        
        // Init Scales
        let x = d3.scaleTime().domain([new Date(2020, 3, 6), new Date(2020, 3, 10)]).range([0, width]);
        let y = d3.scaleLinear().domain([0, _this.maxInput]).range([height, 0]);

        // Init Axis
        let xAxis = d3.axisBottom(x).ticks(5);
        let yAxis = d3.axisLeft(y);

        // // Add Axis
        let gxAxis = g.append('g')
            .attr("class", "x axis ")
            .attr('transform', `translate(0, ${height})`)
            .call(xAxis);

        let gyAxis = g.append('g')
            .attr("class", "y axis")
            .call(yAxis);

        // Draw on canvas
        responseData.forEach( point => {
            drawPoint(point);
        });

        function drawPoint(point) {
            context.beginPath();
            // context.fillStyle = pointColor;
            const px = x(new Date(point.timestamp));
            const py = y(point.value);

            context.fillStyle = 'steelblue';  
            context.arc(px, py, 0.5, 0, 2 * Math.PI,true);
            context.fill();
        }

      })
      .catch(function (error) {
        console.log(error);
      });
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
.scatterplot {
  position: relative;
}
.scatterplot .canvas-plot {
  position: absolute;
  left: 0;
  top: 0;
}
.scatterControl .el-input {
  width: 60px;
}
.scatterControl span {
  font-size: 12px;
}
</style>
