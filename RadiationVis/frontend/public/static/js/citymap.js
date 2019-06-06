const path = require('path')
import * as d3 from 'd3';

class CityMap {

  constructor(imageSrc, longitudeRange, latitudeRange) {
    this.imageSrc = imageSrc || '/static/images/StHimarkMapBlank.png';
    this.longitudeRange = longitudeRange || [-120.0, -119.711751];
    this.latitudeRange = latitudeRange || [0.238585, 0.0];
    this.width = null;
    this.height = null;
    this.timeRange = null;
    this.data = null;
    this.girdsize = null;
  }

  setMapSize(width, height) {
    this.width = width;
    this.height = height;
  }

  loadData(data) {
    this.data = data;
  }

  setTimeRange(timeRange) {
    this.timeRange = timeRange;
  }

  setGridSize(girdsize) {
    this.girdsize = girdsize;
  }

  assignGrid() {
    n = Math.ceil(Math.abs(this.width / (this.longitudeRange[1] - this.longitudeRange[0])))
    m = Math.ceil(Math.abs(this.height / (this.latitudeRange[1] - this.latitudeRange[0])))
  }

  mappingToCoordinate(latitude, longtitude) {
    /**
     * 将经纬度映射成坐标
     */
    let xScale = d3.scaleLinear().domain(this.longitudeRange).range([0, this.width]);
    let yScale = d3.scaleLinear().domain(this.latitudeRange).range([0, this.height]);
    return [xScale(longtitude), yScale(latitude)];
  }

  mappingToPostion(x, y) {
    /**
     * 将位置映射成经纬度
     * Returns [纬度， 经度]
     */
    let xScale = d3.scaleLinear().domain(this.longitudeRange).range([0, this.width]);
    let yScale = d3.scaleLinear().domain(this.latitudeRange).range([0, this.height]);
    return [yScale.invert(y), xScale.invert(x)];
  }
}

export default CityMap
