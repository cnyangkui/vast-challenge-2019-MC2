<template>
  <div id="openlayers_container">
    <div id="himarkmap"></div>
  </div>
</template>
<script>
import CityMap from "../assets/js/citymap";
import axios from '../assets/js/http'
import * as d3 from 'd3'
import 'ol/ol.css';
// import ol from 'ol'
import {Map, View, Feature} from 'ol';
// import {Image as ImageLayer, Vector as VectorLayer} from 'ol/layer';
import Image from 'ol/layer/Image'
import VectorLayer from 'ol/layer/Vector'
// import {ImageStatic, Vector as VectorSource} from 'ol/source';
import ImageStatic from 'ol/source/ImageStatic'
import VectorSource from 'ol/source/Vector'
import {getCenter} from 'ol/extent';
import Projection from 'ol/proj/Projection';
import Point from 'ol/geom/Point'
import {Style, Circle, Fill} from 'ol/style'
import Select from 'ol/interaction/Select'

export default {
  name: 'Openlayers',
  data() {
    return {
      himarkmap: new CityMap(),
      imageExtent: [-120.0, 0, -119.711751, 0.238585], //[left, bottom, right, top]
      map: null, 
      ssLayer: null, //静态传感器层
      
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.loadMap();
    })
  },
  methods: {
    loadMap() {
      this.selfAdaptionSize();
      this.initMap();
      this.addSSLayer(); //添加静态传感器
    },
    selfAdaptionSize() {
      let width = document.querySelector("#openlayers_container").clientWidth;
      console.log(width)
      // let html = <img ref="geomap" :src="imgsrc">
      let img = document.createElement("img");
      img.src = require('../assets/img/StHimarkMapBlank.png');
      // img.width = width;
      // console.log(img.width, img.height);
      document.querySelector("#himarkmap").style.height = width * img.height / img.width  + "px";

    },
    initMap() {
      this.map = new Map({
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
          projection: new Projection({
              // code: 'himark-image',
              unites: 'pixels',
              extent: this.imageExtent
          }),
          center: getCenter(this.imageExtent),
          zoom: 1.5,
          minZoom: 1.5,
          maxZoom: 5,
        })
      });
    },
    addSSLayer() {
      let vectorSource = new VectorSource();
      this.ssLayer = new VectorLayer({
        source: vectorSource,
      });
      this.map.addLayer(this.ssLayer);

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
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
#openlayer_container {
  position: relative;
  height: 100%;
}

</style>

