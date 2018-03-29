// Let's get the embed token by calling an Azure Function

// TODO: Add web.config and force HTTPS

// You can use the DisplayName as well instead of Id
let streamingDashboard = 'https://aa-funcbi.azurewebsites.net/api/dash-embed-token/dashboard/c5558acb-984a-4ed1-b37a-d9808feea1cb';
let theReport = 'https://aa-funcbi.azurewebsites.net/api/report-embed-token/report/9823b019-8db2-4760-90da-4e4cdffb1a9d';

$.ajax({
    url: streamingDashboard,
    success: function(result) {
        embedDashboard(result, 'streamingDashboardDiv');
    },
    beforeSend: () => {
        $('#streamingDashboardDiv').html('<center>' +
            '<p>Loading dashboard...</p>' +
            '<img src="img/squirrel_loading.gif" />' +
            '</center>');
    },
    complete: () => {
        // We have the ajax response
    }
});

$.ajax({
    url: theReport,
    success: function(result) {
        embedReport(result, 'theReportDiv');
    }
});

var dashboardDiv, reportDiv, accessToken, embedUrl;

function embedDashboard(result, divName) {
    accessToken = result.embed_token;
    embedUrl = result.embed_url;
    embedDashboardId = result.dashboard_id;

    // Get models. models contains enums that can be used.
    var models = window['powerbi-client'].models;

    // Embed configuration used to describe the what and how to embed.
    // This object is used when calling powerbi.embed.
    // This also includes settings and options such as filters.
    // You can find more information at https://github.com/Microsoft/PowerBI-JavaScript/wiki/Embed-Configuration-Details.
    var config = {
        type: 'dashboard',
        tokenType: models.TokenType.Embed,
        accessToken: accessToken,
        embedUrl: embedUrl,
        dashboardId: embedDashboardId,
        permissions: models.Permissions.All,
        settings: {
                filterPaneEnabled: true,
                navContentPaneEnabled: false
        },
        pageView: 'actualSize'
    };

    // Get a reference to the embedded HTML element
    dashboardDiv = $('#' + divName)[0];

    // Embed element and display it within the div container.
    dashboard = powerbi.embed(dashboardDiv, config);

    // Wait for element to be fully rendered
    // https://github.com/Microsoft/PowerBI-JavaScript/wiki/Handling-Events
    dashboard.on('loaded', function(event) {
        // Set event handlers
        // $('#Mexico').click(function() {
        //     tile.setFilters([makeLocationFilter('Mexico')])
        //         .then(function (result) {
        //             console.log('Location filter set to Mexico');
        //         })
        //         .catch(function (errors) {
        //             console.error(errors);
        //         });
        // });
        
        // Be verbose about PowerBI events
        dashboard.off('dataSelected');
        dashboard.off('filtersApplied');
        dashboard.on('dataSelected', event => {
            var data = event.detail;
            console.log('[PowerBI dataSelected event]');
            console.log(data);
        });
    });
}

function embedReport(result, divName) {
    accessToken = result.embed_token;
    embedUrl = result.embed_url;
    embedReportId = result.report_id;

    // Get models. models contains enums that can be used.
    var models = window['powerbi-client'].models;

    // Embed configuration used to describe the what and how to embed.
    // This object is used when calling powerbi.embed.
    // This also includes settings and options such as filters.
    // You can find more information at https://github.com/Microsoft/PowerBI-JavaScript/wiki/Embed-Configuration-Details.
    var config = {
        type: 'report',
        tokenType: models.TokenType.Embed,
        accessToken: accessToken,
        embedUrl: embedUrl,
        reportId: embedReportId,
        permissions: models.Permissions.All,
        settings: {
                filterPaneEnabled: false,
                navContentPaneEnabled: true
        },
        pageView: 'fitWidth'
    };

    // Get a reference to the embedded HTML element
    reportDiv = $('#' + divName)[0];

    // Embed element and display it within the div container.
    report = powerbi.embed(reportDiv, config);

    // Wait for element to be fully rendered
    // https://github.com/Microsoft/PowerBI-JavaScript/wiki/Handling-Events
    report.on('loaded', function(event) {
        // Set event handlers
        // $('#Mexico').click(function() {
        //     tile.setFilters([makeLocationFilter('Mexico')])
        //         .then(function (result) {
        //             console.log('Location filter set to Mexico');
        //         })
        //         .catch(function (errors) {
        //             console.error(errors);
        //         });
        // });
        
        // Be verbose about PowerBI events
        report.off('dataSelected', event => {
            $('#canvasWrapper > div').css('border', 'none');
        });
        report.off('filtersApplied');
        report.on('dataSelected', event => {
            $('#canvasWrapper > canvas').css('border', '0');
            var data = event.detail;
            console.log('[PowerBI dataSelected event]');
            console.log(data);
            console.log("session_id from slicer: " + data.dataPoints[0].identity[0].equals);
            console.log("Attempting to highlight matching canvas...");
            $('#' + data.dataPoints[0].identity[0].equals).css('border', '3px solid red');
        });
    });
}

// Enables console.log()
let DEBUG = true;

if (!DEBUG) {
    console = console || {};
    console.log = function(){};
}

let sessionsUrl = '/api/sessions';

function getJeffSessions() {
    $.getJSON(sessionsUrl, function(data) {
        paint(data);
        //console.log('-'.repeat(30));
    });
}

function resizeWithAspect(srcWidth, srcHeight, maxWidth, maxHeight) {
    var ratio = Math.min(maxWidth / srcWidth, maxHeight / srcHeight);
    return { 
        width: srcWidth * ratio,
        height: srcHeight * ratio 
    };
}

function paint(data) {
    $('#sessionCount').text(data.sessions.length);
    data.sessions.forEach(session => {
        let sessionCanvas = $('#' + session)[0];
        if (!sessionCanvas) {
            $('#canvasWrapper').prepend(`<canvas id="${session}" class="camera" style="background: #ddd" width="200"></canvas>`);
            // Handle click on thumbnail event
            $('#' + session).click((event) => {
                console.log(`Set filter to session ${session}`);
            });
        }
        let canvas = $('#' + session)[0];
        let context = canvas.getContext('2d');
        let image = new Image();
        // Backend response must include 'Cache-Control: no-cache',
        // else Chrome (who's testing other browsers anyway?)
        // redraws last cached image
        image.src = `/api/session-jpeg/${session}`;
        image.onload = () => {
            // Paint JPEG on canvas
            let resized = resizeWithAspect(image.width, image.height, 200, 150);
            canvas.height = image.height;
            context.drawImage(image, 0, 0, resized.width, resized.height);
            // Paint session ID on canvas
            context.fillStyle = 'rgba(0, 0, 0, 0.7)';
            context.fillRect(0, 0, (session.length % 2) ? (session.length * 8 + 4) : (session.length * 7 + 14), 16);
            context.fillStyle = "white";
            context.font = '12px "Segoe UI", Helvetica, sans-serif';
            context.fillText(session, 10, 12);
        }
        //console.log(`Got Session ID: ${session}`);
    });
}

getJeffSessions();
setInterval(() => {
    getJeffSessions();
}, 5000);