function timeSeriesChart() {
    var margin = { top: 20, right: 20, bottom: 20, left: 20 },
        width = null,
        height = null,
        xValue = function (d) { return d.date; },
        yValue = function (d) { return d.value; },
        xScale = d3.scaleTime(),
        yScale = d3.scaleLinear(),
        xAxis = d3.axisBottom(xScale).tickSize(6, 0),
        area = d3.area().x(X).y1(Y),
        line = d3.line().x(X).y(Y);

    function chart(selection) {
        selection.each(function (dataSets) {

            if (width === null) {
                width = window.innerWidth - 140;
            }
            if (height === null) {
                height = 250;
            }

            // Convert data to standard representation greedily;
            // this is needed for nondeterministic accessors.
            var standardData = dataSets.map(function (data) {
                return data.map(function (d, i) {
                    return [d.date, d.value];
                });
            });

            // Update the x-scale.
            xScale
                .domain(d3.extent(dataSets[0], function (d) { return d.date; }))
                .range([0, width - margin.left - margin.right]);

            // Update the y-scale.
            yScale
                .domain([0, d3.max(dataSets[0], function (d) { return d.value; })])
                .range([height - margin.top - margin.bottom, 0]);

            var svg = d3.select('svg > g'),
                create = svg.empty(),
                trans = 1000;
            if (create) {
                var svg = d3.select(this)
                    .append('svg')
                    .attr('viewBox', '0 0 ' + width + ' ' + (height + margin.bottom))
                    .attr('preserveAspectRatio', 'xMidYMid meet')
                    .attr('width', width)
                    .attr('height', height)
                    .append('g')
                    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
                svg.append('g').attr('class', 'grid');
            } else {
                d3.select(this)
                    .attr('viewBox', '0 0 ' + width + ' ' + height)
                    .attr('width', width)
                    .attr('height', height);
            }

            standardData.forEach((data, index) => {
                var ch = svg.select('g.line-chart-' + index);
                if (ch.empty()) {
                    var linechart = svg.append('g').attr('class', 'line-chart-' + index);
                    linechart.append('path')
                        .datum(data)
                        .attr('fill', 'none')
                        .style('stroke', 'black')
                        .style('stroke-width', '2px')
                        .attr('class', 'line')
                        .attr('d', line);
                } else {
                    ch.select('path').transition(trans).attr('d', line(data));
                }
            });
            svg.append('g')
                .attr('class', 'x-axis')
                .attr('transform', "translate(0," + yScale.range()[0] + ")")
                .call(xAxis);

            addLegend(svg, dataSets);
            addGrid(svg, dataSets, yScale);
        });
    }

    function addLegend(svg, dataSets) {
        svg.selectAll('g.legend').remove();
        var legendGroup = svg.append('g')
            .attr('class', 'legend'),
            labels = [],
            yOffset = height,
            xOffset = -10;

        for (var dix = 0; dix < dataSets.length; dix += 1) {
            var data = dataSets[dix];
            if (dataSets.length === 0) {
                continue;
            }
            var header = data[0].header || (dix + 1).toString(),
                fieldName = dataSets.length === 1 ? data[0].fieldName : header;
            var padding = 5,
                rectWidth = 10,
                recordValueWidth = 100,
                labelWidth = fieldName.length * 10,
                legendWidth = rectWidth + labelWidth + recordValueWidth;
            var seriesLegend = legendGroup.append('g')
                .style('font-size', '14px')
                .attr('class', 'series-legend')
                .attr('series-index', dix);
            var textFill = 'black',
                rectFill = 'black';
            seriesLegend.append('rect')
                .attr('x', xOffset)
                .attr('y', yOffset - 5)
                .attr('width', 10)
                .attr('height', '2')
                .attr('fill', rectFill);
            var label = seriesLegend.append('text')
                .style('font-weight', '400')
                .attr('class', 'legend-label dataset-' + dix)
                .attr('x', xOffset + rectWidth + padding)
                .attr('y', yOffset)
                .attr('fill', textFill)
                .text(fieldName + ': ');
            xOffset += legendWidth;
        }
    }

    // add grid to chart
    function addGrid(svg, dataSets, yScale) {
        var tickCount = 4;
        if (!dataSets.length) {
            tickCount = 2;
        }
        var fontSize = 11;
        const gridLines = d3.axisLeft(yScale).ticks(tickCount).tickSize(-(width - margin.left - margin.right));

        svg.selectAll('g.grid > *').remove();
        svg.select('g.grid')
            .call(gridLines)
            .call(g => g.selectAll('.tick line')
                .attr('stroke-opacity', 0.5)
                .attr('stroke-dasharray', '2,2'))
            .call(g => g.selectAll('.tick text')
                .style('font-size', fontSize + 'px')
                .attr('x', -fontSize * 2))
            .call(g => g.select('.domain')
                .remove());
    }
    
    // The x-accessor for the path generator; xScale ∘ xValue.
    function X(d) {
        return xScale(d[0]);
    }

    // The x-accessor for the path generator; yScale ∘ yValue.
    function Y(d) {
        return yScale(d[1]);
    }

    chart.margin = function (_) {
        if (!arguments.length) return margin;
        margin = _;
        return chart;
    };

    chart.width = function (_) {
        if (!arguments.lengtsh) return width;
        width = _;
        return chart;
    };

    chart.height = function (_) {
        if (!arguments.length) return height;
        height = _;
        return chart;
    };

    chart.x = function (_) {
        if (!arguments.length) return xValue;
        xValue = _;
        return chart;
    };

    chart.y = function (_) {
        if (!arguments.length) return yValue;
        yValue = _;
        return chart;
    };

    return chart;
}