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
        line = d3.line().x(X).y(Y),
        dataSets = [];

    function chart(selection) {
        selection.each(function (datum) {
            dataSets = datum;

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

            addLegend(svg);
            addGrid(svg, yScale);
            if (create && dataSets.length > 0) {
                toolTip(svg);
            }
        });
    }

    function addLegend(svg) {
        svg.selectAll('g.legend').remove();
        var legendGroup = svg.append('g').attr('class', 'legend g-chart'),
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
            if (label.node()) {
                const bBox = (label.node()).getBBox();
                seriesLegend.append('text')
                    .style('font-weight', '600')
                    .attr('class', 'legend-value dataset-' + dix)
                    .attr('x', bBox.x + bBox.width + padding)
                    .attr('y', yOffset)
                    .attr('fill', textFill);
            }
            xOffset += legendWidth;
            // wrap to next line if legend does not fit
            if ((xOffset + legendWidth) > width) {
                xOffset = -20;
                yOffset += 25;
            }
        }
    }

    // add grid to chart
    function addGrid(svg, yScale) {
        var tickCount = 4;
        if (!dataSets.length) {
            tickCount = 2;
        }
        var fontSize = 11;
        var gridLines = d3.axisLeft(yScale).ticks(tickCount).tickSize(-(width - margin.left - margin.right));

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

    function dropShadow(svg) {
        var defs = svg.append('defs');

        // black drop shadow
        var filter = defs.append('filter')
            .attr('id', 'drop-shadow');

        filter.append('feGaussianBlur')
            .attr('in', 'SourceAlpha')
            .attr('stdDeviation', 1)
            .attr('result', 'blur');
        filter.append('feOffset')
            .attr('in', 'blur')
            .attr('dx', 1)
            .attr('dy', 1)
            .attr('result', 'offsetBlur');
        filter.append('feFlood')
            .attr('in', 'offsetBlur')
            .attr('flood-color', '#2f3d4a')
            .attr('flood-opacity', '0.5')
            .attr('result', 'offsetColor');
        filter.append('feComposite')
            .attr('in', 'offsetColor')
            .attr('in2', 'offsetBlur')
            .attr('operator', 'in')
            .attr('result', 'offsetBlur');

        var feMerge = filter.append('feMerge');

        feMerge.append('feMergeNode')
            .attr('in', 'offsetBlur');
        feMerge.append('feMergeNode')
            .attr('in', 'SourceGraphic');
    }

    function toolTip(svg) {
        dropShadow(svg);
        var focus = svg.append('g')
            .attr('transform', 'translate(' + -width + ',0)')
            .attr('class', 'focus g-tooltip')
            .style('display', 'none');

        focus.append('line')
            .attr('class', 'x-hover-line hover-line')
            .attr('stroke', '#eef5f9')
            .attr('stroke-width', '2px')
            .attr('y1', 0)
            .attr('y2', height);

        var toolTipInfo = focus.append('g').attr('class', 'tooltip');
        // add date label
        toolTipInfo.append('text')
            .style('font-size', '12px')
            .attr('class', 'hover-text dataset-date')
            .attr('x', 10)
            .attr('y', 40)
            .attr('font-family', 'Poppins')
            .attr('fill', 'black');

        // overlay to capture mouse move events on chart
        // it doesn't cover the full `chartHeight` to ensure that click events on legends can fire
        svg.append('rect')
            .attr('transform', 'translate(0, 0)')
            .attr('class', 'overlay')
            .attr('width', (width - margin.left - margin.right))
            .attr('height', height - margin.bottom)
            .attr('fill', 'none')
            .attr('pointer-events', 'all')
            .on("mousemove", mousemove)
            .on("mouseover", mouseover)
            .on("mouseout", mouseout);
    }

    function mouseover() {
        d3.select('g.focus.g-toolip').style('display', null);
    }

    function mouseout(d, i) {
        d3.select('g.focus.g-tooltip').style('display', 'none');
    }

    function mousemove(event) {
        var target = event.target,
            bounds = target.getBoundingClientRect(),
            xcoord = event.clientX;

        if (dataSets.length === 0) {
            return;
        }
        var bisectDate = d3.bisector(function (d) { return d.date; }).right;

        // add offset for scaled svg
        function elementScale() {
            return bounds.left - event.clientX/15;
        }

        var markerHeight = height - margin.bottom,
            newX = xcoord - elementScale(),
            xdate = xScale.invert(xcoord),
            tooltip = d3.select('g.focus.g-tooltip'),
            legend = d3.select('g.legend.g-chart');

        // update marker label for each dataset
        for (var dix = 0; dix < dataSets.length; dix += 1) {
            var rix = bisectDate(dataSets[dix], xdate) - 1;
            var record = dataSets[dix][rix];
            if (record === undefined) {
                continue;
            }

            tooltip
                .attr('transform', 'translate(' + newX + ',' + 0 + ')')
                .style('display', null)
                .select('.x-hover-line').attr('y2', markerHeight);

            var legendText = (legend.select('text.legend-label.dataset-' + dix)).node();
            if (legendText) {
                var bBox = legendText.getBBox();
                legend.select('text.legend-value.dataset-' + dix)
                    .text(function () {
                        return record.value;
                    })
                    .attr('x', bBox.x + bBox.width + 5);
            }
        }

        // update date label
        tooltip
            .select('text.dataset-date')
            .text(function () {
                return d3.timeFormat('%d %B, %H:%M')(xdate);
            });

        var boxWidth = (tooltip.select('text.dataset-date').node()).getBBox().width;

        if (newX + boxWidth > (width - margin.left - margin.right)) {
            var boxX = -boxWidth - 30;
            tooltip.select('g.tooltip')
                .attr('transform', 'translate(' + boxX + ', 0)');
        } else {
            tooltip.select('g.tooltip')
                .attr('transform', 'translate(0, 0)');
        }
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