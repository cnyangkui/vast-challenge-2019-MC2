<template>
  <div id="map_container">
    <div class="timeline-wrapper">
      <button id="playButton" @click="playAnimation();">play</button>
      <div class="heatmap-timeline">
        <div class="line"></div>
      </div>
    </div>
    <div id="heatmap_container">
      <div id="heatmap">
        <img ref="geomap" :src="imgsrc">
      </div>
      <div class="tooltip"></div>
    </div>
  </div>
</template>

<script>
import CityMap from "../assets/js/citymap";
import axios from '../assets/js/http'
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
      imgsrc: require('../assets/img/StHimarkMapBlank.png'),
      svg: null,
      squareSelect: {
        clickTime: "",
        startLoc: [],
        endLoc: [],
        flag: "",
      },
      heatmapInstance: null,
      animationPlayer: {
        isPlaying: false,
        currentFrame: 0,
        speed: 3000,
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
      this.drawTimeline();
      this.selfAdaptionSize();
      this.drawSvg();
      this.drawStaticSensor();
      // this.drawVoronoi();
      this.drawHeatmap();
      this.drawSquare()
      
    },
    drawTimeline() {
      let format = d3.timeFormat("%Y-%m-%d %H:%M:%S");
      let timeline = d3.select(".heatmap-timeline");
      for(let h=0; h<24; h++) {
        timeline.append("div")
          .attr("class", "time-point")
          .datum({time: format(new Date(2020, 3, 6, h)), index: h})
          .classed("active", (d) => {
            return d.index == this.animationPlayer.currentFrame ? true: false
          })
          .on("click", (d) => {
            let end = format(new Date(2020, 3, 6, d.index+1))
            let timePoints = d3.selectAll(".time-point").nodes();
            d3.select(timePoints[this.animationPlayer.currentFrame]).classed("active", false)
            this.animationPlayer.currentFrame = d.index;
            d3.select(timePoints[this.animationPlayer.currentFrame]).classed("active", true)

            // axios.post("/findAggMrrByTimeRange/", {begintime: d.time, endtime: end})
            //   .then((response) => {
            //     let responseData = response.data;
            //     let points = []
            //     responseData.forEach(d => {
            //       let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.latitude), parseFloat(d.longitude));
            //       points.push({"x": Math.round(coordinate[0]), "y": Math.round(coordinate[1]), 'value': parseFloat(d.value), "radius": 5});
            //     })
            //     let data = {"max": 100, "data": points};
            //     this.heatmapInstance.setData(data);
            //   })
            //   .catch((error) => {
            //     console.log(error);
            //   });

            // 根据静态传感器读数和动态传感器数据同时绘制heatmap
            this.paintHeatmapByTimeRange({begintime: d.time, endtime: end}, {begintime: d.time, endtime: end})
          })
      }
      // let timelineWidth = parseFloat(timeline.style("width").replace("px", ""));
      let span = 100 / 23;
      d3.selectAll(".time-point").style("left", (d, i) => {
        return span * i + "%"
      })
    },
    selfAdaptionSize() {
      let width = d3.select("#heatmap_container").style("width").replace("px", "");
      this.$refs.geomap.width = parseFloat(width);
      let height = this.$refs.geomap.offsetHeight;
      this.himarkmap.setMapSize(width, height);
    },
    drawSvg() {
      this.svg = d3.select("#heatmap_container").append("svg")
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
        
      d3.csv("/static/data/StaticSensorLocations.csv").then(csvdata => {
        
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
        
        voronoiGroup.selectAll(".staticSensorPoint")
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

      this.heatmapInstance = h337.create({
        // only container is required, the rest will be defaults
        container: document.querySelector('#heatmap'),
        // gradient: {
        //   // enter n keys between 0 and 1 here
        //   // for gradient color customization
        //   '0': 'blue',
        //   '.25': 'green',
        //   '.50': 'orange',
        //   '.75': 'red',
        //   '1': 'white'
        // }
      });
      
      this.heatmapInstance.setDataMin(0);
      this.heatmapInstance.setDataMax(100);

      let _this = this

      // d3.csv("/static/data/StaticSensorReadingsExample.csv").then(csvdata => {
      //   let points = [];
      //   csvdata.forEach(d => {
      //     let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long));
      //     points.push({"x": Math.round(coordinate[0]), "y": Math.round(coordinate[1]), 'value': parseFloat(d.value), "radius": 15});
      //   })
      //   let data = {"max": 20, "data": points};
      //   _this.heatmapInstance.addData(points);
      // })
      // axios.post("/findAggMrrByTimeRange/", {begintime: '2020-04-06 00:00:00', endtime: '2020-04-06 01:00:00'})
      //   .then((response) => {
      //     let responseData = response.data;
      //     let points = []
      //     responseData.forEach(d => {
      //       let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.latitude), parseFloat(d.longitude));
      //       points.push({"x": Math.round(coordinate[0]), "y": Math.round(coordinate[1]), 'value': parseFloat(d.value), "radius": 5});
      //     })
      //     _this.heatmapInstance.addData(points);
      //   })
      //   .catch((error) => {
      //     console.log(error);
      //   });
      let begin = '2020-04-08 09:00:00';
      let end = '2020-04-08 10:00:00';
      this.paintHeatmapByTimeRange({begintime: begin, endtime: end}, {begintime: begin, endtime: end})

      this.drawTooltip();


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
    },
    drawTooltip() {
      let heatmapContainer = document.querySelector("#heatmap_container");
      
      heatmapContainer.onmousemove = (event) => {
        if(!this.squareSelect.flag) {
          let x = event.layerX;
          let y = event.layerY;
          // console.log(x, y)
          let value = this.heatmapInstance.getValueAt({
            x: x, 
            y: y
          });
          let tooltip = document.querySelector('#heatmap_container .tooltip');
          tooltip.style.display = 'block';
          let transl = 'translate(' + (x + 15) + 'px, ' + (y + 15) + 'px)';
          tooltip.style.webkitTransform = transl;
          tooltip.innerHTML = value;
        }
      }
      heatmapContainer.onmouseout = () => {
        let tooltip = document.querySelector('#heatmap_container .tooltip');
        tooltip.style.display = 'none';
      };
    },
    playAnimation() {
      this.animationPlayer.isPlaying = !this.animationPlayer.isPlaying;
      document.getElementById("playButton").innerHTML = this.animationPlayer.isPlaying == true ? "pause": "play";
      let timePoints = d3.selectAll(".time-point").nodes()
      let format = d3.timeFormat("%Y-%m-%d %H:%M:%S");
      if(this.animationPlayer.isPlaying) { //播放
        this.animationPlayer.interval = setInterval(() => {
          // active节点后移
          d3.select(timePoints[this.animationPlayer.currentFrame]).classed("active", false)
          this.animationPlayer.currentFrame = (this.animationPlayer.currentFrame + 1) % 24;
          d3.select(timePoints[this.animationPlayer.currentFrame]).classed("active", true)

          let d = d3.select(timePoints[this.animationPlayer.currentFrame]).datum();
          let end = format(new Date(2020, 3, 6, d.index+1))

          this.paintHeatmapByTimeRange({begintime: d.time, endtime: end}, {begintime: d.time, endtime: end})
          
        }, this.animationPlayer.speed)
      } else {
        clearInterval(this.animationPlayer.interval)
      }
    },
    getAggMrrByTimeRange(params) {
      return axios.post('/findAggMrrByTimeRange/', params);
    },
    getAggSrrByTimeRange(params) {
      return axios.post('/findAggSrrByTimeRange/', params);
    },
    // 根据静态传感器读数和动态传感器数据同时绘制heatmap
    paintHeatmapByTimeRange(staticParams, mobileParams) {
      axios.all([this.getAggSrrByTimeRange(staticParams), this.getAggMrrByTimeRange(mobileParams)])
        .then(axios.spread((response1, response2) => {
          let points = []
          response1.data.forEach(d => {
            let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.latitude), parseFloat(d.longitude));
            points.push({"x": Math.round(coordinate[0]), "y": Math.round(coordinate[1]), 'value': parseFloat(d.value), "radius": 30});
          })
          response2.data.forEach(d => {
            let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.latitude), parseFloat(d.longitude));
            points.push({"x": Math.round(coordinate[0]), "y": Math.round(coordinate[1]), 'value': parseFloat(d.value), "radius": 10});
          })
          let data = {"min": 0, "max": 500, "data": points};
          this.heatmapInstance.setData(data);
        }));
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
#map_container {
  background: white;
  transition: 1s ease all;
  border-radius: 4px;
  box-shadow: rgba(0,0,0,.65);
}
#map_container #playButton {
  outline: none;
  color: black;
  background: #f2f2f2;
  width: 50px;
  height: 100%;
  cursor: pointer;
  border: none;
  text-transform: uppercase;
  border-top-left-radius: 3px;
  border-bottom-left-radius: 3px;
}
#map_container .heatmap-timeline {
  position: absolute;
  top: 0;
  right: 15px;
  left: 70px;
  height: 100%;
}
#map_container .heatmap-timeline .line {
    position: absolute;
    left: 0;
    right: 0;
    top: 12px;
    height: 2px;
    background: #d7d7d7;
}
#map_container .time-point {
  position: absolute;
  background: white;
  border: 2px solid #272727;
  width: 8px;
  height: 8px;
  border-radius: 100%;
  cursor: pointer;
  top: 12px;
  transform: translateX(-50%) translateY(-50%);
}
#map_container .heatmap-timeline .time-point.active {
    background: black;
}
#heatmap_container {
  position: relative;
}
#map_container .staticSensorPoint {
  fill: black;
}
#map_container .selected {
  fill: orange;
}
#map_container .tooltip {
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
