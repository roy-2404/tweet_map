var map, pointarray, heatmap, respondToMapClick;
var centerofworld = {lat: 0, lng: 0};

function centerMap(map) {
  var centerControlDiv = document.getElementById('center-button');
  var controlUI = document.getElementById('center-ui');
  controlUI.addEventListener('click', function() {
    map.setCenter(centerofworld);
    map.setZoom(2);
  });
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(centerControlDiv);
}

function setupSelectPoint(map) {
  var selectPointDiv = document.getElementById('selectpoint-button');
  var controlUI = document.getElementById('selectpoint-ui');
  controlUI.addEventListener('click', function() {
    respondToMapClick = true;
    alert("Select a point on the map");
  });
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(selectPointDiv);
}

function setResetPosition(map) {
  var resetPositionDiv = document.getElementById('reset-button');
  var controlUI = document.getElementById('reset-ui');
  controlUI.addEventListener('click', function() {
    response = $('#map').data('tweet');
    renderHeatmap(response);
  });
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(resetPositionDiv);
}

function locationSearch(loc) {
  $.getJSON("location.json/" + loc)
    .done(function(data) {
      response = data;
      var tweets = response.tweets;
      if (tweets.length == 0) {
        alert("No tweets in the vicinity");
      }
      renderHeatmap(response);
    })
    .fail(function(jqxhr, textStatus, error) {
      alert("No tweets in the vicinity");
      renderHeatmap(null);
    });
}

function keywordSearch(key) {
  if (key.startsWith('Please')) {
    response = $('#map').data('tweet');
    renderHeatmap(response);
    return;
  }
  $.getJSON("keyword.json/" + key)
    .done(function(data) {
      response = data;
      var tweets = response.tweets;
      if (tweets.length == 0) {
        alert("No tweets matched the selected keyword");
      }
      renderHeatmap(response);
    })
    .fail(function(jqxhr, textStatus, error) {
      alert("No tweets matched the selected keyword");
      renderHeatmap(null);
    });
};

function main() {
  // Map center
  var mapCenter = new google.maps.LatLng(0, 0);

  // Map options
  var mapOptions = {
    zoom: 2,
    center: mapCenter,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }

  // Render basemap
  map = new google.maps.Map(document.getElementById("map"), mapOptions);
  response = $('#map').data('tweet');
  renderHeatmap(response);
  centerMap(map);
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(document.getElementById('reset-button'));
  setupSelectPoint(map);
  // Add click listener for geo-location
  google.maps.event.addListener(map, 'click', function (e) {
    if (respondToMapClick) {
      var locJSON = "{";
      locJSON += "\"dist\":" + "\"100mi\",";
      locJSON += "\"lat\":" + e.latLng.lat() + ",";
      locJSON += "\"lon\":" + e.latLng.lng();
      locJSON += "}";
      locationSearch(locJSON);      
    }
    respondToMapClick = false;
  });

  setResetPosition(map);

  $( ".datepicker" ).change(function() {
    keywordSearch($( ".datepicker option:selected" ).text());
  });
}

function renderHeatmap(response) {
  if (typeof heatmap !== "undefined" && heatmap !== null) {
    heatmap.setMap(null);
  }

  var data = [];
  // Transform data format
  var tweets = response.tweets;
  for (i in tweets) {
    data.push(new google.maps.LatLng(parseFloat(tweets[i].lat), parseFloat(tweets[i].lon)));
  }

  var pointArray = new google.maps.MVCArray(data);

  // Create heatmap
  heatmap = new google.maps.visualization.HeatmapLayer({
    data: pointArray
  });
  heatmap.set('radius', heatmap.get('radius') ? null : 15);
  heatmap.set('opacity', heatmap.get('opacity') ? null : .75);
  heatmap.setMap(map);
}

window.onload = main;

// var map, pointarray, heatmap;
// var centerofworld = {lat: 0, lng: 0};


// function centerMap(map) {
//   var centerControlDiv = document.getElementById('center-button');
//   var controlUI = document.getElementById('center-ui');
//   controlUI.addEventListener('click', function() {
//     map.setCenter(centerofworld);
//     map.setZoom(2);
//   });
//   map.controls[google.maps.ControlPosition.TOP_CENTER].push(centerControlDiv);
// }

// function keywordSearch(key) {
//   if (key.startsWith('Please')) {
//     response = $('#map').data('tweet');
//     renderHeatmap(response);
//     return;
//   }
//   $.getJSON("keyword.json/" + key)
//     .done(function(data) {
//       response = data;
//       var tweets = response.tweets;
//       if (tweets.length == 0) {
//         alert("No tweets matched the selected keyword");
//       }
//       renderHeatmap(response);
//     })
//     .fail(function(jqxhr, textStatus, error) {
//       alert("No tweets matched the selected keyword");
//       renderHeatmap(null);
//     });
// };

// function main() {
//   // Map center
//   var mapCenter = new google.maps.LatLng(0, 0);

//   // Map options
//   var mapOptions = {
//     zoom: 2,
//     center: mapCenter,
//     mapTypeId: google.maps.MapTypeId.ROADMAP
//   }

//   // Render basemap
//   map = new google.maps.Map(document.getElementById("map"), mapOptions);
//   response = $('#map').data('tweet');
//   renderHeatmap(response);
//   centerMap(map);

//   $( ".datepicker" ).change(function() {
//     keywordSearch($( ".datepicker option:selected" ).text());
//   });
// }

// function renderHeatmap(response) {
//   if (typeof heatmap !== "undefined" && heatmap !== null) {
//     heatmap.setMap(null);
//   }

//   var data = [];
//   // Transform data format
//   var tweets = response.tweets;
//   for (i in tweets) {
//     data.push(new google.maps.LatLng(parseFloat(tweets[i].lat), parseFloat(tweets[i].lon)));
//   }

//   var pointArray = new google.maps.MVCArray(data);

//   // Create heatmap
//   heatmap = new google.maps.visualization.HeatmapLayer({
//     data: pointArray
//   });
//   heatmap.set('radius', heatmap.get('radius') ? null : 15);
//   heatmap.set('opacity', heatmap.get('opacity') ? null : .75);
//   heatmap.setMap(map);
// }

// window.onload = main;