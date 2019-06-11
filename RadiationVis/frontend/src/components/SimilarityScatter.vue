<template>
  <div id="similarity_scatter_container">
    <div class="scatter">
    </div>
    <div class="tooltip"></div>
  </div>
</template>

<script>
import axios from '../assets/js/http'
import * as d3 from "d3"
export default {
  name: 'SimilarityScatter',
  props: {
    // msg: String
  },
  data() {
    return {
      svg: null,
      svgWidth: 0,
      svgHeight: 0,
    }
  },
  created() {
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
      this.drawVoronoi();
    },
    selfAdaptionSvgSize() {
      let parentNode = document.querySelector("#similarity_scatter_container").parentNode;
      console.log(parentNode.clientWidth, parentNode.clientHeight)
      this.svgWidth = parentNode.clientWidth;
      this.svgHeight = parentNode.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select("#similarity_scatter_container .scatter").append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    drawVoronoi() {
      let margin = {top: 10, right: 10, bottom: 10, left: 10};
      let width = this.svgWidth - margin.left - margin.right;
      let height = this.svgHeight - margin.top - margin.bottom;
      let g = this.svg.append("g")
        .attr('transform', `translate(${margin.left}, ${margin.top})`);
        // .attr
      // let voronoi = d3.voronoi()
      //   .extent([[0, 0], [width, height]]);
        
      let tooltip = document.querySelector("#similarity_scatter_container .tooltip");

      d3.csv("/static/data/SensorSimilarity.csv").then(csvdata => {
        let xExtent = d3.extent(csvdata, d => parseFloat(d.x))
        let yExtent = d3.extent(csvdata, d => parseFloat(d.y))
        xExtent = [Math.floor(xExtent[0]), Math.ceil(xExtent[1])];
        yExtent = [Math.floor(yExtent[0]), Math.ceil(yExtent[1])];
        
        // Init Scales
        let x = d3.scaleLinear().domain(xExtent).range([0, width]);
        let y = d3.scaleLinear().domain(yExtent).range([height, 0]);

        let points = csvdata.map(d => {
          return [x(parseFloat(d.x)), x(parseFloat(d.y))];
        })

        // console.log(points)

        // g.selectAll("path")
        //   .data(voronoi(points).polygons())
        //   .enter()
        //   .append("path")
        //   .style('stroke', 'tomato')
        //   .style('fill', 'none')
        //   .attr("d", d =>  { 
        //     return d ? "M" + d.join("L") + "Z" : null; 
        //   })
        
        g.selectAll("#similarity_scatter_container .sensor_node")
          .data(csvdata)
          .enter()
          .append("circle")
          .attr("class", d => "sensor_node " + d.sensor)
          .attr("cx", d => {
            return x(d.x)
          })
          .attr("cy", d => {
            return y(d.y)
          })
          .attr("r", d => {
            return Math.sqrt(d.mean / Math.PI)
          })
          .attr("fill", d => {
            return d.type == 1 ? 'steelblue': 'orange';
          })
          .style("opacity", d => {

          })
          .on("mouseover", (d, i) => {
            tooltip.style.display = 'block';
            let transl = 'translate(' + (x(d.x)) + 'px, ' + (y(d.y) + 15) + 'px)';
            tooltip.style.webkitTransform = transl;
            tooltip.innerHTML = d.sensor;
          })
          .on("mouseout", (d, i) => {
            tooltip.style.display = 'none';
          })
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
#similarity_scatter_container {
  position: relative;
}
#similarity_scatter_container .selected {
  fill: orange;
}
#similarity_scatter_container .tooltip {
  position: absolute;
  left: 0;
  top: 0;
  background: rgba(0,0,0,.8);
  color: white;
  font-size: 14px;
  padding: 5px;
  line-height: 18px;
  display: none;
}
</style>
