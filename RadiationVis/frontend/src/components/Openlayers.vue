<template>
  <div id="openlayers_container">
    <!-- <div class="sidepanel">
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
          <el-checkbox v-model="r_si_kriging_check" @change="krigingLayerUpdate" size="mini">SI</el-checkbox>
          <el-checkbox v-model="r_mi_idw_check" @change="idwMLayerUpdate" size="mini">MI</el-checkbox>
          <el-checkbox v-model="r_s_check" @change="SRLayerUpdate" size="mini">S</el-checkbox>
          <el-checkbox v-model="r_m_check" @change="MRLayerUpdate" size="mini">M</el-checkbox>
        </div>
        <div class="nav-checkbox-group" v-else-if="currentSelectValue=='uncertainty'">
          <el-checkbox v-model="u_mi_check" @change="uncertaintyidwMLayerUpdate" size="mini">MS Interpolation</el-checkbox>
          <el-checkbox v-model="u_pie_check" @change="piesUpdate" size="mini">Pies</el-checkbox>
        </div>
        <div class="nav-checkbox-group" v-else-if="currentSelectValue=='track'">
          <el-checkbox v-model="t_heatmap_check" @change="heatmapLayerUpdate" size="mini">Heatmap</el-checkbox>
        </div>
      </div> 
    </div> -->
    <div id="himarkmap"></div>
    <div id="popup" class="ol-popup">
      <a href="#" id="popup-closer" class="ol-popup-closer"></a>
      <div id="popup-content"></div>
    </div>
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
import {Style, Circle, Fill, Stroke, Icon} from 'ol/style'
import Select from 'ol/interaction/Select'
import {defaults as defaultControls, FullScreen} from 'ol/control';
import Overlay from 'ol/Overlay';

export default {
  name: 'Openlayers',
  props: {
    mapControl: Object,
  },
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
        SRLayer: null,
        mobilePointLayer: null,
        krigingLayer: null,
        idwMLayer: null,
        idwSLayer: null,
        heatmapLayer: null,
        idwUncertaintyLayer: null,
        MRLayer: null,
        pathsLayer: null,
      },
      dataCollection: {
        staticSensorGridData: null,
        mobileSensorGridData: null,
        mobileSensorReadings: null,
        staticSensorReadings: null,
        mobileUncertaintyGridData: null,
        mobilePathData: null,
      },
      zoom: 1.4,
      sid: null,
      timeRange: null,
      mapTimeRange: null,
      defaultTimeRange: {begintime: '2020-04-06 00:00:00', endtime: '2020-04-11 00:00:00'},
      popup: {
        container: null,
        content: null,
        closer: null,
      }
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
      this.addSelectEvent();
    },
    selfAdaptionSize() {
      let width = document.querySelector("#openlayers_container").clientWidth;
      let img = document.createElement("img");
      img.src = require('../assets/img/StHimarkMapRoad.png');
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
              url: require('../assets/img/StHimarkMapRoad.png'),
              imageExtent: this.imageExtent,
            })
          })
        ],
        view: new View({
          projection: this.getProjection(),
          center: getCenter(this.imageExtent),
          zoom: 1.4,
          minZoom: 1.4,
          maxZoom: 4,
        })
      });

      let _this = this;

      this.map.on("moveend",function(e){
        _this.zoom = _this.map.getView().getZoom();  //获取当前地图的缩放级别
      }); 

      // this.map.on('click', function(evt) {
      //   var feature = _this.map.forEachFeatureAtPixel(evt.pixel,
      //     function(feature) {
      //       return feature;
      //     });
      //   console.log(feature)
      // });

    },
    addSelectEvent() {
      if(!this.popup.container) {
        this.popup.container = document.getElementById('popup');
      }
      if(!this.popup.content) {
        this.popup.content = document.getElementById('popup-content');
      }
      if(!this.popup.closer) {
        this.popup.closer = document.getElementById('popup-closer');
      }
      let popup = this.map.getOverlayById('popup');
      if(!popup) {
        popup = new Overlay({
          id: 'popup',
          element: this.popup.container,
          positioning: 'bottom-center',
          stopEvent: false,
          autoPan: true,
          autoPanAnimation: {
            duration: 250
          }
          // offset: [0, -50]
        });
        this.popup.closer.onclick = function() {
          popup.setPosition(undefined);
          // this.popup.closer.blur();
          return false;
        };
        
        this.map.addOverlay(popup);
      }
      let _this = this;
      let selectSingleClick = new Select();
      this.map.addInteraction(selectSingleClick);
      selectSingleClick.on('select', function(e) {
        let features = e.target.getFeatures().getArray();
        if(features.length > 0) {
          let geo = features[0].getGeometry();
          console.log(geo)
          let extent = geo.getExtent()
          // console.log(extent)
          axios.post('/findSensorByTimeRangeAndCoords/', Object.assign({}, _this.timeRange, {coords: extent}))
            .then((response) => {
              let coordinates = geo.getCoordinates();
              popup.setPosition(coordinates[0][1]);
              _this.popup.content.innerHTML = JSON.stringify(response.data)
            })
            .catch((error) => {
              console.log(error);
            });
        }
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
            image: new Icon({
                // radius: 3,
                // fill: new Fill({ color: "#00F" })
              src: require('../assets/img/static.png'),
              scale: 0.2
              // size: [50, 50]
            })
          }));
          vectorSource.addFeature(feature);
        })
        // 点击事件
        // let selectSingleClick = new Select();
        // this.map.addInteraction(selectSingleClick);
        // selectSingleClick.on('select', function(e) {
        //   var features = e.target.getFeatures().getArray();
        //   if(features.length > 0) {
        //     console.log(features[0].getGeometry());
        //   }
        // });
      })
      this.map.addLayer(this.layers.staticPointLayer);
      this.layers.staticPointLayer.setVisible(this.mapControl.icon_s_check);
    },
    drawSRLayer() {
      let _this = this;
      let colorScale = d3.scaleLinear().domain([12, 25]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      if(this.dataCollection.staticSensorReadings) {
        render(this.dataCollection.staticSensorReadings);
      } else {
        axios.post("/findAggSrrByTimeRange/", this.timeRange || this.defaultTimeRange).then(response => {
          this.dataCollection.staticSensorReadings = response.data;
          render(this.dataCollection.staticSensorReadings);
        })
      }
      function render(data) {
        let vectorSource = new VectorSource();
          _this.layers.SRLayer = new VectorLayer({
            source: vectorSource,
          });
        data.forEach(point => {
          let feature = new Feature({
            geometry: new Point([parseFloat(point.longitude), parseFloat(point.latitude)])
          });
          feature.setStyle(new Style({
            image: new Circle({
                radius: 15 * _this.zoom,
                fill: new Fill({ color: colorScale(point.value) })
            })
          }));
          vectorSource.addFeature(feature);
        })
        _this.layers.SRLayer.setOpacity(0.3);
        _this.layers.SRLayer.setVisible(_this.mapControl.r_s_check);
        _this.map.addLayer(_this.layers.SRLayer);
      }
    },
    // 静态传感器插值层
    drawKrigingLayer() {
      let _this = this;
      let colorScale = d3.scaleLinear().domain([0, 100]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      if(this.dataCollection.staticSensorReadings) {
        render(this.dataCollection.staticSensorReadings);
      } else {
        axios.post("/findAggSrrByTimeRange/", this.timeRange || this.defaultTimeRange).then(response => {
          this.dataCollection.staticSensorReadings = response.data;
          render(this.dataCollection.staticSensorReadings);
        })
      }

      function render(data) {
        let params = {
          // maxValue: 100,
          krigingModel: 'exponential',
          krigingSigma2: 0,
          krigingAlpha: 100,
          canvasAlpha: 0.20,
          colors: ["#006837", "#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d73027", "#a50026"],
        }

        let colorScale = _this.color();
        let colors = [];
        for(let i=0; i<=100; i++) {
          colors.push(colorScale(i));
        }
          
        let values = data.map(d => parseFloat(d.value));
        let lngs = data.map(d => parseFloat(d.longitude));
        let lats = data.map(d => parseFloat(d.latitude));

        let letiogram = kriging.train(values, lngs, lats, params.krigingModel, params.krigingSigma2, params.krigingAlpha);
        let grid = kriging.grid(_this.coords, letiogram, (_this.imageExtent[2] - _this.imageExtent[0]) / 75);
        
        //创建新图层
        _this.layers.krigingLayer = new Image({
          extent: _this.imageExtent,
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
                    [extent[0], extent[2]], [extent[1], extent[3]], params.colors);
                return canvas;
            },
            // projection: this.getProjection()
          })
        });
        _this.layers.krigingLayer.setOpacity(0.3);
        _this.map.addLayer(_this.layers.krigingLayer);
        _this.layers.krigingLayer.setVisible(_this.mapControl.r_si_kriging_check);
      }
    },
    drawIdwMLayer() {
      this.layers.idwMLayer = new VectorLayer({
        style: new Style({
          stroke: new Stroke({
            width: 1,
            color: "red"
          })
        })
      })
      let colorScale = d3.scaleLinear().domain([20, 100]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      if(this.dataCollection.mobileSensorGridData != null) {
        this.renderIdwLayer(this.dataCollection.mobileSensorGridData, this.layers.idwMLayer, this.mapControl.r_mi_idw_check, colorScale);
      } else {
        axios.post("/getMobileIdwDataByTimeRange/", this.timeRange || this.defaultTimeRange)
          .then((response) => {
            this.dataCollection.mobileSensorGridData = response.data;
            this.renderIdwLayer(this.dataCollection.mobileSensorGridData, this.layers.idwMLayer, this.mapControl.r_mi_idw_check, colorScale);
          })
          .catch((error) => {
            console.log(error);
          });
      }
    },
    drawIdwSLayer() {
      this.layers.idwSLayer = new VectorLayer({
        // style: new Style({
        //   stroke: new Stroke({
        //     width: 1,
        //     color: "white"
        //   })
        // })
      })
      let colorScale = d3.scaleLinear().domain([12, 20]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      if(this.dataCollection.staticSensorGridData != null) {
        this.renderIdwLayer(this.dataCollection.staticSensorGridData, this.layers.idwSLayer, this.mapControl.r_si_idw_check, colorScale);
      } else {
        axios.post("/getStaticIdwDataByTimeRange/", this.timeRange || this.defaultTimeRange)
          .then((response) => {
            this.dataCollection.staticSensorGridData = response.data;
            this.renderIdwLayer(this.dataCollection.staticSensorGridData, this.layers.idwSLayer, this.mapControl.r_si_idw_check, colorScale);
          })
          .catch((error) => {
            console.log(error);
          });
      }
    },
    renderIdwLayer(idwdata, layer, isVisibale, colorScale) {
        // let griddata = this.convertGridData(data);
        // let aggGridData = griddata.map(d => {
        //   let value;
        //   if(d.list.length == 0) {
        //     value = null;
        //   } else {
        //     value = d3.mean(d.list);
        //   }
        //   return Object.assign({}, d, {value:value})
        // })

        // let idwdata = idw(aggGridData);

        let features = [];

        idwdata.forEach(d => {
          let polygon = new Polygon([[[d.lngEx[0], d.latEx[0]], [d.lngEx[0], d.latEx[1]], [d.lngEx[1], d.latEx[1]], [d.lngEx[1], d.latEx[0]], [d.lngEx[0], d.latEx[0]]]]);
          let polygonFeature = new Feature(polygon);
          let style = new Style({
            fill: new Fill({
              color: colorScale(d.mean),//[0, 0, 255, 0.6]
            })
          })
          if(d.flag) {
            style.stroke_ = new Stroke({
              color: 'white',
              width: 1
            })
          } 
          polygonFeature.setStyle(style);
          features.push(polygonFeature)
        })
      layer.setSource(new VectorSource({
        features: features
      }))
      layer.setOpacity(0.3);
      this.map.addLayer(layer);
      layer.setVisible(isVisibale);
    },
    // drawMRLayer() {

    //   let _this = this;

    //   if(this.dataCollection.mobileSensorReadings != null) {
    //     render(this.dataCollection.mobileSensorReadings);
    //   } else {
    //     axios.post("/findMrrByTimeRange/", this.timeRange || this.defaultTimeRange)
    //       .then((response) => {
    //         this.dataCollection.mobileSensorReadings = response.data;
    //         render(response.data);
    //       })
    //       .catch((error) => {
    //         console.log(error);
    //       });
    //   }

    //   // axios.all([
    //   //   axios.post("/findMrrByTimeRange/", this.timeRange),
    //   //   axios.post("/findSrrByTimeRange/", this.timeRange),
    //   // ]).then(axios.spread((response1, response2) => {
    //   //   let data = response1.data.concat(response2.data);
    //   //   render(data);
    //   // })) 

    //   function render(data) {
    //     let griddata = _this.convertGridData(data);
    //     let aggGridData = griddata.map(d => {
    //       let value;
    //       if(d.list.length == 0) {
    //         value = null;
    //       } else {
    //         value = d3.mean(d.list);
    //       }
    //       return Object.assign({}, d, {value:value})
    //     })

    //     let idwdata = idw(aggGridData);

    //     let features = [];

    //     let colorScale = d3.scaleLinear().domain([20, 30, 50, 100]).range(["rgb(0,0,255)", "rgb(0,255,0)", "rgb(225,225,0)", "rgb(255,0,0)"])
        
    //     idwdata.forEach(d => {
    //       if(d.value != null) {
    //         let polygon = new Polygon([[[d.lngEx[0], d.latEx[0]], [d.lngEx[0], d.latEx[1]], [d.lngEx[1], d.latEx[1]], [d.lngEx[1], d.latEx[0]], [d.lngEx[0], d.latEx[0]]]]);
    //         let polygonFeature = new Feature(polygon);
    //         let style;
    //         if(d.list.length != 0) {
    //           style = new Style({
    //             fill: new Fill({
    //               color: colorScale(d.value),//[0, 0, 255, 0.6]
    //             })
    //           })
    //         } 
    //         // else {
    //         //   style = new Style({
    //         //     fill: new Fill({
    //         //       color: [0, 0, 0, 0]
    //         //     })
    //         //   })
    //         // }
    //         polygonFeature.setStyle(style);
    //         features.push(polygonFeature)
    //       }
    //     })

    //     _this.layers.MRLayer = new VectorLayer({
    //       source: new VectorSource({
    //         features: features
    //       }),
    //       style: new Style({
    //         stroke: new Stroke({
    //           width: 2,
    //           color: "white"
    //         })
    //       })
    //     })
    //     _this.layers.MRLayer.setOpacity(0.3);
    //     _this.map.addLayer(_this.layers.MRLayer);
    //     _this.layers.MRLayer.setVisible(_this.mapControl.r_m_check);
    //   }


    // },
    drawIdwUncertaintyLayer() {
      if(this.dataCollection.mobileSensorGridData != null) {
        this.renderIdwUncertaintyLayer(this.dataCollection.mobileSensorGridData);
      } else {
        axios.post("/getMobileIdwDataByTimeRange/", this.timeRange|| this.defaultTimeRange)
        .then((response) => {
          this.dataCollection.mobileSensorGridData = response.data;
          this.renderIdwUncertaintyLayer(response.data);
        })
        .catch((error) => {
          console.log(error);
        });
      }
    },
    renderIdwUncertaintyLayer(idwdata) {
      // let griddata = this.convertGridData(data);
      // let aggGridData = griddata.map(d => {
      //   let value;
      //   if(d.list.length == 0) {
      //     value = null;
      //   } else {
      //     value = d3.variance(d.list);
      //   }
      //   return Object.assign({}, d, {value:value})
      // })

      // let idwdata = idw(aggGridData);

      let features = [];

      let colorScale = d3.scaleLinear().domain([0, 200]).range(["rgb(0,255,0)", "rgb(255,0,0)"])
      let scale = d3.scaleLinear().domain([0,200]).range([0,10])

      idwdata.forEach(d => {
        let polygon = new Polygon([[[d.lngEx[0], d.latEx[0]], [d.lngEx[0], d.latEx[1]], [d.lngEx[1], d.latEx[1]], [d.lngEx[1], d.latEx[0]], [d.lngEx[0], d.latEx[0]]]]);
        let polygonFeature = new Feature(polygon);
        // let color = colorScale(d.variance).replace("rgb(", "").replace(")", "");
        // color = color.split(",");
        let style = new Style({
          // fill: new Fill({
          //   color: colorScale(Math.sqrt(d.variance)),
          // })
          stroke: new Stroke({
            color: 'white',
            width: scale(Math.sqrt(d.variance))
          })
        })
        // if(!d.flag) {
        //   style.stroke_ = new Stroke({
        //     color: 'white',
        //     width: scale(Math.sqrt(d.variance))
        //   })
        // }
        polygonFeature.setStyle(style);
        features.push(polygonFeature)
        
      })

      this.layers.idwUncertaintyLayer = new VectorLayer({
        source: new VectorSource({
          features: features
        }),
        // style: new Style({
        //   stroke: new Stroke({
        //     width: 1,
        //     color: "white"
        //   })
        // })
      })
      this.layers.idwUncertaintyLayer.setOpacity(0.6);
      this.map.addLayer(this.layers.idwUncertaintyLayer);
      this.layers.idwUncertaintyLayer.setVisible(this.mapControl.u_mi_check);
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
          this.layers.heatmapLayer.setVisible(this.mapControl.t_heatmap_check);
          this.map.addLayer(this.layers.heatmapLayer)
        }))
    },
    drawMobilePointLayer() {
      let vectorSource = new VectorSource();
      this.layers.mobilePointLayer = new VectorLayer({
        source: vectorSource,
      });
      axios.post("/getLastCoordByTimeRange/", (this.timeRange || this.defaultTimeRange)).then((response) => {
        let pointData = response.data;
        pointData.forEach(point => {
          let feature = new Feature({
            geometry: new Point([parseFloat(point.lnglat[0]), parseFloat(point.lnglat[1])])
          });
          feature.setStyle(new Style({
            image: new Icon({
                // radius: 2,
                // fill: new Fill({ color: "#00F" })
                src: require("../assets/img/mobile.png"),
                scale: 0.1,
            })
          }));
          vectorSource.addFeature(feature);
        })
        this.layers.mobilePointLayer.setVisible(this.mapControl.icon_m_check);
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
    drawPath(params) {
      let _this = this;

      if(this.layers.pathsLayer) {
        this.layers.pathsLayer = null;
      }
      
      axios.post("/getPathByTimeRangeAndSid/", Object.assign({}, this.timeRange || this.defaultTimeRange, {sid: params.sid}))
        .then((response) => {
          let data = response.data.sort((a, b) => new Date(a.time).getTime()-new Date(b.time).getTime());
          console.log(data)
          render(data);
        })

      function render(data) {
        let vectorSource = new VectorSource();
        _this.layers.pathsLayer = new VectorLayer({
          source: vectorSource,
        });
        
        for(let j=0, pathLen=data.length; j<pathLen-1; j++) {
          let feature = new Feature({
            geometry: new LineString([[data[j].longitude, data[j].latitude], [data[j+1].longitude, data[j+1].latitude]])
          });
          vectorSource.addFeature(feature);
        }
        _this.layers.pathsLayer.setVisible(true);
        _this.map.addLayer(_this.layers.pathsLayer);
      }
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
      return d3.scaleLinear().domain([0, 10, 20, 30]).range(["rgb(0,0,255)", "rgb(0,255,0)", "rgb(225,225,0)", "rgb(255,0,0)"]);
    },
    clearDataCollection() {
      this.dataCollection.staticSensorGridData = null;
      this.dataCollection.mobileSensorGridData = null;
      this.dataCollection.mobileSensorReadings = null;
      this.dataCollection.staticSensorReadings = null;
      this.dataCollection.mobilePathData = null;
    },
    clearLayers() {
      this.map.removeLayer(this.layers.krigingLayer);
      this.map.removeLayer(this.layers.idwMLayer);
      this.map.removeLayer(this.layers.idwSLayer);
      this.map.removeLayer(this.layers.mobilePointLayer);
      this.map.removeLayer(this.layers.heatmapLayer);
      this.map.removeLayer(this.layers.idwUncertaintyLayer);
      this.map.removeLayer(this.layers.MRLayer);
      this.map.removeLayer(this.layers.SRLayer);
      this.layers.krigingLayer = null;
      this.layers.idwMLayer = null;
      this.layers.idwSLayer = null;
      this.layers.heatmapLayer  = null;
      this.layers.idwUncertaintyLayer = null;
      this.layers.MRLayer = null;
      this.layers.SRLayer = null;
      this.layers.mobilePointLayer = null;
    },
    krigingLayerUpdate() {
      if(this.layers.krigingLayer) {
        this.layers.krigingLayer.setVisible(this.mapControl.r_si_kriging_check);
      }
    },
    idwMLayerUpdate() {
     if(this.layers.idwMLayer) {
       this.layers.idwMLayer.setVisible(this.mapControl.r_mi_idw_check);
     }
    },
    idwSLayerUpdate() {
      if(this.layers.idwSLayer) {
        this.layers.idwSLayer.setVisible(this.mapControl.r_si_idw_check);
      }
    },
    heatmapLayerUpdate() {
      if(this.layers.heatmapLayer) {
        this.layers.heatmapLayer.setVisible(this.mapControl.t_heatmap_check);
      }
    },
    uncertaintyidwLayerUpdate() {
      if(this.layers.idwUncertaintyLayer) {
        this.layers.idwUncertaintyLayer.setVisible(this.mapControl.u_mi_check);
      }
    },
    SRLayerUpdate() {
      if(this.layers.SRLayer) {
       this.layers.SRLayer.setVisible(this.mapControl.r_mi_idw_check);
      }
    },
    staticPointLayerUpdate() {
      if(this.layers.staticPointLayer) {
        this.layers.staticPointLayer.setVisible(this.mapControl.icon_s_check);
      }
    },  
    mobilePointLayerUpdate() {
      if(this.layers.mobilePointLayer) {
       this.layers.mobilePointLayer.setVisible(this.mapControl.icon_m_check);
      }
    },
    allLayerUpdate() {
      this.staticPointLayerUpdate();
      this.mobilePointLayerUpdate();
      this.SRLayerUpdate();
      this.idwSLayerUpdate();
      this.idwMLayerUpdate();
      this.uncertaintyidwLayerUpdate();
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
      this.sid = null;
      if(params == null) {
        return;
      }
      this.clearDataCollection();
      this.clearLayers();
      // this.clearPies();

      this.addSelectEvent();
      
      if(this.mapControl.r_s_check) {
        this.drawSRLayer();
      }
      if(this.mapControl.icon_s_check && this.layers.staticPointLayer == null) {
        this.drawStaticPointLayer();
      }
      if(this.mapControl.icon_m_check) {
        this.drawMobilePointLayer();
      }
      if(this.mapControl.r_mi_idw_check) {
        this.drawIdwMLayer();
      }
      if(this.mapControl.r_si_idw_check) {
        this.drawIdwSLayer();
      }
      if(this.mapControl.u_mi_check) {
        this.drawIdwUncertaintyLayer();
      }
      if(this.mapControl.u_pie_check) {
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
    //  this.drawPath(params);
    }
  },
  watch: {
    zoom(newValue, oldValue) {
      if(this.u_pie_check) {
        this.clearPies();
        this.drawPies();
      }
      if(this.mapControl.r_mi_idw_check) {
        this.map.removeLayer(this.layers.SRLayer);
        this.layers.SRLayer = null;
        this.drawSRLayer();
      }
    },
    mapControl: {
      handler(newValue,oldValue){
        if(this.timeRange == null) {
          return;
        }
        // if(newValue.r_si_kriging_check && this.layers.krigingLayer == null) {
        //   this.drawKrigingLayer();
        // }
        console.log(newValue)
        if(newValue.r_s_check && this.layers.SRLayer == null) {
          this.drawSRLayer();
        }
        if(newValue.icon_s_check && this.layers.staticPointLayer == null) {
          this.drawStaticPointLayer();
        }
        if(newValue.icon_m_check && this.layers.mobilePointLayer == null) {
          this.drawMobilePointLayer();
        }
        if(newValue.r_si_idw_check && this.layers.idwSLayer == null) {
          this.drawIdwSLayer();
        }
        if(newValue.r_mi_idw_check && this.layers.idwMLayer == null) {
          this.drawIdwMLayer();
        }
        if(newValue.u_mi_check && this.layers.idwUncertaintyLayer == null) {
          this.drawIdwUncertaintyLayer();
        }
        this.clearPies();
        if(newValue.u_pie_check) {
          this.drawPies();
        }
        this.allLayerUpdate();
      },
      deep:true
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
/* #openlayers_container .sidepanel {
  width: 100%;
  height: 8%;
  background-color: #ccc;
  opacity: 0.8;
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
} */
#himarkmap {
  width: 100%;
  height: 100%;
  margin-top: 5px;
  /* position: absolute;
  top: 10%; */
}
.el-tabs {
  height: 30px;
}
.ol-popup {
  position: absolute;
  background-color: white;
  -webkit-filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
  filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
  padding: 15px;
  border-radius: 10px;
  border: 1px solid #cccccc;
  bottom: 12px;
  left: -50px;
  min-width: 200px;
  font-size: 12px;
}
.ol-popup:after, .ol-popup:before {
  top: 100%;
  border: solid transparent;
  content: " ";
  height: 0;
  width: 0;
  position: absolute;
  pointer-events: none;
}
.ol-popup:after {
  border-top-color: white;
  border-width: 10px;
  left: 48px;
  margin-left: -10px;
}
.ol-popup:before {
  border-top-color: #cccccc;
  border-width: 11px;
  left: 48px;
  margin-left: -11px;
}
.ol-popup-closer {
  text-decoration: none;
  position: absolute;
  top: 2px;
  right: 8px;
}
.ol-popup-closer:after {
  content: "✖";
}
</style>

