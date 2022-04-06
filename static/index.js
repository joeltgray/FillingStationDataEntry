// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see the error "The Geolocation service
// failed.", it means you probably did not give permission for the browser to
// locate you.
let map, pos;

function initMap() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        }
      })
      map = new google.maps.Map(document.getElementById("map"), {
        center: pos,
        zoom: 10,
      });
  } else {
        map = new google.maps.Map(document.getElementById("map"), {
          center: { lat: 54.607868, lng: -5.926437 },
          zoom: 6,
          }
        )
      }

}