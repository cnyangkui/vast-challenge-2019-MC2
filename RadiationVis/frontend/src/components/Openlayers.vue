<template>
  <div id="openlayers_container">
    <div class="sidepanel">
      <div class="nav">
        <div class="nav-select">
            <el-select v-model="currentSelectValue" placeholder="请选择" size="mini" style="width: 110px;" @change="selectChanged">
              <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
        </div>
        <div class="nav-checkbox-group" v-if="currentSelectValue=='radiation'">
          <el-checkbox v-model="r_si_check" @change="krigingLayerUpdate" size="mini">SS Interpolation</el-checkbox>
          <el-checkbox v-model="r_mi_check" @change="idwLayerUpdate" size="mini">MS Interpolation</el-checkbox>
        </div>
        <div class="nav-checkbox-group" v-else-if="currentSelectValue=='uncertainty'">
          <el-checkbox v-model="u_mi_check" @change="uncertaintyIdwLayerUpdate" size="mini">MS Interpolation</el-checkbox>
          <el-checkbox v-model="u_pie_check" @change="piesUpdate" size="mini">Pies</el-checkbox>
        </div>
        <div class="nav-checkbox-group" v-else-if="currentSelectValue=='track'">
          <el-checkbox v-model="t_heatmap_check" @change="heatmapLayerUpdate" size="mini">Heatmap</el-checkbox>
        </div>
      </div> 
    </div>
    <div id="himarkmap"></div>
  </div>
</template>
<script>
import CityMap from "../assets/js/citymap";
import axios from '../assets/js/http'
import kriging from '../assets/js/kriging'
import idw from '../assets/js/idw'
import * as d3 from 'd3'
import 'ol/ol.css';
// import ol from 'ol'
import {Map, View, Feature, Graticule} from 'ol';
import Image from 'ol/layer/Image'
import VectorLayer from 'ol/layer/Vector'
import Heatmap from 'ol/layer/Heatmap'
import ImageStatic from 'ol/source/ImageStatic'
import ImageCanvas from 'ol/source/ImageCanvas'
import VectorSource from 'ol/source/Vector'
import {getCenter} from 'ol/extent';
import Projection from 'ol/proj/Projection';
import {Point, LineString, Polygon} from 'ol/geom'
import {Style, Circle, Fill, Stroke} from 'ol/style'
import Select from 'ol/interaction/Select'
import {defaults as defaultControls, FullScreen} from 'ol/control';
import Overlay from 'ol/Overlay';

export default {
  name: 'Openlayers',
  data() {
    return {
      options: [{
        value: 'radiation',
        label: 'radiation'
      }, {
        value: 'uncertainty',
        label: 'uncertainty'
      }, {
        value: 'track',
        label: 'track'
      }],
      currentSelectValue: 'radiation',
      himarkmap: new CityMap(),
      imageExtent: [-120.0, 0, -119.711751, 0.238585], //[left, bottom, right, top]
      map: null, 
      layers: {
        staticPointLayer: null, //静态传感器层
        mobilePointLayer: null,
        krigingLayer: null,
        idwLayer: null,
        heatmapLayer: null,
        idwUncertaintyLayer: null,
      },
      dataCollection: {
        mobileSensorReadings: null,
        staticSensorReadings: null,
      },
      zoom: 2,
      sid: null,
      r_si_check: false,
      r_mi_check: false,
      t_heatmap_check: false,
      u_pie_check: false,
      u_mi_check: false,
      timeRange: null,
      defaultTimeRange: {begintime: '2020-04-06 00:00:00', endtime: '2020-04-11 00:00:00'}
    }
  },
  created: function () {
      this.$root.eventHub.$on('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$on('sensorSelected', this.sensorSelected);
   },
   // 最好在组件销毁前
   // 清除事件监听
   beforeDestroy: function () {
      this.$root.eventHub.$off('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$off('sensorSelected', this.sensorSelected);
   },
  mounted() {
    this.$nextTick(() => {
      this.loadMap();
    })
  },
  methods: {
    loadMap() {
      this.initMap();
      this.drawStaticPointLayer(); //添加静态传感器
      // this.drawKrigingLayer()
      // this.drawIdwLayer();
      // this.drawHeatmapLayer();
      // this.drawIdwUncertaintyLayer();
      // if(this.u_pie_check) {
      //   this.drawPies();
      // }
    },
    selfAdaptionSize() {
      let width = document.querySelector("#openlayers_container").clientWidth;
      let img = document.createElement("img");
      img.src = require('../assets/img/StHimarkMapBlank.png');
      document.querySelector("#himarkmap").style.height = width * img.height / img.width  + "px";

    },
    initMap() {
      this.map = new Map({
        // controls: defaultControls().extend([
        //   new FullScreen()
        // ]),
        target: 'himarkmap',
        layers: [
          new Image({
            source: new ImageStatic({
              url: require('../assets/img/StHimarkMapBlank.png'),
              imageExtent: this.imageExtent,
            })
          })
        ],
        view: new View({
          projection: this.getProjection(),
          center: getCenter(this.imageExtent),
          zoom: 2,
          minZoom: 2,
          maxZoom: 4,
        })
      });

      let _this = this;

      this.map.on("moveend",function(e){
        _this.zoom = _this.map.getView().getZoom();  //获取当前地图的缩放级别
        // console.log(zoom);
      }); 
    },
    getProjection() {
      return new Projection({
        // code: 'himark-image',
        // unites: 'pixels',
        extent: this.imageExtent
      })
    },
    drawStaticPointLayer() {
      let vectorSource = new VectorSource();
      this.layers.staticPointLayer = new VectorLayer({
        source: vectorSource,
      });

      d3.csv("/static/data/StaticSensorLocations.csv").then(csvdata => {
        csvdata.forEach(point => {
          let feature = new Feature({
            geometry: new Point([parseFloat(point.long), parseFloat(point.lat)])
          });
          feature.setStyle(new Style({
            image: new Circle({
                radius: 3,
                fill: new Fill({ color: "#00F" })
            })
          }));
          vectorSource.addFeature(feature);
        })
        // 点击事件
        let selectSingleClick = new Select();
        this.map.addInteraction(selectSingleClick);
        selectSingleClick.on('select', function(e) {
          var features = e.target.getFeatures().getArray();
          if(features.length > 0) {
            console.log(features[0].getGeometry());
          }
        });
      })
      this.map.addLayer(this.layers.staticPointLayer);
    },
    // 静态传感器插值层
    drawKrigingLayer() {
      let params = {
        // maxValue: 100,
        krigingModel: 'exponential',
        krigingSigma2: 0,
        krigingAlpha: 100,
        canvasAlpha: 0.20,
        // colors:["#006837", "#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d73027", "#a50026"],
      }

      let colorScale = this.color();
      let colors = [];
      for(let i=20; i<=100; i++) {
        colors.push(colorScale(i));
      }
      
      axios.post("/findAggSrrByTimeRange/", this.timeRange || this.defaultTimeRange)
        .then((response) => {
          let responseData = response.data;
          
          let values = responseData.map(d => parseFloat(d.value));
          let lngs = responseData.map(d => parseFloat(d.longitude));
          let lats = responseData.map(d => parseFloat(d.latitude));

          let letiogram = kriging.train(values, lngs, lats, params.krigingModel, params.krigingSigma2, params.krigingAlpha);
          let grid = kriging.grid(this.coords, letiogram, (this.imageExtent[2] - this.imageExtent[0]) / 75);
          
          //创建新图层
          this.layers.krigingLayer = new Image({
            extent: this.imageExtent,
            source: new ImageCanvas({
              canvasFunction: (extent, resolution, pixelRatio, size, projection) => {
                  let canvas = document.createElement('canvas');
                  canvas.width = size[0];
                  canvas.height = size[1];
                  canvas.style.display = 'block';
                  //设置canvas透明度
                  // canvas.getContext('2d').globalAlpha = params.canvasAlpha;
                  //使用分层设色渲染
                  kriging.plot(canvas, grid,
                      [extent[0], extent[2]], [extent[1], extent[3]], colors);
                  return canvas;
              },
              // projection: this.getProjection()
            })
          });
          this.layers.krigingLayer.setOpacity(0.3);
          this.map.addLayer(this.layers.krigingLayer);
          this.layers.krigingLayer.setVisible(this.r_si_check);
        })
        .catch((error) => {
          console.log(error);
        });
    },
    drawIdwLayer() {

      let _this = this;

      let colorScale = d3.scaleLinear().domain([20, 30, 50, 100]).range(["rgb(0,0,255)", "rgb(0,255,0)", "rgb(225,225,0)", "rgb(255,0,0)"])
      if(this.dataCollection.mobileSensorReadings != null) {
        render(this.dataCollection.mobileSensorReadings);
      } else {
        let url;
        let params = this.timeRange || this.defaultTimeRange;
        if(this.sid == null) {
          url = "/findMrrByTimeRange/";
        } else {
          url = "/findMrrByTimeRangeAndSid/"
          params = Object.assign({}, params, this.sid)
        } 
        axios.post(url, params)
          .then((response) => {
            this.dataCollection.mobileSensorReadings = response.data;
            render(response.data);
          })
          .catch((error) => {
            console.log(error);
          });
      }

      function render(data) {
        let griddata = _this.convertGridData(data);
        let aggGridData = griddata.map(d => {
          let value;
          if(d.list.length == 0) {
            value = null;
          } else {
            value = d3.mean(d.list);
          }
          return Object.assign({}, d, {value:value})
        })

        let idwdata = idw(aggGridData);

        let features = [];

        let usedData;
        if(_this.sid == null) {
          usedData = idwdata;
        } else {
          usedData = aggGridData;
        }
        
        usedData.forEach(d => {
          if(d.value != null) {
            let polygon = new Polygon([[[d.lngEx[0], d.latEx[0]], [d.lngEx[0], d.latEx[1]], [d.lngEx[1], d.latEx[1]], [d.lngEx[1], d.latEx[0]], [d.lngEx[0], d.latEx[0]]]]);
            let polygonFeature = new Feature(polygon);
            let style = new Style({
              fill: new Fill({
                color: colorScale(d.value),//[0, 0, 255, 0.6]
              })
            })
            if(d.list.length != 0) {
              style.stroke_ = new Stroke({
                color: 'white',
                width: 2
              })
            }
            polygonFeature.setStyle(style);
            features.push(polygonFeature)
          }
        })

        _this.layers.idwLayer = new VectorLayer({
          source: new VectorSource({
            features: features
          }),
          style: new Style({
            stroke: new Stroke({
              width: 1,
              color: "red"
            })
          })
        })
        _this.layers.idwLayer.setOpacity(0.3);
        _this.map.addLayer(_this.layers.idwLayer);
        _this.layers.idwLayer.setVisible(_this.r_mi_check);
      }


    },
    drawIdwUncertaintyLayer() {
      let _this = this;

      let colorScale = d3.scaleLinear().domain([20, 50, 100, 500]).range(["rgb(0,0,255)", "rgb(0,255,0)", "rgb(225,225,0)", "rgb(255,0,0)"])
      if(this.dataCollection.mobileSensorReadings != null) {
        render(this.dataCollection.mobileSensorReadings);
      } else {
        axios.post("/findMrrByTimeRange/", this.timeRange|| this.defaultTimeRange)
        .then((response) => {
          this.dataCollection.mobileSensorReadings = response.data;
          render(response.data);
        })
        .catch((error) => {
          console.log(error);
        });
      }

      function render(data) {
        let griddata = _this.convertGridData(data);
        let aggGridData = griddata.map(d => {
          let value;
          if(d.list.length == 0) {
            value = null;
          } else {
            value = d3.variance(d.list);
          }
          return Object.assign({}, d, {value:value})
        })

        // console.log(aggGridData.map(d => d.value))

        let idwdata = idw(aggGridData);

        let features = [];

        let usedData;
        if(_this.sid != null) {
          usedData = idwdata;
        } else {
          usedData = aggGridData;
        }
        
        usedData.forEach(d => {
          if(d.value != null) {
            let polygon = new Polygon([[[d.lngEx[0], d.latEx[0]], [d.lngEx[0], d.latEx[1]], [d.lngEx[1], d.latEx[1]], [d.lngEx[1], d.latEx[0]], [d.lngEx[0], d.latEx[0]]]]);
            let polygonFeature = new Feature(polygon);
            let style = new Style({
              fill: new Fill({
                color: colorScale(d.value),//[0, 0, 255, 0.6]
              })
            })
            if(d.list.length != 0) {
              style.stroke_ = new Stroke({
                color: 'white',
                width: 2
              })
            }
            polygonFeature.setStyle(style);
            features.push(polygonFeature)
          }
        })

        _this.layers.idwUncertaintyLayer = new VectorLayer({
          source: new VectorSource({
            features: features
          }),
          style: new Style({
            stroke: new Stroke({
              width: 1,
              color: "red"
            })
          })
        })
        _this.layers.idwUncertaintyLayer.setOpacity(0.3);
        _this.map.addLayer(_this.layers.idwUncertaintyLayer);
        _this.layers.idwUncertaintyLayer.setVisible(_this.u_mi_check);
      }


    },
    drawHeatmapLayer() {
      let vectorSource = new VectorSource();
      this.layers.heatmapLayer = new Heatmap({
        source: vectorSource,
        radius: 1,
      });

      axios.all([this.getAggSrrByTimeRange(this.timeRange || this.defaultTimeRange), this.getAggMrrByTimeRange(this.timeRange || this.defaultTimeRange)])
        .then(axios.spread((response1, response2) => {
          let features = [];
          
          response1.data.forEach(d => {
            let feature = new Feature({
              geometry: new Point([parseFloat(d.longitude), parseFloat(d.latitude)]),
              weight: d.value
            });
            features.push(feature);
          })
          response2.data.forEach(d => {
            let feature = new Feature({
              geometry: new Point([parseFloat(d.longitude), parseFloat(d.latitude)]),
              weight: d.value
            });
            features.push(feature);
          })
          vectorSource.addFeatures(features);
          this.layers.heatmapLayer.setVisible(this.t_heatmap_check);
          this.map.addLayer(this.layers.heatmapLayer)
        }))
    },
    drawMobilePointLayer() {
      let vectorSource = new VectorSource();
      this.layers.mobilePointLayer = new VectorLayer({
        source: vectorSource,
      });
      axios.post("/findMrrByTimeRange/", (this.timeRange || this.defaultTimeRange)).then((response) => {
        let pointData = response.data;
        pointData.forEach(point => {
          let feature = new Feature({
            geometry: new Point([parseFloat(point.longitude), parseFloat(point.latitude)])
          });
          feature.setStyle(new Style({
            image: new Circle({
                radius: 2,
                fill: new Fill({ color: "#00F" })
            })
          }));
          vectorSource.addFeature(feature);
        })
        this.map.addLayer(this.layers.mobilePointLayer);
      })
    },
    drawPies() {
      let _this = this;

      if(this.dataCollection.mobileSensorReadings != null) {
        render(this.dataCollection.mobileSensorReadings);
      } else {
        axios.post("/findMrrByTimeRange/", this.timeRange || this.defaultTimeRange)
        .then((response) => {
          this.dataCollection.mobileSensorReadings = response.data;
          render(response.data);
        })
        .catch((error) => {
          console.log(error);
        });
      }

      function render(data) {
        let griddata = _this.convertGridData(data);
          
        griddata.forEach(d => {
          if(d.list.length != 0) {
            let level_1 = d.list.filter(v => v<=8).length;
            let level_2 = d.list.filter(v => v>8 && v<=25).length;
            let level_3 = d.list.filter(v => v>25 && v<=60).length;
            let level_4 = d.list.filter(v => v>60 && v<=500).length;
            let level_5 = d.list.filter(v => v>500 && v<=1600).length;
            let level_6 = d.list.filter(v => v>1600).length;

            let domid = `${d.i}_${d.j}`;
            
            _this.drawPie(domid, [level_1, level_2, level_3, level_4, level_5, level_6]);
            
            let overlay = new Overlay({
              id: domid,
              element: document.getElementById(domid),
              position: [d.lngEx[0], d.latEx[1]],
              // positioning: "bottom-center", //统计图和渲染点位的位置关系
              // offset: [0, 18],//如果统计图相对于点位又偏移，可以通过此属性将统计图移回来
              stopEvent: false  //overlay也支持滚珠放大缩小
            });
            _this.map.addOverlay(overlay);

          }
        })
      }
    },
    drawPie(domid, data) {
      var colors = d3.scaleOrdinal(d3.schemeCategory10); //maps integers to colors
      // var data = [1, 1, 2, 3, 5, 8, 13, 21]; //data we want to turn into a pie chart
      var pies = d3.pie()(data); // turns into data for pie chart with start and end angles
      let radius = 8 * this.zoom;
      var arc = d3.arc()
                  .innerRadius(0) //means full circle. if not 0, would be donut
                  .outerRadius(radius) //size of circle
                  .startAngle(d =>d.startAngle) //how does it get d???
                  .endAngle(d=> d.endAngle);

      
      var svg = d3.select('#himarkmap')
                  .append('svg')
                  .attr("id", domid)
                  .append('g')
                  .attr('transform', `translate(${radius},${radius})`);
      
      svg.selectAll('path')
        .data(pies).enter().append('path')
        .attr('d', arc)
        .attr('fill', (d, i) => colors(d.value))
        .attr('stroke', '#fff')
        .style('opacity', 0.6);

      return svg;
    },
    clearPies() {
      let overlays = this.map.getOverlays().clear();
    },
    convertGridData(data) {
      let span = 0.01;
      
      let m = Math.ceil(Math.abs(this.imageExtent[1] - this.imageExtent[3]) / span);
      let n = Math.ceil(Math.abs(this.imageExtent[0] - this.imageExtent[2]) / span);

      let right = this.imageExtent[0] + n * span;
      let bottom = this.imageExtent[3] - m * span;

      let xRange = [], yRange = [];

      for(let i=0; i<m; i++) {
        yRange.push(i);
      }
      for(let j=0; j<n; j++) {
        xRange.push(j);
      }

      let xScale = d3.scaleQuantize().domain([this.imageExtent[0], right]).range(xRange);
      let yScale = d3.scaleQuantize().domain([bottom, this.imageExtent[3]]).range(yRange.reverse());

      let dim2Arr = initDim2Array();

        
      data.forEach(d => {
        let x = xScale(parseFloat(d.longitude));
        let y = yScale(parseFloat(d.latitude));

        dim2Arr[y][x].list.push(d.value) ;
        dim2Arr[y][x].list.push(d.value);
      })
      
      let griddata = [];
      for(let i=0, len=dim2Arr.length; i<len; i++) {
        for(let j=0, len2=dim2Arr[i].length; j<len2; j++) {
          let lngEx = xScale.invertExtent(j)
          let latEx = yScale.invertExtent(i);
          let obj = {i:i, j:j, latEx: latEx, lngEx: lngEx, lat: d3.mean(latEx), lng: d3.mean(lngEx), list: dim2Arr[i][j].list};
          griddata.push(obj);
        }
      }

      function initDim2Array() {
        let dim2Arr = [];
        for(let i=0; i<m; i++) {
          let row = [];
          for(let j=0; j<n; j++) {
            row.push({list: []});
          }
          dim2Arr.push(row)
        }
        return dim2Arr;
      }

      return griddata;
    },
    color() {
      return d3.scaleLinear().domain([20, 30, 50, 100]).range(["rgb(0,0,255)", "rgb(0,255,0)", "rgb(225,225,0)", "rgb(255,0,0)"]);
    },
    clearDataCollection() {
      this.dataCollection.mobileSensorReadings = null;
      this.dataCollection.staticSensorReadings = null;
    },
    clearLayers() {
      this.map.removeLayer(this.layers.krigingLayer);
      this.map.removeLayer(this.layers.idwLayer);
      this.map.removeLayer(this.layers.heatmapLayer);
      this.map.removeLayer(this.layers.idwUncertaintyLayer);
      this.layers.krigingLayer = null;
      this.layers.idwLayer = null;
      this.layers.heatmapLayer  = null;
      this.layers.idwUncertaintyLayer = null;
    },
    krigingLayerUpdate() {
      this.layers.krigingLayer.setVisible(this.r_si_check);
    },
    idwLayerUpdate() {
      this.layers.idwLayer.setVisible(this.r_mi_check);
    },
    heatmapLayerUpdate() {
      this.layers.heatmapLayer.setVisible(this.t_heatmap_check);
    },
    uncertaintyIdwLayerUpdate() {
      this.layers.idwUncertaintyLayer.setVisible(this.u_mi_check);
    },
    piesUpdate() {
      if(this.u_pie_check) {
        this.drawPies();
      } else {
        this.clearPies();
      }
    },
    selectChanged(value) {
      this.currentSelectValue = value;
    },
    timeRangeUpdated(params) {
      this.timeRange = params;
      if(params == null) {
        return;
      }
      this.clearDataCollection();
      this.clearLayers();
      this.clearPies();
      this.drawKrigingLayer()
      this.drawIdwLayer();
      this.drawHeatmapLayer();
      this.drawIdwUncertaintyLayer();
      if(this.u_pie_check) {
        this.drawPies();
      }
    },
    getAggMrrByTimeRange(params) {
      return axios.post('/findAggMrrByTimeRange/', params);
    },
    getAggSrrByTimeRange(params) {
      return axios.post('/findAggSrrByTimeRange/', params);
    },
    sensorSelected(params) {
      this.sid = params;
      console.log(params)
      this.clearDataCollection();
      this.clearLayers();
      this.clearPies();
      this.drawKrigingLayer()
      this.drawIdwLayer();
      this.drawHeatmapLayer();
      this.drawIdwUncertaintyLayer();
      if(this.u_pie_check) {
        this.drawPies();
      }
    }
  },
  watch: {
    zoom(newValue, oldValue) {
      if(this.u_pie_check) {
        this.clearPies();
        this.drawPies();
      }
    }
  },
  computed: {
    coords: function() {
      return [[[this.imageExtent[0], this.imageExtent[3]], [this.imageExtent[2], this.imageExtent[3]], [this.imageExtent[2], this.imageExtent[1]], [this.imageExtent[0], this.imageExtent[1]]]]
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#openlayers_container {
  height: 100%;
}
#openlayers_container .sidepanel {
  width: 100%;
  height: 8%;
  background-color: #ccc;
  opacity: 0.8;
  /* position: absolute; */
}
#openlayers_container .nav {
  height: 100%;
  position: relative;
}
#openlayers_container .nav-select {
  position: absolute;
  top: 50%;
  left: 10px;
}
#openlayers_container .nav-checkbox-group {
  position: absolute;
  top: 50%;
  left: 180px;
}
#openlayers_container .el-select {
  top: -14px;
}
#openlayers_container .el-checkbox {
  top: -9px;
}
#openlayers_container  >>> span {
  font-size: 12px;
}
.el-select-dropdown__item >>> span {
  font-size: 12px;
}
#himarkmap {
  width: 100%;
  height: 90%;
  margin-top: 5px;
  /* position: absolute;
  top: 10%; */
}
.el-tabs {
  height: 30px;
}
</style>

