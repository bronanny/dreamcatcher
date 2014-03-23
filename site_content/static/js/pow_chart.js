
function powchart() {

  var margin = {top: 20, right: 20, bottom: 20, left: 20},
      width = 1024,
      height = 320,
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

  function chart(svgchart, data) {

    if (data.length === 0) {
      data = [[0, 0]];
    }

//    var blip_width = width / data.length;
    var w = width - margin.left - margin.right - 2;

    xScale
      .domain([data[0][0], data[data.length - 1][0]])
      .range([margin.left, w]);

    yScale
      .domain([0, 100])
      //.domain([0, d3.max(data, yValue)])
      .range([height - margin.top - margin.bottom, margin.top]);

    yAxis.tickSize(-(w - margin.left));
      
    svgchart.attr("width", width).attr("height", height);

    var bar = svgchart.selectAll("rect")
      .data(data);
    bar.exit().remove();
    bar.enter().append("rect")
      .attr("height", 2)
      .attr("width", 2);
    bar
      .attr("title", function(d) { return "" + d[1]; })
      .attr("x", function(d) { return xScale(d[0]); })
      .attr("y", function(d) { return yScale(d[1]); });

    svgchart.selectAll("g").remove();

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

  return chart;
}
