<template>
  <div id="mapContainer">
    <div id="heatmap">
      <img ref="geomap" :src="himarkmap.imageSrc">
    </div>
  </div>
</template>

<script>
import CityMap from "../../public/static/js/citymap";
import * as d3 from "d3"
import * as h337 from "heatmap.js"
export default {
  name: 'StHimarkMap',
  props: {
    // msg: String
  },
  data() {
    return {
      himarkmap: new CityMap(),
      svg: null,
      squareSelect: {
        clickTime: "",
        startLoc: [],
        endLoc: [],
        flag: "",
      } 
    }
  },
  created() {
    console.log(this.himarkmap)
  },
  mounted() {
    this.$nextTick(() => {
      // dom虽然加载完成,但是图片资源的请求不一定已经返回
      this.$refs.geomap.addEventListener('load', () => {
        this.loadMap();
      })
    })
  },
  methods: {
    loadMap() {
      this.selfAdaptionSize();
      this.drawSvg();
      // this.drawStaticSensor();
      this.drawVoronoi();
      this.drawHeatmap();
      this.drawSquare()
      
    },
    selfAdaptionSize() {
      let width = d3.select("#mapContainer").style("width").replace("px", "");
      this.$refs.geomap.width = parseFloat(width);
      let height = this.$refs.geomap.offsetHeight;
      this.himarkmap.setMapSize(width, height);
    },
    drawSvg() {
      this.svg = d3.select("#mapContainer").append("svg")
        .attr("width", this.himarkmap.width)
        .attr("height", this.himarkmap.height)
        .style("position", "absolute")
        .style("top", 0)
        .style("left", 0)
    },
    drawStaticSensor() {
      d3.csv("static/data/StaticSensorLocations.csv").then(csvdata => {
        this.svg.selectAll(".staticSensorPoint")
          .data(csvdata)
          .enter()
          .append("circle")
          .attr("class", "staticSensorPoint")
          .attr("id", d => "sid_" + d.sid)
          .attr("cx", d => {
            return this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long))[0]
          })
          .attr("cy", d => {
            return this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long))[1]
          })
          .attr("r", 3)
          .attr("fill", 'steelblue');
      })
      // d3.csv("static/data/StaticSensorLocations.csv", (d) => {
      //   let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long));
      //   this.svg.append("circle")
      //     .attr("id", "sid_" + d.sid)
      //     .attr("cx", coordinate[0])
      //     .attr("cy", coordinate[1])
      //     .attr("r", 3)
      //     .attr("fill", 'steelblue');
      // })
    },
    drawVoronoi() {
      let voronoiGroup = this.svg.append("g").attr("class", "voronoi");
      let voronoi = d3.voronoi()
				.extent([[0, 0], [this.himarkmap.width, this.himarkmap.height]]);
        
      d3.csv("static/data/StaticSensorLocations.csv").then(csvdata => {
        
        let coordinateData = csvdata.map(d => {
          return this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long));
        })

        voronoiGroup.selectAll("path")
          .data(voronoi(coordinateData).polygons())
          .enter()
          .append("path")
          .style('stroke', 'tomato')
          .style('fill', 'none')
          .attr("d", d =>  { 
            return d ? "M" + d.join("L") + "Z" : null; 
          })
        
        this.svg.selectAll(".staticSensorPoint")
          .data(csvdata)
          .enter()
          .append("circle")
          .attr("class", "staticSensorPoint")
          .attr("id", d => "sid_" + d.sid)
          .attr("cx", d => {
            return this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long))[0]
          })
          .attr("cy", d => {
            return this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long))[1]
          })
          .attr("r", 3);
          // .attr("fill", 'steelblue');
      })
    },
    drawHeatmap() {
      this.heatmap = d3.select("#heatmap")
        .style("width", this.himarkmap.width + "px")
        .style("height", this.himarkmap.height + "px")
        .style("position", "absolute")
        .style("top", 0)
        .style("left", 0)

      let heatmapInstance = h337.create({
        // only container is required, the rest will be defaults
        container: document.querySelector('#heatmap')
      });

      d3.csv("static/data/StaticSensorReadingsExample.csv").then(csvdata => {
        let points = [];
        csvdata.forEach(d => {
          let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long));
          points.push({"x": Math.round(coordinate[0]), "y": Math.round(coordinate[1]), 'value': parseFloat(d.value), "radius": 80});
        })
        let data = {"max": 20, "data": points};
        heatmapInstance.setData(data);
      })
    },
    drawSquare() {
      /**
       * 框选数据
       */
      let rect = this.svg.append("rect")
        .attr("width", 0)
        .attr("height", 0)
        .attr("fill", "rgba(33,20,50,0.3)")
        .attr("stroke", "#ccc")
        .attr("stroke-width", "2px")
        .attr("transform", "translate(0,0)")
        .attr("id", "squareSelect");
 
      this.svg.on("mousedown", () => {
        this.squareSelect.clickTime = (new Date()).getTime();//mark start time
        this.squareSelect.flag = true;//以flag作为可执行圈选的标记
        rect.attr("transform", "translate(" + d3.event.layerX + "," + d3.event.layerY + ")");
        this.squareSelect.startLoc = [d3.event.layerX, d3.event.layerY];
        // console.log(this.squareSelect)
      });
 
      this.svg.on("mousemove", () => {
        //判断事件target
        if ((d3.event.target.localName == "svg" && this.squareSelect.flag == true) || (d3.event.target.localName == "circle" && this.squareSelect.flag == true) || (d3.event.target.localName == "path" && this.squareSelect.flag == true)) {
          let width = d3.event.layerX - this.squareSelect.startLoc[0];
          let height = d3.event.layerY - this.squareSelect.startLoc[1];
          if (width < 0) {
            rect.attr("transform", "translate(" + d3.event.layerX + "," + this.squareSelect.startLoc[1] + ")");
          }
          if (height < 0) {
            rect.attr("transform", "translate(" + this.squareSelect.startLoc[0] + "," + d3.event.layerY + ")");
          }
          if (height < 0 && width < 0) {
            rect.attr("transform", "translate(" + d3.event.layerX + "," + d3.event.layerY + ")");
          }
          rect.attr("width", Math.abs(width)).attr("height", Math.abs(height))
        }
      })
  
      this.svg.on("mouseup", () => {
        if(this.squareSelect.flag == true) {
          this.squareSelect.flag = false;
          this.squareSelect.endLoc = [d3.event.layerX, d3.event.layerY];
          let leftTop = [];
          let rightBottom = []
          if(this.squareSelect.endLoc[0] >= this.squareSelect.startLoc[0]){
              leftTop[0] = this.squareSelect.startLoc[0];
              rightBottom[0] = this.squareSelect.endLoc[0];
          } else {
              leftTop[0] = this.squareSelect.endLoc[0];
              rightBottom[0] = this.squareSelect.startLoc[0];
          }

          if(this.squareSelect.endLoc[1] >= this.squareSelect.startLoc[1]){
              leftTop[1] = this.squareSelect.startLoc[1];
              rightBottom[1] = this.squareSelect.endLoc[1];
          } else {
              leftTop[1] = this.squareSelect.endLoc[1];
              rightBottom[1] = this.squareSelect.startLoc[1];
          }

          //最后通过和node的坐标比较，确定哪些点在圈选范围
          d3.selectAll(".staticSensorPoint").data().forEach(d => {
            let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long));
            if(coordinate[0] < rightBottom[0] && coordinate[0] > leftTop[0] && coordinate[1] > leftTop[1] && coordinate[1] < rightBottom[1]) {
              d3.select("#sid_"+d.sid).classed("selected", true);
            } else {
              d3.select("#sid_"+d.sid).classed("selected", false);
            }
          })
          rect.attr("width", 0).attr("height", 0);
        }

        let times = (new Date()).getTime() - this.squareSelect.clickTime;
        if (times < 100 && d3.event.target.id !== "squareSelect") {
          let nodes = d3.selectAll(".staticSensorPoint").classed("selected", false);
        }
      })  
    }

  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
#mapContainer {
  position: relative;
}
.staticSensorPoint {
  fill: steelblue;
}
.selected {
  fill: orange;
}
</style>
