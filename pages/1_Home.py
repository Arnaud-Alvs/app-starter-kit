import streamlit as st
import random
from PIL import Image
import os

# Page configuration must be the FIRST Streamlit command
st.set_page_config(
    page_title="WasteWise - Home",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("♻️ WasteWise - Your smart recycling assistant")
st.markdown("### Easily find where to dispose of your waste and contribute to a cleaner environment")

# Hero image (if available)
try:
    # If you have an image file, uncomment and use this
    # hero_image = Image.open("assets/recycling_hero.jpg")
    # st.image(hero_image, use_column_width=True)
    
    # Alternatively, use a placeholder
    st.image("https://via.placeholder.com/1200x400?text=WasteWise+-+Sustainable+Waste+Management", 
             caption="Sustainable waste management for a cleaner environment")
except Exception as e:
    st.warning("Hero image could not be loaded.")

# Feature showcases with icons and descriptions
st.markdown("## 🧐 What can WasteWise do for you?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚮 Find Collection Points")
    st.markdown("""
    Simply tell us what waste you want to dispose of and your address in St. Gallen.
    We'll find the nearest collection points and upcoming collection dates for you.
    """)
    st.page_link("2_Find_Collection_Points.py", label="Find Disposal Options", icon="🔍")
    
with col2:
    st.markdown("### 🔍 Identify Your Waste")
    st.markdown("""
    Not sure what type of waste you have? Upload a photo or describe it,
    and our AI will help you identify it and provide proper disposal instructions.
    """)
    st.page_link("3_Identify_Waste.py", label="Identify Your Waste", icon="📸")

# Environmental impact statistics
st.markdown("## Environmental Impact")

impact_col1, impact_col2, impact_col3 = st.columns(3)

with impact_col1:
    st.metric(label="Waste Correctly Sorted", value="12,543 kg", delta="1,243 kg this month")

with impact_col2:
    st.metric(label="CO₂ Emissions Saved", value="2,432 kg", delta="347 kg this month")

with impact_col3:
    st.metric(label="Active Users", value="853", delta="57 new")

# Tips of the day
st.markdown("---")
st.subheader("💡 Tip of the Day")
tips_of_the_day = [
    "Recycling one aluminum can saves enough energy to run a TV for three hours.",
    "Paper can be recycled up to 7 times before the fibers become too short.",
    "Glass is 100% recyclable and can be recycled infinitely without losing its quality!",
    "A mobile phone contains more than 70 different materials, many of which are recyclable.",
    "Batteries contain toxic heavy metals, never throw them away with household waste.",
    "Consider putting a 'No Junk Mail' sticker on your mailbox to reduce paper waste.",
    "Composting can reduce the volume of your household waste by up to 30%.",
    "Remember to break down cardboard packaging before disposing of it to save space.",
    "LED bulbs are less harmful to the environment and last longer."
]
st.info(random.choice(tips_of_the_day))

# Set up sidebar
with st.sidebar:
    st.title("WasteWise")
    st.markdown("Your smart recycling assistant")
    
    # Navigation
    st.markdown("## Navigation")
    st.page_link("1_Home.py", label="Home", icon="🏠")
    st.page_link("2_Find_Collection_Points.py", label="Find Collection Points", icon="🚮")
    st.page_link("3_Identify_Waste.py", label="Identify Waste", icon="🔍")
    st.page_link("4_About.py", label="About", icon="ℹ️")
    
    # Useful links
    st.markdown("## Useful Links")
    st.markdown("[Complete recycling guide](https://www.stadt.sg.ch/home/umwelt-energie/entsorgung.html)")
    st.markdown("[Reducing waste in everyday life](https://www.bafu.admin.ch/bafu/en/home/topics/waste/guide-to-waste-a-z/avoiding-waste.html)")
    st.markdown("[Waste legislation in Switzerland](https://www.bafu.admin.ch/bafu/en/home/topics/waste/legal-basis.html)")
    st.markdown("[Official St. Gallen city website](https://www.stadt.sg.ch/)")

# Footer
st.markdown("---")
st.markdown("© 2025 WasteWise - University Project | [Contact](mailto:contact@wastewise.example.com) | [Legal notice](https://example.com)")