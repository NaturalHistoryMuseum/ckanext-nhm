ckan.module('stats_graphs', function ($) {
  return {
    initialize: function () {
      const graphBox = $('#graph-box');
      const encodedData = this.options.data;
      const byteChars = atob(encodedData);
      let byteNums = new Array(byteChars.length);
      for (let i = 0; i < byteChars.length; i++) {
        byteNums[i] = byteChars.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNums);
      const inflatedData = pako.inflate(byteArray, { to: 'string' });
      let data = JSON.parse(inflatedData).map((d) => [new Date(d[0]), d[1]]);
      let dateGrouping = 'day';
      if (data.length > 100) {
        data = d3.rollups(
          data,
          (v) => v.reduce((a, b) => Math.max(a, b[1]), 0),
          (d) => d3.timeMonth.round(d[0]),
        );
        dateGrouping = 'month';
      }

      $(window).on('resize', drawGraph);
      drawGraph();

      function drawGraph() {
        graphBox.empty();
        const width = graphBox.width();
        const height = graphBox.height() > 0 ? graphBox.height() : 500;
        const marginH = Math.round(height * 0.1);
        const marginV = Math.round(height * 0.04);

        let svg = d3
          .select('#graph-box')
          .append('svg')
          .attr('width', width)
          .attr('height', height)
          .attr('viewBox', [0, 0, width + 50, height + 50]);
        let x = d3.map(data, (d) => d[0]);
        let y = d3.map(data, (d) => d[1]);
        let xScale = d3.scaleUtc(d3.extent(x), [marginH, width - marginH]);
        let yScale = d3.scaleLinear(
          [0, d3.max(y)],
          [height - marginV, marginV],
        );
        let xAxis = d3
          .axisBottom(xScale)
          .ticks(d3.timeYear.every(1))
          .tickSizeOuter(0);
        let yAxis = d3.axisLeft(yScale).ticks(10);

        let line = d3
          .line()
          .curve(d3.curveCatmullRom)
          .x((i) => xScale(x[i]))
          .y((i) => yScale(y[i]));

        svg
          .append('g')
          .attr('transform', `translate(0,${height - marginV})`)
          .call(xAxis);

        svg
          .append('g')
          .attr('transform', `translate(${marginH},0)`)
          .call(yAxis)
          .call((g) =>
            g
              .selectAll('.tick line')
              .clone()
              .attr('x2', width - marginH * 2)
              .attr('stroke-opacity', 0.1),
          );

        svg
          .append('path')
          .attr('fill', 'none')
          .attr('stroke', '#188100')
          .attr('stroke-opacity', 0.5)
          .attr('stroke-width', 4)
          .attr('d', line(d3.range(x.length)));

        svg
          .append('g')
          .attr('fill', '#0E4609')
          .selectAll('circle')
          .data(d3.range(x.length))
          .join('circle')
          .attr('cx', (i) => xScale(x[i]))
          .attr('cy', (i) => yScale(y[i]))
          .attr('r', 2);

        let tooltip = svg.append('g').style('pointer-events', 'none');
        let box = tooltip
          .append('rect')
          .attr('fill', 'white')
          .attr('stroke', 'black')
          .attr('stroke-opacity', 0.2);
        let vLine = svg
          .append('line')
          .attr('stroke', 'black')
          .attr('stroke-opacity', 0.2);
        let xText = tooltip.append('text');
        let yText = tooltip.append('text');

        svg.on('pointerenter pointermove', (event) => {
          let pointerXY = d3.pointer(event);
          const pointIx = d3.bisectCenter(x, xScale.invert(pointerXY[0]));
          const pointX = x[pointIx];
          const pointY = y[pointIx];
          tooltip.style('display', null);
          vLine.style('display', null);
          tooltip.attr(
            'transform',
            `translate(${xScale(pointX) + 5},${yScale(pointY) + 50})`,
          );

          vLine
            .attr('x1', xScale(pointX))
            .attr('x2', xScale(pointX))
            .attr('y1', height - marginV)
            .attr('y2', yScale(pointY));

          xText
            .attr('y', '-1em')
            .attr('x', 5)
            .text(() => {
              let day = pointX.getDate().toString().padStart(2, '0');
              let month = (pointX.getMonth() + 1).toString().padStart(2, '0');
              let year = pointX.getFullYear();
              let dateString = `${year}-${month}`;
              return dateGrouping === 'day'
                ? `${dateString}-${day}`
                : dateString;
            });

          yText.attr('x', 5).text(() => pointY);

          let text = tooltip.selectAll('text');

          const {
            x: boxX,
            y: boxY,
            width: boxW,
            height: boxH,
          } = text.node().getBBox();
          box
            .attr('width', boxW + 10)
            .attr('height', boxH * 2 + 10)
            .attr('y', boxY - 5);
        });

        svg.on('pointerleave', () => {
          tooltip.style('display', 'none');
          vLine.style('display', 'none');
        });
      }
    },
  };
});
