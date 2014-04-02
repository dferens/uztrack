var appendWeekdays = function(calendar) {
    var shiftByY = function(selection, dy) {
        return selection.attr('y', function() {
            return parseFloat(this.attributes.y.value) + dy;
        });
    };
    var cellSize = calendar.options.cellSize;
    var cellPadding = calendar.options.cellPadding;
    var gutter = calendar.options.domainGutter;
    var domainSvg = calendar.root.select('.graph');
    var domainWrappers = domainSvg.selectAll('svg.graph-domain');
    var domains = domainWrappers.selectAll('svg.graph-domain svg');

    var shiftValue = cellSize + gutter;
    shiftByY(domains.selectAll('g rect'), shiftValue);
    shiftByY(domains.selectAll('g text'), shiftValue);
    domainWrappers.attr('height', function() {return parseFloat(this.attributes.height.value) + shiftValue});
    _.each(['Mn', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'], function(weekday, i) {
        var block = domains.append('g');
        var blockX = (cellSize + cellPadding) * i;
        var textX = blockX + cellSize / 2;
        block.append('rect')
             .attr('x', blockX)
             .attr('fill', 'white')
             .attr('width', cellSize)
             .attr('height', cellSize);
        block.append('text')
             .attr('class', 'subdomain-text')
             .attr('text-anchor', 'middle')
             .attr('dominant-baseline', 'central')
             .attr('x', textX)
             .attr('y', cellSize / 2)
             .text(weekday);
    });

    window.graph = domainSvg;
    window.calendar = calendar;
}


$(function() {
    var id = window.location.pathname
                           .split('/track/')[1]
                           .slice(0, -1);
    var calendar = new CalHeatMap();
    calendar.init({
        cellSize: 23,
        data: historiesCalendarData,
        displayLegend: false,
        domain: 'month',
        domainLabelFormat: '%b %Y',
        domainGutter: 5,
        highlight: ['now'],
        label: {
            position: 'top'
        },
        legendColors: {
            min: 'white',
            max: 'green',
            empty: '#DFDFDF',
        },
        subDomain: 'x_day',
        subDomainTextFormat: '%d',
        range: 4,
    });
    appendWeekdays(calendar);
});
