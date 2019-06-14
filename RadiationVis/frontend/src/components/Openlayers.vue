<template>
  <div id="openlayers_container">
    <div class="sidepanel">
        <!-- <span class="sidepanel-title">Side Panel</span> -->
        <el-checkbox v-model="checked1" @change="krigingLayerUpdate">Static</el-checkbox>
        <el-checkbox v-model="checked2" @change="idwLayerUpdate">Mobile</el-checkbox>
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
// import {Image as ImageLayer, Vector as VectorLayer} from 'ol/layer';
import Image from 'ol/layer/Image'
import VectorLayer from 'ol/layer/Vector'
// import {ImageStatic, Vector as VectorSource} from 'ol/source';
import ImageStatic from 'ol/source/ImageStatic'
import ImageCanvas from 'ol/source/ImageCanvas'
import VectorSource from 'ol/source/Vector'
import {getCenter} from 'ol/extent';
import Projection from 'ol/proj/Projection';
import {Point, LineString, Polygon} from 'ol/geom'
import {Style, Circle, Fill, Stroke} from 'ol/style'
import Select from 'ol/interaction/Select'
import {defaults as defaultControls, FullScreen} from 'ol/control';

export default {
  name: 'Openlayers',
  data() {
    return {
      himarkmap: new CityMap(),
      imageExtent: [-120.0, 0, -119.711751, 0.238585], //[left, bottom, right, top]
      map: null, 
      ssLayer: null, //静态传感器层
      ssILayer: null,
      krigingLayer: null,
      idwLayer: null,
      checkList: null,
      checked1: false,
      checked2: false
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.loadMap();
    })
  },
  methods: {
    loadMap() {
      // this.selfAdaptionSize();
      this.initMap();
      this.addSSLayer(); //添加静态传感器
      this.drawKrigingLayer();
      // this.drawIdwLayer();
      this.drawIdwLayer();
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
          zoom: 1.2,
          // minZoom: 1.2,
          maxZoom: 5,
        })
      });
    },
    getProjection() {
      return new Projection({
        // code: 'himark-image',
        unites: 'pixels',
        extent: this.imageExtent
      })
    },
    addSSLayer() {
      let vectorSource = new VectorSource();
      this.ssLayer = new VectorLayer({
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
      this.map.addLayer(this.ssLayer);
    },
    // 静态传感器插值层
    drawKrigingLayer() {
      let params = {
        // maxValue: 100,
        krigingModel: 'exponential',
        krigingSigma2: 0,
        krigingAlpha: 100,
        canvasAlpha: 0.20,
        colors:["#006837", "#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d73027", "#a50026"],
      }
      
      axios.post("/findAggSrrByTimeRange/", {begintime: '2020-04-06 06:00:00', endtime: '2020-04-06 07:00:00'})
        .then((response) => {
          let responseData = response.data;
          
          let values = responseData.map(d => parseFloat(d.value));
          let lngs = responseData.map(d => parseFloat(d.longitude));
          let lats = responseData.map(d => parseFloat(d.latitude));

          let letiogram = kriging.train(values, lngs, lats, params.krigingModel, params.krigingSigma2, params.krigingAlpha);
          let grid = kriging.grid(this.coords, letiogram, (this.imageExtent[2] - this.imageExtent[0]) / 100);
          
          //创建新图层
          this.krigingLayer = new Image({
            source: new ImageCanvas({
              canvasFunction: (extent, resolution, pixelRatio, size, projection) => {
                  let canvas = document.createElement('canvas');
                  canvas.width = size[0];
                  canvas.height = size[1];
                  canvas.style.display = 'block';
                  //设置canvas透明度
                  canvas.getContext('2d').globalAlpha = params.canvasAlpha;
                  //使用分层设色渲染
                  kriging.plot(canvas, grid,
                      [extent[0], extent[2]], [extent[1], extent[3]], params.colors);
                  return canvas;
              },
              projection: this.getProjection()
            })
          });
        })
        .catch((error) => {
          console.log(error);
        });
    },
    drawIdwLayer() {
      let span = 0.01;
      
      let m = Math.ceil(Math.abs(this.imageExtent[1] - this.imageExtent[3]) / span);
      let n = Math.ceil(Math.abs(this.imageExtent[0] - this.imageExtent[2]) / span);

      let right = this.imageExtent[0] + n * span;
      let bottom = this.imageExtent[3] - m * span;

      // [-120.0, 0, -119.711751, 0.238585], [left, bottom, right, top]
      // console.log(m, n, right, bottom);

      let features = [];
      let xRange = [], yRange = [];
      xRange.push(0);
      yRange.push(0);

      for(let i=1; i<m; i++) {
        // let lineFeature = new Feature(new LineString([[this.imageExtent[0], this.imageExtent[3] - i * span], [this.imageExtent[2], this.imageExtent[3] - i * span]]));
        // features.push(lineFeature);

        yRange.push(i);
      }
      for(let j=1; j<n; j++) {
        // let lineFeature = new Feature(new LineString([[this.imageExtent[0] + j * span, this.imageExtent[1]], [this.imageExtent[0] + j * span, this.imageExtent[3]]]));
        // features.push(lineFeature);

        xRange.push(j);
      }

      let xScale = d3.scaleQuantize().domain([this.imageExtent[0], right]).range(xRange);
      let yScale = d3.scaleQuantize().domain([bottom, this.imageExtent[3]]).range(yRange.reverse());

      function initDim2Array() {
        let dim2Arr = [];
        for(let i=0; i<m; i++) {
          let row = [];
          for(let j=0; j<n; j++) {
            row.push({sum: 0, count: 0});
          }
          dim2Arr.push(row)
        }
        return dim2Arr;
      }

      let colorScale = d3.scaleLinear().domain([20, 30, 50, 100]).range(["rgb(0,0,255,0.3)", "rgb(0,255,0,0.3)", "rgb(225,225,0,0.3)", "rgb(255,0,0,0.3)"])

      axios.post("/findAggMrrByTimeRange/", {begintime: '2020-04-08 08:00:00', endtime: '2020-04-08 09:00:00'})
      .then((response) => {
        let responseData = response.data;

        let dim2Arr = initDim2Array();
        let i = 0
        responseData.forEach(d => {
          
          let x = xScale(parseFloat(d.longitude));
          let y = yScale(parseFloat(d.latitude));

          dim2Arr[y][x].sum += d.value;
          dim2Arr[y][x].count ++;
        }) 

        for(let i=0; i<m; i++) {
          for(let j=0; j<n; j++) {
            if(dim2Arr[i][j].count == 0) {
              dim2Arr[i][j].value = null;
            } else {
              dim2Arr[i][j].value = dim2Arr[i][j].sum / dim2Arr[i][j].count;
            }
          }
        }

        // let result = dim2Arr.map((row, i) => row.map((d, j) => {
        //   let lngEx = xScale.invertExtent(j)
        //   let latEx = yScale.invertExtent(i);
        //   return {latEx: latEx, lngEx: lngEx, lat: d3.mean(latEx), lng: d3.mean(lngEx), value: d.value}
        // }));

        let griddata = [];
        for(let i=0, len=dim2Arr.length; i<len; i++) {
          for(let j=0, len2=dim2Arr[i].length; j<len2; j++) {
            let lngEx = xScale.invertExtent(j)
            let latEx = yScale.invertExtent(i);
            griddata.push({latEx: latEx, lngEx: lngEx, lat: d3.mean(latEx), lng: d3.mean(lngEx), value: dim2Arr[i][j].value});
          }
        }

        let idwdata = idw(griddata);
        
        idwdata.forEach(d => {
          if(d.value != null) {
            let polygonFeature = new Feature(new Polygon([[[d.lngEx[0], d.latEx[0]], [d.lngEx[0], d.latEx[1]], [d.lngEx[1], d.latEx[1]], [d.lngEx[1], d.latEx[0]], [d.lngEx[0], d.latEx[0]]]]));
            polygonFeature.setStyle(new Style({fill: new Fill({
              color: colorScale(d.value)//[0, 0, 255, 0.6]
            })}))
            features.push(polygonFeature)
          }
        })

        this.idwLayer = new VectorLayer({
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
      // this.map.addLayer(this.idwLayer)
      })
      .catch((error) => {
        console.log(error);
      });


    },
    // drawIdwLayer() {
    //   axios.post("/findAggMrrByTimeRange/", {begintime: '2020-04-06 06:00:00', endtime: '2020-04-06 07:00:00'})
    //     .then((response) => {
    //       let responseData = response.data;
          
    //       let values = responseData.map(d => parseFloat(d.value));
    //       let lngs = responseData.map(d => parseFloat(d.longitude));
    //       let lats = responseData.map(d => parseFloat(d.latitude));

    //       //创建新图层
    //       this.idwLayer = new Image({
    //         source: new ImageCanvas({
    //           canvasFunction: (extent, resolution, pixelRatio, size, projection) => {
    //               let canvas = document.createElement('canvas');
    //               canvas.width = size[0];
    //               canvas.height = size[1];
    //               canvas.style.display = 'block';
    //               //设置canvas透明度
    //               let ctx = canvas.getContext('2d')
    //               ctx.globalAlpha = 0.2;
                  
    //               let gridsize = 50;
    //               let m = Math.ceil(parseInt(size[0] / gridsize));
    //               let n = Math.ceil(parseInt(size[1] / gridsize));

    //               ctx.beginPath();
    //               for(let i=0; i<m; i++) {
    //                 ctx.moveTo(0, gridsize * i);
    //                 ctx.lineTo(canvas.width, gridsize * i);
    //               }
    //               for(let j=0; j<n; j++) {
    //                 ctx.moveTo(gridsize * j, 0);
    //                 ctx.lineTo(gridsize * j, canvas.height);
    //               }
    //               ctx.strokeStyle = "black";
    //               ctx.stroke();


    //               return canvas;
    //           },
    //           projection: this.getProjection()
    //         })
    //       });
    //       this.map.addLayer(this.idwLayer)
    //     })
    //     .catch((error) => {
    //       console.log(error);
    //     });
    // },
    krigingLayerUpdate() {
      if(this.checked1) {
        //向map添加图层
        this.map.addLayer(this.krigingLayer);
      } else {
        this.map.removeLayer(this.krigingLayer);
      }
    },
    idwLayerUpdate() {
      if(this.checked2) {
        //向map添加图层
        this.map.addLayer(this.idwLayer);
      } else {
        this.map.removeLayer(this.idwLayer);
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
<style>
#openlayers_container {
  height: 100%;
}
.sidepanel {
  width: 100%;
  height: 10%;
  position: absolute;
}
#himarkmap {
  width: 100%;
  height: 70%;
  position: absolute;
  top: 10%;
}
</style>

