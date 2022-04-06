// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see the error "The Geolocation service
// failed.", it means you probably did not give permission for the browser to
// locate you.
let map;
let lat;
let lng;
let pos;


function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 52.607868, lng: -7.926437 },
    //center: { lat: 54.607868, lng: -5.926437 },
    zoom: 12,
  })

  locate();
};

function locate(){
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        lat = position.coords.latitude;
        lng = position.coords.longitude;
        pos = {lat: lat, lng: lng}
        console.log(lat, lng)
        map.panTo(pos);
      })
      
  } else {
    console.log("couldnt locate person")
    }
};


