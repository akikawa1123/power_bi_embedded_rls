// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

// Global variables
var reportContainer;
var models;
var currentReport;

$(function () {
    reportContainer = $("#report-container").get(0);
    models = window["powerbi-client"].models;

    // Initialize iframe for embedding report
    powerbi.bootstrap(reportContainer, { type: "report" });

    // Load customers for RLS dropdown
    loadCustomers();

    // Event handlers
    $("#customer-select").change(function() {
        var customerId = $(this).val();
        $("#load-report-rls").prop("disabled", !customerId);
    });

    $("#load-report-rls").click(function() {
        var customerId = $("#customer-select").val();
        if (customerId) {
            loadReportWithRLS(customerId);
        }
    });

    $("#load-report-default").click(function() {
        loadDefaultReport();
    });
});

function loadCustomers() {
    $.ajax({
        type: "GET",
        url: "/getcustomers",
        dataType: "json",
        success: function (data) {
            var customerSelect = $("#customer-select");
            data.customers.forEach(function(customer) {
                customerSelect.append(
                    $("<option>").val(customer.id).text(customer.name)
                );
            });
        },
        error: function (err) {
            console.error("Failed to load customers:", err);
        }
    });
}

function loadDefaultReport() {
    // データセットにRLSが定義されている場合、identityなしのトークン生成はAPIに拒否される。
    // そのため、全データを表示する customer_c の identity を使って RLS エンドポイントを呼び出す。
    loadReportWithRLS('customer_c');
    $("#customer-select").val('customer_c');
    $("#load-report-rls").prop("disabled", false);
}

function loadReportWithRLS(customerId) {
    var reportLoadConfig = {
        type: "report",
        tokenType: models.TokenType.Embed,
    };

    $.ajax({
        type: "POST",
        url: "/getembedinfo_rls",
        contentType: "application/json",
        data: JSON.stringify({ customerId: customerId }),
        dataType: "json",
        success: function (data) {
            embedData = $.parseJSON(JSON.stringify(data));
            reportLoadConfig.accessToken = embedData.accessToken;
            reportLoadConfig.embedUrl = embedData.reportConfig[0].embedUrl;
            tokenExpiry = embedData.tokenExpiry;

            // Reset any existing embed before creating a fresh one with the RLS token
            powerbi.reset(reportContainer);

            // Embed Power BI report with RLS
            currentReport = powerbi.embed(reportContainer, reportLoadConfig);

            // Display customer info
            if (embedData.customerInfo) {
                $("#display-customer-id").text(embedData.customerInfo.customerId);
                $("#display-customer-name").text(embedData.customerInfo.customerName);
                $("#display-username").text(embedData.customerInfo.username);
                $("#display-roles").text(embedData.customerInfo.roles.join(", "));
                $("#customer-info").show();
            }

            setupReportEventHandlers(currentReport);
        },
        error: function (err) {
            showError(err);
        }
    });
}

function setupReportEventHandlers(report) {
    // Triggers when a report schema is successfully loaded
    report.on("loaded", function () {
        console.log("Report load successful");
    });

    // Triggers when a report is successfully embedded in UI
    report.on("rendered", function () {
        console.log("Report render successful");
    });

    // Clear any other error handler event
    report.off("error");

    // Handle errors that occur during embedding
    report.on("error", function (event) {
        var errorMsg = event.detail;
        console.error(errorMsg);
        return;
    });
}

function showError(err) {
    // Show error container
    var errorContainer = $(".error-container");
    $(".embed-container").hide();
    errorContainer.show();

    // Format error message
    var errMessageHtml = "<strong> Error Details: </strong> <br/>" + $.parseJSON(err.responseText)["errorMsg"];
    errMessageHtml = errMessageHtml.split("\n").join("<br/>");

    // Show error message on UI
    errorContainer.html(errMessageHtml);
}