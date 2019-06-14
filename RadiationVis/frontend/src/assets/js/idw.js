//idw算法
//输入[{x:0,y:0,v:0},{x:0,y:0,v:0},{x:0,y:0,v:0}]
export default function idw(griddata) {
    /**
     * griddata 原始网格数据，每个网格都有一个value，有的value有值，有的为null，idw将为null的网格进行插值
     */
    let copy = JSON.parse(JSON.stringify(griddata)) // 深拷贝
    let points = copy.filter(d => d.value != null); // 有值的点
    let nullPoints = copy.filter(d => d.value == null); //null的点

    if(points.lenght < 3) return nullPoints;
    var m0=points.length;
    var m1=nullPoints.length;

    //console.info(points);

    //距离列表
    var r=[];

    for(var i=0;i<m1;i++){
        for(var j=0;j<m0;j++){
            var tmpDis = Math.sqrt(Math.pow(nullPoints[i].lat - points[j].lat, 2) + Math.pow(nullPoints[i].lng - points[j].lng, 2));
            r.push(tmpDis);
        }
    }

    //插值函数

    for (var i = 0; i < m1; i++)
    {
        //查找重复
        var ifFind = false;
        for (var j = m0 * i; j < m0 * i + m0; j++)
        {
            if (Math.abs(r[j]) < 0.0001)
            {
                nullPoints[i].value = points[j - m0 * i].value;
                ifFind = true;
                break;
            }
        }

        if (ifFind) continue;

        var numerator = 0;
        var denominator = 0;

        for (var j = m0 * i; j < m0 * i + m0; j++)
        {
            numerator += points[j - m0 * i].value / (r[j] * r[j]);
            denominator += 1 / (r[j] * r[j]);
        }

        nullPoints[i].value = numerator / denominator;
    }
    return points.concat(nullPoints);

}