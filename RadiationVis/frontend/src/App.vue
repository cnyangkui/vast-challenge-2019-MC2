<template>
  <div id="app">
    <el-row :gutter=1>
      <el-col :span="4" class="left">
        <div class="grid-content">
            <div class="control-header">
              <label>Data Center</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group first last">
                <div class="input-ele">
                  <input type="checkbox" value="radiation" name="overview-type" v-model="datatype"><label>Radiation</label>
                </div>
                <div class="input-ele">
                  <input type="checkbox" value="uncertainty" name="overview-type" v-model="datatype"><label>Uncertainty</label>
                  </div>
              </div>
            </div>
            <div class="control-header">
              <label>Overall Radiation Trend View Settings</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group first">
                <div class="input-ele"><input type="checkbox" value="static"  v-model="timeSeriesCheckedState"><label>Static Sensors (SSs)</label></div>
                <div class="input-ele"><input type="checkbox" value="mobile" v-model="timeSeriesCheckedState"><label>Mobile Sensors (MSs)</label></div>
              </div>
              <div class="input-ele-group last">
                <div class="input-ele"><input type="radio" value="global" name="timeSeriesState" v-model="timeSeriesControl.state"><label>By 1 hour</label></div>
                <div class="input-ele"><input type="radio" value="local" name="timeSeriesState" v-model="timeSeriesControl.state" :disabled="timeSeriesControl.localDisabled"><label>By 1 minute</label></div>
              </div>
            </div>
            <div class="control-header">
              <label>Sensor Clustering Treemap View Settings</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group first">
                <div class="input-ele"><input type="checkbox" value="static" v-model="treemapCheckedState"><label>Static Sensors (SSs)</label></div>
                <div class="input-ele"><input type="checkbox" value="mobile" v-model="treemapCheckedState"><label>Mobile Sensors (MSs)</label></div>
              </div>
              <div class="input-ele-group last">
                <div class="input-ele"><input class="button" type="button" value="Back to root" @click="getTreemap1();"></div>
              </div>
            </div>
            <div class="control-header">
              <label>Individual Sensor Temporal View Settings</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group first last">
                <div class="input-ele"><input type="radio" value="line" name="sidTrendChartStyle" v-model="sidTrendChartStyle"><label>Line</label></div>
                <div class="input-ele"><input type="radio" value="point" name="sidTrendChartStyle" v-model="sidTrendChartStyle"><label>Point</label></div>
              </div>
            </div>
            <div class="control-header">
              <label>Gis View Settings</label>
            </div>
              <div class="control-content">
                <div class="input-ele-group first">
                  <label>Map layers:</label>
                  <select class="select" style="margin-left: 5px;" v-model="mapControl.image" @change="changeMapImage">
                    <option v-for="(item, index) in mapImages" :key="index" :value="item">{{item}}</option>
                  </select>
                </div>
                <div class="input-ele-group">
                  <div class="input-ele"><input type="checkbox" v-model="mapControl.icon_s_check"><label>Static Sensors (SSs)</label>
                  <img :src="require('./assets/img/static.png')" alt="" width="20px;"></div>
                  <div class="input-ele"><input type="checkbox" v-model="mapControl.icon_m_check"><label>Mobile Sensors (MSs)</label>
                  <img :src="require('./assets/img/mobile.png')" alt="" width="20px;"></div>
                </div>
                <div class="input-ele-group last">
                  <div class="input-ele"><input type="checkbox" v-model="mapControl.si_idw_check"><label>Static Interpolation</label></div>
                  <div class="input-ele"><input type="checkbox" v-model="mapControl.mi_idw_check"><label>Mobile Interpolation</label></div>
                </div>
              </div>
            <div class="control-header">
              <label>Animation Settings</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group first">
                <div class="input-ele"><input type="radio" value="hour" v-model="playerSpeed"><label>By 1 hour</label></div>
                <div class="input-ele"><input type="radio" value="minute" v-model="playerSpeed" :disabled="timeSeriesControl.localDisabled"><label>By 1 minute</label></div>
              </div>
              <div class="input-ele-group last">
                <div class="input-ele"><input class="button" type="button" :value="playerState==true?'Pause':'Play'" @click="animationPlayer();"></div>
             </div>
            </div>
            <div class="control-header">
              <label>Uncertainty Settings</label>
            </div>
              <div class="control-content">
                <div class="input-ele-group first"><label class="bold">Uncertainty index system</label></div>
                <!-- <ul>
                  <li>U1: Inconsistency </li>
                  <li>U2: Credibility</li>
                  <li>U3: Precision</li>
                  <li>U4: Data completeness</li>
                </ul> -->
                <table>
                  <tr>
                    <td width="220px">U1: Inconsistency</td>
                    <td width="300px">weight: <input type="text" style="width:30px; text-align:center" value="1"></td>
                  </tr>
                  <tr>
                    <td>U2: Credibility</td>
                    <td>weight: <input type="text" style="width:30px; text-align:center" value="1"></td>
                  </tr>
                  <tr>
                    <td>U3: Precision</td>
                    <td>weight: <input type="text" style="width:30px; text-align:center" value="1"></td>
                  </tr>
                  <tr>
                    <td>U4: Data completeness</td>
                    <td>weight: <input type="text" style="width:30px; text-align:center" value="1"></td>
                  </tr>
                </table>
              <div class="control-content">
                <div class="input-ele-group first"><label class="bold">Uncertainty levels</label></div>
                <ul>
                  <li>Level 1: <img :src="require('./assets/img/star.png')" alt="" width="20px;">low</li>
                  <li>Level 2: 
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    guarded
                  </li>
                  <li>Level 3: 
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    elevated
                  </li>
                  <li>Level 4: 
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    high
                  </li>
                  <li>Level 5: 
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    severe
                  </li>
                </ul>
              </div>
          </div>
        </div>
      </el-col>
      <el-col :span="20" class="right">
        <el-row class="right_top">
          <el-col :span="24">
            <div class="grid-content" v-if="datatype.length == 2">
              <time-series-chart v-show="timeSeriesControl.state=='global'" :cid="`time_series_chart_container`" :checkedItem="timeSeriesCheckedState"></time-series-chart>
              <trend-chart v-show="timeSeriesControl.state=='local'" :cid="`trend_local_chart_container`" :originData="trendChart" :checkedItem="timeSeriesCheckedState"></trend-chart>
            </div>
            <div class="grid-content" v-if="datatype.length == 1 && datatype[0]=='radiation'">
              <radiation-time-series-chart v-show="timeSeriesControl.state=='global'" :cid="`radiation_time_series_chart_container`" :checkedItem="timeSeriesCheckedState"></radiation-time-series-chart>
              <radiation-trend-chart v-show="timeSeriesControl.state=='local'" :cid="`radiation_trend_local_chart_container`" :originData="trendChart" :checkedItem="timeSeriesCheckedState"></radiation-trend-chart>
            </div>
            <div class="grid-content" v-if="datatype.length == 1 && datatype[0] == 'uncertainty'">
              <uncertainty-time-series-chart v-show="timeSeriesControl.state=='global'" :cid="`uncertainty_time_series_chart_container`" :checkedItem="timeSeriesCheckedState"></uncertainty-time-series-chart>
              <uncertainty-trend-chart v-show="timeSeriesControl.state=='local'" :cid="`uncertainty_trend_local_chart_container`" :originData="trendChart" :checkedItem="timeSeriesCheckedState"></uncertainty-trend-chart>
            </div>
          </el-col>
        </el-row>
        <el-row class="right_bottom">
          <el-col :span="9" class="bottom_left">
            <div class="grid-content bottom_left_top" v-if="datatype.length == 2">
              <treemap v-show="treemapState=='treemap1'" :cid="`treemap-container`" :originData="treemap1"></treemap>
              <treemap v-show="treemapState=='treemap2'" :cid="`treemap-container2`" :originData="treemap2"></treemap>
            </div>
            <div class="grid-content bottom_left_top" v-if="datatype.length == 1 && datatype[0]=='radiation'">
              <radiation-treemap v-show="treemapState=='treemap1'" :cid="`radiation-treemap-container`" :originData="treemap1"></radiation-treemap>
              <radiation-treemap v-show="treemapState=='treemap2'" :cid="`radiation-treemap-container2`" :originData="treemap2"></radiation-treemap>
            </div>
            <div class="grid-content bottom_left_top" v-if="datatype.length == 1 && datatype[0]=='uncertainty'">
              <uncertainty-treemap v-show="treemapState=='treemap1'" :cid="`uncertainty-treemap-container`" :originData="treemap1"></uncertainty-treemap>
              <uncertainty-treemap v-show="treemapState=='treemap2'" :cid="`uncertainty-treemap-container2`" :originData="treemap2"></uncertainty-treemap>
            </div>
            <div class="grid-content bottom_left_top" v-if="datatype.length == 0">
              
            </div>
            <div class="grid-content bottom_left_bottom" v-if="datatype.length == 2">
              <div v-for="(item, index) in sidTrendCharts" :key='index' class="innerdiv">
                <sid-trend-chart :cid="`trend_chart_container_${index}`" :originData="item" :componentStyle="sidTrendChartStyle"></sid-trend-chart>
              </div>
            </div>
            <div class="grid-content bottom_left_bottom" v-if="datatype.length == 1 && datatype[0]=='radiation'">
              <div v-for="(item, index) in sidTrendCharts" :key='index' class="innerdiv">
                <radiation-sid-trend-chart :cid="`radiation_trend_chart_container_${index}`" :originData="item" :componentStyle="sidTrendChartStyle"></radiation-sid-trend-chart>
              </div>
            </div>
            <div class="grid-content bottom_left_bottom" v-if="datatype.length == 1 && datatype[0]=='uncertainty'">
              <div v-for="(item, index) in sidTrendCharts" :key='index' class="innerdiv">
                <uncertainty-sid-trend-chart :cid="`uncertainty_trend_chart_container_${index}`" :originData="item" :componentStyle="sidTrendChartStyle"></uncertainty-sid-trend-chart>
              </div>
            </div>

          </el-col>
          <el-col :span="15" class="bottom_right">
            <div class="grid-content">
              <gis-view :mapControl="mapControl" :datatype="datatype"></gis-view>
            </div>
          </el-col>
        </el-row>
      </el-col>
    </el-row>

  </div>
</template>

<script>
import TimeSeriesChart from './components/TimeSeriesChart.vue'
import RadiationTimeSeriesChart from './components/RadiationTimeSeriesChart.vue'
import UncertaintyTimeSeriesChart from './components/UncertaintyTimeSeriesChart.vue'
import TrendChart from './components/TrendChart.vue'
import RadiationTrendChart from './components/RadiationTrendChart.vue'
import UncertaintyTrendChart from './components/UncertaintyTrendChart.vue'
import Treemap from './components/Treemap.vue'
import UncertaintyTreemap from './components/UncertaintyTreemap.vue'
import RadiationTreemap from './components/RadiationTreemap.vue'
import SidTrendChart from './components/SidTrendChart.vue'
import RadiationSidTrendChart from './components/RadiationSidTrendChart.vue'
import UncertaintySidTrendChart from './components/UncertaintySidTrendChart.vue'
import GisView from './components/GisView.vue'
import * as d3 from 'd3'
import axios from './assets/js/http'

export default {
  name: 'app',
  components: {
    GisView,
    TimeSeriesChart,
    RadiationTimeSeriesChart,
    UncertaintyTimeSeriesChart,
    TrendChart,
    RadiationTrendChart,
    UncertaintyTrendChart,
    Treemap,
    RadiationTreemap,
    UncertaintyTreemap,
    SidTrendChart,
    RadiationSidTrendChart,
    UncertaintySidTrendChart
  },
  data() {
    return {
      srScatterVisible: false,
      datatype: ["radiation", "uncertainty"],
      timeSeriesControl: {
        state: 'global',
        localDisabled: true,
      },
      timeSeriesCheckedState: ['static', 'mobile'],
      treemapCheckedState: ['static', 'mobile'],
      treemapState: 'treemap1',
      mapControl: {
        // r_si_kriging_check: false,
        // r_si_idw_check: false,
        // r_mi_idw_check: false,
        // r_s_check: false,
        
        // t_heatmap_check: false,
        // u_pie_check: false,
        // u_mi_check: false,
        // playState: false,

        icon_m_check: false,
        icon_s_check: false,
        si_idw_check: false,
        mi_idw_check: false,
        inconsistency_check: false,
        image: 'StHimarkMapRoad'
      },
      mapImages: ['StHimarkMapRoad', 'StHimarkMapBlank', 'StHimarkMapPoi', 'StHimarkMapHouse'],
      trendChart: null,
      sidTrendCharts: [],
      sidTrendChartStyle: null,
      treemap1: null,
      treemap2: null,
      timeRange: null,
      defaultTimeRange: {
        begintime: '2020-04-06 00:00:00',
        endtime: '2020-04-11 00:00:00'
      },
      playerState: false,
      playerSpeed: 'hour',
      currentPlayerTime: null,
      inteval: null,
    }
  },
  created: function () {
    this.$root.eventHub.$on('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$on('sensorSelected', this.sensorSelected);
      this.$root.eventHub.$on('defaultSensors', this.defaultSensors);
      this.$root.eventHub.$on('getTreemap2', this.getTreemap2);
   },
   // 最好在组件销毁前
   // 清除事件监听
   beforeDestroy: function () {
     this.$root.eventHub.$off('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$off('sensorSelected', this.sensorSelected);
      this.$root.eventHub.$off('defaultSensors', this.defaultSensors);
      this.$root.eventHub.$off('getTreemap2', this.getTreemap2);
   },
  mounted() {
    // this.layout();
    this.$nextTick(() => {
      this.getTreemapDataByTimeRange(this.defaultTimeRange);
      this.sidTrendChartStyle = this.datatype.length == 2? 'line':'point';
      this.currentPlayerTime = this.timeRange || this.defaultTimeRange.begintime;
    })
  },
  methods: {
    sensorSelected(params) {
      // 如果该传感器已经存在，则不添加
      if(this.sidTrendCharts.filter(d => d.category==params.category && d.sid==params.sid).length > 0) {
        return;
      }
      this.getSidTrendChartData(params);
    },
    defaultSensors(params) {
      // 如果该传感器已经存在，则不添加
      if(this.sidTrendCharts.filter(d => d.category==params.category && d.sid==params.sid).length > 0) {
        return;
      }
      this.getSidTrendChartData(params);
    },
    getSidTrendChartData(params) {
      let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      axios.post("/calTimeSeriesBySid/", params)
        .then((response) => {
          let data = response.data.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: -1.96 * d.standarderror + d.avg,
              avg: d.avg,
              upper95: 1.96 * d.standarderror + d.avg,
              std: d.std
            };
          });
          let sidtrendChart = {
            category: params.category,
            sid: params.sid,
            timeRange: {begintime: params.begintime, endtime: params.endtime},
            data: data
          }
          this.sidTrendCharts.push(sidtrendChart);
      })
    },
    getTrendChartDataByTimeRange(params) {
      let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      axios.post("/calTimeSeries/", params)
        .then((response) => {
          let data = response.data;
          var static_data = data.static.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: -1.96 * d.standarderror + d.avg,
              avg: d.avg,
              upper95: 1.96 * d.standarderror + d.avg,
              std: d.std
            };
          });
          var mobile_data = data.mobile.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: -1.96 * d.standarderror + d.avg,
              avg: d.avg,
              upper95: 1.96 * d.standarderror + d.avg,
              std:d.std
            };
          });
          this.trendChart = {
            timeRange: params,
            data: {staticData: static_data, mobileData: mobile_data}
          }
        })

    },
    getTreemapDataByTimeRange(params) {
      if(this.treemapCheckedState.length == 2) {
        axios.post("/calSensorClusters/", params).then(response => {
          this.treemap1 = {
            state: this.treemapState,
            data: response.data,
            timeRange: params,
            checkedState: this.treemapCheckedState,
            sensorType: 'both'
          }
        })
      }
      if(this.treemapCheckedState.length == 1 && this.treemapCheckedState[0] == 'static') {
        axios.post("/calStaticSensorClusters/", params).then(response => {
          this.treemap1 = {
            state: this.treemapState,
            data: response.data,
            timeRange: params,
            checkedState: this.treemapCheckedState,
            sensorType: 'static'
          }
        })

      }
      if(this.treemapCheckedState.length == 1 && this.treemapCheckedState[0] == 'mobile') {
        axios.post("/calMobileSensorClusters/", params).then(response => {
          this.treemap1 = {
            state: this.treemapState,
            data: response.data,
            timeRange: params,
            checkedState: this.treemapCheckedState,
            sensorType: 'mobile'
          }
        })

      }
      
    },
    getTreemap1() {
      this.treemapState = 'treemap1';
    },
    getTreemap2(params) {
      this.treemapState = 'treemap2';

      if(this.treemapCheckedState.length == 2) {
        this.treemap2 = {
          state: this.treemapState,
          data: params,
          timeRange: this.timeRange,
          checkedState: this.treemapCheckedState,
          sensorType: 'both'
        }
      }
      if(this.treemapCheckedState.length == 1 && this.treemapCheckedState[0] == 'static') {
        this.treemap2 = {
          state: this.treemapState,
          data: params,
          timeRange: this.timeRange,
          checkedState: this.treemapCheckedState,
          sensorType: 'static'
        }
      }
      if(this.treemapCheckedState.length == 1 && this.treemapCheckedState[0] == 'mobile') {
        this.treemap2 = {
          state: this.treemapState,
          data: params,
          timeRange: this.timeRange,
          checkedState: this.treemapCheckedState,
          sensorType: 'mobile'
        }

      }
    },
    timeRangeUpdated(params) {
      this.timeRange = params;
      this.sidTrendCharts = [];
      if(params) {
        this.timeSeriesControl.localDisabled = false;
        // this.timeSeriesControl.state = "local";
        this.trendChart = null;
        this.getTrendChartDataByTimeRange(params);
        this.treemap1 = null;
        this.treemap2 = null;
        this.treemapState = 'treemap1';
        this.getTreemapDataByTimeRange(params);
      }  else {
        this.timeSeriesControl.localDisabled = true;
      }
      if(!this.playerState) {
        let time = this.timeRange || this.defaultTimeRange;
        this.currentPlayerTime = time.begintime;
      }
    },
    changeMapImage() {
      console.log(this.mapControl)
    },
    animationPlayer() {
      this.playerState = !this.playerState;
      console.log(this.playerSpeed)
      if(this.playerState) {
        if(this.playerSpeed == 'hour') {
          this.inteval = setInterval(() => {
            let beginDate = new Date(this.currentPlayerTime);
            console.log(this.currentPlayerTime)
            let endDate = new Date(beginDate.getFullYear(), beginDate.getMonth(), beginDate.getDate(), beginDate.getHours()+1);
            let timeFormat = d3.timeFormat("%Y-%m-%d %H:%M:%S")
            let endtime = timeFormat(endDate);
            this.$root.eventHub.$emit("timeRangeUpdated", {begintime: this.currentPlayerTime, endtime: endtime});
            this.$root.eventHub.$emit("timeSliceUpdated", {begintime: this.currentPlayerTime, endtime: endtime});
            this.currentPlayerTime = endtime;
          }, 5000)
        } else {
          this.inteval = setInterval(() => {
            let beginDate = new Date(this.currentPlayerTime);
            console.log(this.currentPlayerTime)
            let endDate = new Date(beginDate.getFullYear(), beginDate.getMonth(), beginDate.getDate(), beginDate.getHours(), beginDate.getMinutes()+1);
            let timeFormat = d3.timeFormat("%Y-%m-%d %H:%M:%S")
            let endtime = timeFormat(endDate);
            this.$root.eventHub.$emit("minuteTimeRangeUpdated", {begintime: this.currentPlayerTime, endtime: endtime});
            this.$root.eventHub.$emit("timeSliceUpdated", {begintime: this.currentPlayerTime, endtime: endtime});
            this.currentPlayerTime = endtime;
          }, 5000)
        }
      } else {
        clearInterval(this.inteval);
      }
    }
  },
  watch: {
    treemapCheckedState(n, o) {
      this.treemapState = 'treemap1';
      this.getTreemapDataByTimeRange(this.timeRange);
    },
    datatype(n, o) {
      this.sidTrendChartStyle = this.datatype.length == 2? 'line':'point';
      this.treemap1 = null;
      this.treemap2 = null;
      this.treemapState = 'treemap1';
      this.getTreemapDataByTimeRange(this.timeRange);
    }
  }
}
</script>

<style>
/* #app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */

* {
  padding:0;
  margin:0;
  /* border: 0.1px solid red; */
}
html, body, #app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
.el-row {
  height: 100%;
}
.el-col {
  height: 100%;
}
.grid-content {
  border: 1px solid #ccc;
  height: 100%;
}
.left, .right {
  height: 100%;
}
.right_top {
  height: 16%;
}
.right_bottom {
  height: 84%;
}
.bottom_left, .bottom_right {
  height: 100%;
}
.bottom_left_top {
  height: 60%;
}
.bottom_left_bottom {
  height: 40%;
  overflow-y: auto;
  overflow-x: hidden;
}
.bottom_left_bottom .innerdiv {
  height: 50%;
}
.nav {
  height: 10%;
  font-size: 10px;
}
.main {
  height: 90%;
}
.control-header {
  background-color: #ccc;
}
.control-header label {
  margin-left: 1%;
  font-size: 18px;
  font-weight: bold;
}
.control-content img {
  width: 15px;
}
.control-content .input-ele-group, ul, table {
  width: 98%;
  margin-left: 1%;
}
.input-ele {
  width: 50%;
  display: inline-block;
}
.control-content label, input.button, select.select, ul, table {
  font-size: 15px;
}
.control-content .input-ele-group, .input-ele, label {
  height: 32px;
  line-height: 32px;
}
.control-content input.button, select.select {
  height: 30px;
  line-height: 30px;
}
.control-content label {
  vertical-align: middle;
}
.first {
  margin-top: 8px;
}
.last {
  margin-bottom: 8px;
}
</style>
