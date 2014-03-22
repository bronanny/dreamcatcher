
function powchart() {

  var margin = {top: 20, right: 20, bottom: 20, left: 20},
      width = 1024,
      height = 320,
      xValue = function(d) { return d[0]; },
      yValue = function(d) { return d[1]; },
      xScale = d3.scale.linear(),
      yScale = d3.scale.linear(),
      xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .tickSize(6, 0)
        .tickSubdivide(true)
        .tickFormat(function(tick){
          return moment.unix(tick).calendar();
        }),
      yAxis = d3.svg.axis()
        .scale(yScale)
        .ticks(4)
        .orient("right");

  function chart(selection) {
    selection.each(function(data, i) {

      var blip_width = width / data.length;
      var w = width - margin.left - margin.right - blip_width;

      xScale
        .domain([data[0][0], data[data.length - 1][0]])
        .range([margin.left, w]);

      yScale
        .domain([0, 100])
        //.domain([0, d3.max(data, yValue)])
        .range([height - margin.top - margin.bottom, margin.top]);

      yAxis.tickSize(-(w - margin.left));
        
      var svgchart = d3.select(this).selectAll("svg")
          .attr("width", width)
          .attr("height", height);

      var bar = svgchart.selectAll("rect")
            .data(data)
//            .data(data.archives[i].points)
          .enter().append("rect")
            .attr("title", function(d) { return "" + d[1]; })
            .attr("x", function(d) { return xScale(d[0]); })
            .attr("y", function(d) { return yScale(d[1]); })
            .attr("width", blip_width)
            .attr("height", 2);

      // Add the y-axis.
      svgchart.append("g")
          .attr("class", "y axis")
          .attr("transform", "translate(" + (width - margin.right- margin.left) + ",0)")
          .call(yAxis);

      // Add the x-axis.
      svgchart.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + (height - margin.top - margin.bottom) + ")")
          .call(xAxis)
        .selectAll("text")
          .attr("transform", "rotate(12)")
          .style("text-anchor", "start");

    });

  }

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin = _;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.x = function(_) {
    if (!arguments.length) return xValue;
    xValue = _;
    return chart;
  };

  chart.y = function(_) {
    if (!arguments.length) return yValue;
    yValue = _;
    return chart;
  };

  return chart;
}
