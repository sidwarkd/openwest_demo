'use strict';

var buttonPresses = 0;
var rfidButtonScans = 0;
var rfidCardScans = 0;
var pointsAdded = 0;

function SendJSONRequest(url, data, success, error){
  $.ajax(url, {
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(data),
    error: error,
    success: success

  });
}

$(document).ready(function(){

  // ===================================
  // WEB SOCKET
  // ===================================
  var ws = new WebSocket("ws://10.0.0.17:8080/ws");
  //var ws = new WebSocket("ws://0.0.0.0:8080/ws");
  // ws.onopen = function() {
  //     ws.send("Hello, world");
  // };
  ws.onmessage = function (evt) {
      //console.log(evt.data);
      var d = eval("(" + evt.data + ")");

      // What kind of message did we receive
      // TEMP SENSOR
      if(d.hasOwnProperty("temp")){
        $("#currentTemp").html(d.temp);

        var chart = $("#tempGraph").highcharts();
        var series = chart.series[0];
        var x = (new Date()).getTime(), // current time
            y = d.temp;
        if(pointsAdded < 10)
          series.addPoint([x, y], true, false);
        else
          series.addPoint([x, y], true, true);

        pointsAdded++;
      }

      // BUTTON
      if(d.hasOwnProperty("button")){
        buttonPresses += 1;
        $("#pressCount").html(buttonPresses);
      }

      // SWITCH
      if(d.hasOwnProperty("switch")){
        $("#switchState").prop("checked", d.switch);
      }

      // RFID
      if(d.hasOwnProperty("rfid")){
        console.log(d.rfid);
        if(d.rfid == "71002539117C"){
          rfidCardScans += 1;
          $("#tagRFID").html(rfidCardScans);
        }

        if(d.rfid == "730061CADC04"){
          rfidButtonScans += 1;
          $("#buttonRFID").html(rfidButtonScans);
        }

        $("#rfidMessage").html("Detected Tag ID: " + d.rfid);
        $("#rfidMessage").slideDown(function() {
          setTimeout(function() {
              $("#rfidMessage").slideUp();
          }, 2000);
      });
      }

  };

  // ===================================
  // SPI ITEMS
  // ===================================
  $("#spi-display-form").submit(function(event){
    event.preventDefault();

    SendJSONRequest("/hw", 
      {device: "display", text: $("#textInput").val()}, 
      function(data, status, xhr){}, 
      function(xhr, status, errorThrown){});

  });


  // ===================================
  // GPIO PANEL ITEMS
  // ===================================

  $("#led-switch").on('click', function(event){

    SendJSONRequest("/hw", 
      {device: "led", state: $(this).is(":checked")}, 
      function(data, status, xhr){}, 
      function(xhr, status, errorThrown){});
  });

  $("#relay-1").on('click', function(event){
    // console.log("Relay 1 On: " + $(this).find("input").first().is(":checked"));

    SendJSONRequest("/hw", 
      {device: "relay", id: 1, state: $(this).find("input").first().is(":checked")},  
      function(data, status, xhr){}, 
      function(xhr, status, errorThrown){});
  });

  $("#relay-2").on('click', function(event){
    // console.log("Relay 2 On: " + $(this).find("input").first().is(":checked"));

    SendJSONRequest("/hw", 
      {device: "relay", id: 2, state: $(this).find("input").first().is(":checked")},  
      function(data, status, xhr){}, 
      function(xhr, status, errorThrown){});
  });

  $("#relay-3").on('click', function(event){
    // console.log("Relay 3 On: " + $(this).find("input").first().is(":checked"));

    SendJSONRequest("/hw", 
      {device: "relay", id: 3, state: $(this).find("input").first().is(":checked")}, 
      function(data, status, xhr){}, 
      function(xhr, status, errorThrown){});
  });

  Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    var chart;
    $('#tempGraph').highcharts({
        chart: {
            type: 'spline',
            animation: Highcharts.svg, // don't animate in old IE
            marginRight: 10,
        },
        title: {
            text: 'History'
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150
        },
        yAxis: {
            title: {
                text: '°F'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+
                    Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) +'<br/>'+
                    Highcharts.numberFormat(this.y, 2);
            }
        },
        legend: {
            enabled: false
        },
        exporting: {
            enabled: false
        },
        series: [{
            name: 'Temperature',
            data: [null],
            pointStart: (new Date().getTime())
        }]
    });

  // Don't need this since we can just periodically send this info from the web socket
  // setInterval(function(){
  //   SendJSONRequest("/hw", 
  //     {device: "sensors"}, 
  //     function(data, status, xhr){}, 
  //     function(xhr, status, errorThrown){});
  // }, 5000);

});