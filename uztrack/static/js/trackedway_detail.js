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
        highlight: ['now'],
        subDomain: 'x_day',
        subDomainTextFormat: '%d',
        range: 4,
    });
});
