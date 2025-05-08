import streamlit as st
import random
from PIL import Image
import os

# Page configuration - this is needed on each page
st.set_page_config(
    page_title="WasteWise - Home",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("♻️ Welcome to WasteWise")
st.markdown("### Your smart recycling assistant in St. Gallen")

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

# Mission statement
st.markdown("""
## Our Mission

WasteWise aims to simplify waste disposal and recycling in St. Gallen by providing:

- **Easy waste identification** using AI technology
- **Location-based collection information** for all types of waste
- **Collection schedules** to never miss a pickup
- **Environmental education** to promote sustainable practices
""")

# Featured modules with cards
st.markdown("## Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🚮 Find Collection Points
    
    Find the nearest collection points for any type of waste in St. Gallen. Get directions and information on opening hours.
    """)
    st.page_link("pages/2_Find_Collection_Points.py", label="Find nearest points", icon="🚮")

with col2:
    st.markdown("""
    ### 🔍 Identify Waste
    
    Not sure what type of waste you have? Our AI can help identify it and provide proper disposal instructions.
    """)
    st.page_link("pages/3_Identify_Waste.py", label="Identify your waste", icon="🔍")

with col3:
    st.markdown("""
    ### ℹ️ About WasteWise
    
    Learn more about our project, the technology behind it, and the team that made it possible.
    """)
    st.page_link("pages/4_About.py", label="About us", icon="ℹ️")

# Environmental impact statistics
st.markdown("## Environmental Impact")

impact_col1, impact_col2, impact_col3 = st.columns(3)

with impact_col1:
    st.metric(label="Waste Correctly Sorted", value="12,543 kg", delta="1,243 kg this month")

with impact_col2:
    st.metric(label="CO₂ Emissions Saved", value="2,432 kg", delta="347 kg this month")

with impact_col3:
    st.metric(label="Active Users", value="853", delta="57 new")

# Recent news or updates
st.markdown("## Latest Updates")

# Create cards for news
news_container = st.container()
with news_container:
    news_col1, news_col2 = st.columns(2)
    
    with news_col1:
        st.markdown("### 🆕 New Collection Points Added")
        st.markdown("""
        We've added 15 new collection points for electronic waste throughout the city.
        Check the map for locations near you!
        """)
        st.date_input("Posted on", value=st.session_state.get("today", None), disabled=True, label_visibility="collapsed")
    
    with news_col2:
        st.markdown("### 📊 Recycling Statistics Released")
        st.markdown("""
        St. Gallen has achieved a 67% recycling rate in 2024, up from 62% last year.
        Learn how you can help reach the 75% target by 2027.
        """)
        st.date_input("Posted on", value=st.session_state.get("today", None), disabled=True, label_visibility="collapsed")

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
