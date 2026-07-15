import streamlit as st
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="GeoLocate", page_icon="🌍", layout="centered")

st.title("🌍 GeoLocate")
st.write("Type a city, country, or landmark and explore its location and local time.")

query = st.text_input("Location", placeholder="e.g. Paris, France")
find_clicked = st.button("Find Location")

if find_clicked:
    if not query.strip():
        st.session_state["error"] = "Try a city, country, or landmark."
        st.session_state.pop("result", None)
    else:
        geolocator = Nominatim(user_agent="geo_app")
        name = geolocator.geocode(query)

        if not name:
            st.session_state["error"] = "Location not found. Try a different search term."
            st.session_state.pop("result", None)
        else:
            latitude = name.latitude
            longitude = name.longitude

            tf = TimezoneFinder()
            timezone_name = tf.timezone_at(lng=longitude, lat=latitude)

            result = {
                "address": name.address,
                "label": name.address.split(",")[0],
                "lat": latitude,
                "lon": longitude,
                "timezone_name": timezone_name,
            }

            if timezone_name:
                location_tz = pytz.timezone(timezone_name)
                current_time = datetime.now(location_tz)
                current_hour = int(current_time.strftime('%H'))
                result["local_time"] = current_time.strftime('%H:%M %Z')
                result["message"] = (
                    "☀️ It is currently daytime there"
                    if 6 <= current_hour <= 18
                    else "🌙 It is currently nighttime there"
                )

            st.session_state["result"] = result
            st.session_state.pop("error", None)

# Show any error
if st.session_state.get("error"):
    st.warning(st.session_state["error"])

# Render info + map from session_state so it survives map-triggered reruns
result = st.session_state.get("result")
if result:
    st.success(f"**Address:** {result['address']}")
    if result.get("timezone_name"):
        st.write(f"**Local Time:** {result['local_time']}")
        st.write(result["message"])
    else:
        st.error("Timezone not found for these coordinates.")
    st.write("**Coordinates:**")
    st.write(f"Latitude: {result['lat']}")
    st.write(f"Longitude: {result['lon']}")

    m = folium.Map(location=[result["lat"], result["lon"]], zoom_start=17)
    folium.Marker(
        location=[result["lat"], result["lon"]],
        popup=result["label"],
        tooltip=result["label"],
        icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
    ).add_to(m)
    st_folium(m, width=800, height=600, key="map")